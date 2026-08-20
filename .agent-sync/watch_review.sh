#!/usr/bin/env bash
#
# Watcher do implementador (opencode).
#
# Deteta quando o Claude escreve uma nova entrada no CLAUDE_REVIEW.md
# (o ficheiro de handoff que o implementador lê) e regista a deteção em
# WATCHER_LOG.md, com a entrada mais recente para contexto.
#
# IMPORTANTE: o watcher apenas DETETA e REGISTA. A ação (ler, corrigir,
# implementar, commit+push) continua a ser do implementador, por sessão —
# quando ele for invocado, lê o topo do CLAUDE_REVIEW.md e o WATCHER_LOG.md.
#
# Utilização:
#   iniciar :  nohup .agent-sync/watch_review.sh >/dev/null 2>&1 &
#   estado  :  cat .agent-sync/WATCHER_LOG.md   (e .agent-sync/.watch.pid)
#   parar   :  kill "$(cat .agent-sync/.watch.pid)"
#

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW="$SCRIPT_DIR/CLAUDE_REVIEW.md"
STATE="$SCRIPT_DIR/.watch_state"
LOG="$SCRIPT_DIR/WATCHER_LOG.md"
PIDFILE="$SCRIPT_DIR/.watch.pid"
INTERVAL="${WATCH_INTERVAL:-30}"

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

# Baseline: ao primeiro arranque regista o estado atual sem reportar "mudança"
if [ ! -f "$STATE" ] || [ ! -s "$STATE" ]; then
  if [ -f "$REVIEW" ]; then
    hash_of "$REVIEW" > "$STATE"
    log "Watcher iniciado (pid $(cat "$PIDFILE")). Baseline registado — a monitorizar a cada ${INTERVAL}s. Sem mudanças a reportar."
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
    log "  → Implementador: ler o TOPO de .agent-sync/CLAUDE_REVIEW.md e agir (AÇÃO NECESSÁRIA / TRABALHO PEDIDO)."
  fi
done
