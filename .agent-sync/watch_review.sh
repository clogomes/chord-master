#!/usr/bin/env bash
#
# Watcher do implementador (opencode).
#
# Deteta quando o Claude escreve uma nova entrada no CLAUDE_REVIEW.md
# (o ficheiro de handoff que o implementador lê) e, além de registar a
# deteção em WATCHER_LOG.md, **INVOCAR o implementador** de forma
# não-interativa via:
#
#     opencode run --continue "<mensagem>"
#
# Assim o ciclo não fica parado à espera de alguém invocar o implementador
# à mão: quando o Claude publica um veredito, o implementador é desperto
# automaticamente para o ler e agir.
#
# ── IMPORTANTE: há um agente autónomo ligado ────────────────────────────────
# Este watcher passa a correr sem supervisão e a invocar o opencode. Por isso
# tem 7 travões de segurança (nenhum é opcional):
#
#   1. Interruptor de desligar — se existir .agent-sync/.watch_disabled, o
#      watcher deteta e regista mas NÃO invoca. Forma de parar sem matar o
#      processo nem editar código:  touch .agent-sync/.watch_disabled
#   2. Não invocar em paralelo — guarda o PID da invocação em curso; se ainda
#      estiver viva, regista e não lança outra.
#   3. Arrefecimento (cooldown) — mínimo de 60 s entre invocações.
#   4. Limite por hora — máx. 10 invocações/hora; se atingido, para até à
#      hora seguinte.
#   5. Timeout — mata a invocação se passar de ~30 min.
#   6. Registo completo — cada invocação escreve início, fim, duração e código
#      de saída em WATCHER_LOG.md.
#   7. Nunca invocar a partir do próprio commit — se a mudança no
#      CLAUDE_REVIEW.md foi feita pelo implementador (marcador
#      .watch_my_marker), não se auto-invoca. Elimina o ciclo infinito.
#
# O watcher NUNCA faz `git commit`/`push` — a decisão de commitar continua a
# ser do implementador, dentro da sessão. O gatilho é SÓ o CLAUDE_REVIEW.md.
#
# Utilização:
#   iniciar :  nohup .agent-sync/watch_review.sh >/dev/null 2>&1 &
#   estado  :  cat .agent-sync/WATCHER_LOG.md   (e .agent-sync/.watch.pid)
#   parar   :  kill "$(cat .agent-sync/.watch.pid)"
#   desligar invocações (sem parar o watcher):  touch .agent-sync/.watch_disabled
#   ligar de novo:                              rm    .agent-sync/.watch_disabled
#   marcar mudança como minha (evita auto-invocação):
#         .agent-sync/watch_review.sh --mark
#
# Variáveis de ambiente (opcional):
#   WATCH_INTERVAL      segundos entre verificações (default 30)
#   WATCH_COOLDOWN      cooldown mínimo entre invocações, em s (default 60)
#   WATCH_MAX_PER_HOUR  limite de invocações por hora (default 10)
#   WATCH_TIMEOUT       timeout da invocação, em s (default 1800 = 30 min)
#   OPENCODE_BIN        caminho do binário opencode (default: opencode)
#

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW="$SCRIPT_DIR/CLAUDE_REVIEW.md"
STATE="$SCRIPT_DIR/.watch_state"
LOG="$SCRIPT_DIR/WATCHER_LOG.md"
PIDFILE="$SCRIPT_DIR/.watch.pid"
INV_PIDFILE="$SCRIPT_DIR/.watch_invocation.pid"
DISABLED="$SCRIPT_DIR/.watch_disabled"
MARKER="$SCRIPT_DIR/.watch_my_marker"
COOLDOWN_FILE="$SCRIPT_DIR/.watch_last_invoke"
RATE_FILE="$SCRIPT_DIR/.watch_rate"

INTERVAL="${WATCH_INTERVAL:-30}"
COOLDOWN="${WATCH_COOLDOWN:-60}"
MAX_PER_HOUR="${WATCH_MAX_PER_HOUR:-10}"
INVOKE_TIMEOUT="${WATCH_TIMEOUT:-1800}"
OPENCODE_BIN="${OPENCODE_BIN:-opencode}"

INVOKE_OUT="$SCRIPT_DIR/.watch_invocation.out"

INVOKE_MSG='Nova entrada do Claude em .agent-sync/CLAUDE_REVIEW.md. Lê o TOPO do ficheiro e age conforme o veredito (AÇÃO NECESSÁRIA / TRABALHO PEDIDO / APROVADO com "avança para"). Segue o AGENTS.md.'

# ── Subcomando --mark: registar o estado atual como "meu" (travão 7) ─────────
# O implementador corre isto depois de commitar alterações ao CLAUDE_REVIEW.md,
# para o watcher não o auto-invocar em resposta à sua própria mudança.
if [ "${1:-}" = "--mark" ]; then
  if [ -f "$REVIEW" ]; then
    hash_of_tmp() { shasum -a 256 "$1" 2>/dev/null | awk '{print $1}'; }
    hash_of_tmp "$REVIEW" > "$MARKER"
    echo "Marcador atualizado: mudanças futuras idênticas a este estado serão tratadas como do implementador (sem auto-invocação)."
  else
    echo "ERRO: ficheiro alvo não existe: $REVIEW" >&2
    exit 1
  fi
  exit 0
fi

# Evitar dois watchers em simultâneo (se o anterior ainda estiver vivo)
if [ -f "$PIDFILE" ]; then
  oldpid="$(cat "$PIDFILE" 2>/dev/null || true)"
  if [ -n "$oldpid" ] && kill -0 "$oldpid" 2>/dev/null; then
    echo "Já existe um watcher a correr (pid $oldpid). A sair." >&2
    exit 0
  fi
fi
echo $$ > "$PIDFILE"

if [ ! -f "$LOG" ]; then
  printf '# Watcher — novas entradas do Claude em CLAUDE_REVIEW.md\n\n' > "$LOG"
fi

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG"
}

hash_of() { shasum -a 256 "$1" 2>/dev/null | awk '{print $1}'; }

# Entrada mais recente = primeiro cabeçalho '## ' do ficheiro
top_entry() { awk '/^## /{sub(/^##[[:space:]]*/, ""); print; exit}' "$REVIEW"; }

# ── Travão 7: a mudança é do implementador? ──────────────────────────────────
# Compara o hash atual com o marcador que o implementador regista quando
# commita alterações ao CLAUDE_REVIEW.md. Se forem iguais, foi ele → não
# auto-invocar.
is_my_change() {
  local cur="$1"
  [ -f "$MARKER" ] || return 1
  local mine
  mine="$(cat "$MARKER" 2>/dev/null || true)"
  [ -n "$mine" ] && [ "$cur" = "$mine" ]
}

# ── Travões 3 e 4: cooldown e limite por hora ────────────────────────────────
now_epoch() { date '+%s'; }

in_cooldown() {
  [ -f "$COOLDOWN_FILE" ] || return 1
  local last
  last="$(cat "$COOLDOWN_FILE" 2>/dev/null || true)"
  [ -n "$last" ] || return 1
  local now elapsed
  now="$(now_epoch)"; elapsed=$(( now - last ))
  [ "$elapsed" -lt "$COOLDOWN" ]
}

# Conta invocações iniciadas na última hora (uma linha por timestamp).
hourly_count() {
  [ -f "$RATE_FILE" ] || { echo 0; return; }
  local now cutoff
  now="$(now_epoch)"; cutoff=$(( now - 3600 ))
  local n=0 ts
  while IFS= read -r ts; do
    case "$ts" in (*[!0-9]*|'') continue;; esac
    if [ "$ts" -ge "$cutoff" ]; then n=$(( n + 1 )); fi
  done < "$RATE_FILE"
  echo "$n"
}

rate_limited() {
  local c
  c="$(hourly_count)"
  [ "$c" -ge "$MAX_PER_HOUR" ]
}

# ── Travão 2: já há uma invocação em curso? ──────────────────────────────────
invocation_running() {
  [ -f "$INV_PIDFILE" ] || return 1
  local pid
  pid="$(cat "$INV_PIDFILE" 2>/dev/null || true)"
  [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

# ── Invocação do implementador (com timeout — travão 5) ─────────────────────
# Corre `opencode run --continue` com timeout; regista início, fim, duração e
# código de saída (travão 6). O stdout/stderr da invocação vai para
# $INVOKE_OUT (não para o WATCHER_LOG.md, que só tem linhas estruturadas).
# Um trap garante que a linha de fecho é escrita mesmo em caso de interrupção.
do_invoke() {
  local cur="$1"

  # Guard defensivo: se o binário não existir, regista e não invoca.
  if ! command -v "$OPENCODE_BIN" >/dev/null 2>&1; then
    log "ERRO: binário '$OPENCODE_BIN' não encontrado no PATH — não invocado."
    return 1
  fi

  local start_ts start_epoch
  start_ts="$(date '+%Y-%m-%d %H:%M:%S')"; start_epoch="$(now_epoch)"

  log "INVOCAR implementador (início $start_ts) — entrada: $(top_entry || echo '<sem cabeçalho ##>')"

  # Regista o início para o limite por hora (travão 4) e o cooldown (travão 3).
  echo "$(now_epoch)" >> "$RATE_FILE"
  echo "$(now_epoch)" > "$COOLDOWN_FILE"

  # Trunca o ficheiro de saída da invocação (cada invocação começa limpo).
  : > "$INVOKE_OUT"

  # Lança a invocação em segundo plano; stdout/stderr vai para $INVOKE_OUT.
  "$OPENCODE_BIN" run --continue "$INVOKE_MSG" > "$INVOKE_OUT" 2>&1 &
  local inv_pid=$!
  echo "$inv_pid" > "$INV_PIDFILE"

  # Trap para garantir que a linha de fecho é escrita mesmo se o script
  # for interrompido (SIGTERM/SIGINT) durante a invocação.
  local _inv_start_epoch="$start_epoch"
  trap '
    local _rc=143
    if [ -f "'"$INV_PIDFILE"'" ]; then
      local _ep _ts _dur
      _ep="$(date +%s)"; _ts="$(date "+%Y-%m-%d %H:%M:%S")"
      _dur=$(( _ep - _inv_start_epoch ))
      printf "[%s] INVOCACAO terminou (fim %s, duração %ss, código de saída %s — interrompido)\n" "$_ts" "$_ts" "$_dur" "$_rc" >> "'"$LOG"'"
      rm -f "'"$INV_PIDFILE"'"
    fi
  ' TERM INT

  # Aguarda com timeout (travão 5).
  local waited=0 rc=0
  while kill -0 "$inv_pid" 2>/dev/null; do
    if [ "$waited" -ge "$INVOKE_TIMEOUT" ]; then
      log "TIMEOUT: invocação (pid $inv_pid) excedeu ${INVOKE_TIMEOUT}s — a terminar."
      kill "$inv_pid" 2>/dev/null || true
      wait "$inv_pid" 2>/dev/null || true
      rc=124
      break
    fi
    sleep 5
    waited=$(( waited + 5 ))
  done
  wait "$inv_pid" 2>/dev/null; rc=$?

  # Remove o trap agora que a invocação terminou normalmente.
  trap - TERM INT

  local end_epoch end_ts duration
  end_epoch="$(now_epoch)"; end_ts="$(date '+%Y-%m-%d %H:%M:%S')"
  duration=$(( end_epoch - start_epoch ))
  log "INVOCACAO terminou (fim $end_ts, duração ${duration}s, código de saída $rc)"
  rm -f "$INV_PIDFILE"
}

# Baseline: ao primeiro arranque regista o estado atual sem reportar "mudança"
if [ ! -f "$STATE" ] || [ ! -s "$STATE" ]; then
  if [ -f "$REVIEW" ]; then
    hash_of "$REVIEW" > "$STATE"
    log "Watcher iniciado (pid $(cat "$PIDFILE")). Baseline registado — a monitorizar a cada ${INTERVAL}s. Invocação ativa (cooldown ${COOLDOWN}s, máx. ${MAX_PER_HOUR}/h, timeout ${INVOKE_TIMEOUT}s)."
  else
    log "ERRO: ficheiro alvo não existe: $REVIEW"
  fi
fi

while true; do
  sleep "$INTERVAL"
  [ -f "$REVIEW" ] || continue
  cur="$(hash_of "$REVIEW")"
  prev="$(cat "$STATE" 2>/dev/null || true)"
  if [ -n "$cur" ] && [ "$cur" != "$prev" ]; then
    echo "$cur" > "$STATE"
    log "MUDANÇA DETETADA — entrada mais recente: $(top_entry || echo '<sem cabeçalho ##>')"

    # Travão 7: não auto-invocar se a mudança for do implementador.
    if is_my_change "$cur"; then
      log "  → Mudança do implementador (marcador) — a saltar a invocação."
      continue
    fi

    # Travão 1: interruptor de desligar.
    if [ -f "$DISABLED" ]; then
      log "  → .watch_disabled presente — deteção registada mas SEM invocação."
      continue
    fi

    # Travão 2: não invocar em paralelo.
    if invocation_running; then
      log "  → Invocação anterior ainda a correr — a saltar."
      continue
    fi

    # Travão 3: cooldown.
    if in_cooldown; then
      log "  → Em cooldown (< ${COOLDOWN}s desde a última invocação) — a saltar."
      continue
    fi

    # Travão 4: limite por hora.
    if rate_limited; then
      log "  → Limite de ${MAX_PER_HOUR} invocações/hora atingido — a saltar até à hora seguinte."
      continue
    fi

    do_invoke "$cur"
  fi
done
