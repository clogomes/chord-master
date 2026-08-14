# Estado da Sessão — Pausa por Quota do Gemini

**Última atualização**: 2026-08-14, ~20:00 (UTC+1)
**Motivo da pausa**: o Gemini atingiu o limite de quota da API a meio da
sessão. Este ficheiro regista o estado completo do projeto para retomares
sem perder contexto, seja nesta conversa ou noutra.

---

## 1. Estado do código: tudo aprovado, working tree limpa

- **Testes**: 134/134 a passar (3 saltados por falta de `scipy`/`PyMuPDF`
  neste ambiente local — comportamento esperado e correto, ver secção 4).
- **Git**: tudo commitado e sincronizado com `origin/main`
  (`github.com/clogomes/chord-master`, repositório público).
- **Último commit**: `5e46101` — "Approve OMR pixel-to-note fix".
- **Não há nenhuma AÇÃO NECESSÁRIA pendente** neste momento — o único item
  bloqueante que existia (bug de mapeamento pixel→nota no OMR, Fases 18-19)
  foi corrigido e aprovado nesta sessão (ver secção 3).

## 2. Fases implementadas até agora (1 a 19, todas concluídas e aprovadas)

| # | Fase | O que é |
|---|------|---------|
| 1-2 | Dedilhação de piano + Repertório | `core/fingering.py`, `core/songs.py` (16 músicas) |
| 3 | Estúdio "Tocar" | `gui/screens/practice_song.py` — teclado PC/MIDI, follow-along |
| 4 | Prática com instrumento real | `audio/pitch_listener.py` — microfone, deteção de afinação FFT+autocorrelação |
| 5 | Ditado de Solfejo Cantado | `QuestionType.SOLFEGE_SING` em `core/quiz_engine.py`, ligado ao microfone |
| 6 | Motor Adaptativo | `core/adaptive_engine.py` — deteção de pontos fracos, "Modo Adaptativo" nos ecrãs de prática |
| 7 | Gráficos de Progresso | `stats_screen.py` — tendência semanal, comparação por categoria, calendário estilo GitHub |
| 8 | Importador MIDI | `core/midi_importer.py` — parser SMF puro Python |
| 9 | Notação Rítmica & Rampa de Tempo | compassos, barras de compasso, metrónomo em `practice_instrument.py` |
| 10 | Acompanhamento Rítmico Sintetizado | `audio/backing_tracks.py` — 5 estilos, bateria 100% sintetizada (Karplus-Strong não, é síntese aditiva+ruído) |
| 11 | Mais Escalas & Modos | `core/scales.py` — completou os 7 modos gregos + 4 exóticas (16 escalas no total) |
| 12 | Estúdio de Prática de Escalas | `gui/screens/practice_scales.py` |
| 13 | Scroll do rato + Piano 4 oitavas | `gui/scroll_utils.py` |
| 14 | Sons realistas (Karplus-Strong) | `audio/synthesizer.py` — viola com síntese física de corda dedilhada |
| 15 | Alternador PT/EN | `gui/i18n.py`, `core/i18n_helpers.py` |
| 16 | Mais dicas de técnica | `core/theory_content.py` expandido |
| 17 | Renderizador de Markdown | `gui/markdown_renderer.py` — corrige formatação em bruto no ecrã de teoria |
| 18-19 | Importação de Partituras (OMR leve) | `core/omr_importer.py`, `gui/screens/omr_review.py` — **corrigido nesta sessão** |

## 3. O que aconteceu no fim desta sessão (importante)

O Gemini tinha um bug real na Fase 18 (`map_pixel_to_note` em
`core/omr_importer.py` usava a linha de pauta errada como referência —
todas as notas importadas saíam sistematicamente uma 4ª abaixo do correto).
Já tinha **começado a corrigir isto** (alterações locais no ficheiro) quando
atingiu a quota da API, deixando o fix por commitar.

**Eu (Claude) verifiquei que a correção estava completa e correta** (testes
+ verificação numérica direta) **e commitei em nome do Gemini** (`bb9339a`)
para não se perder o trabalho, depois aprovei formalmente em
`.agent-sync/CLAUDE_REVIEW.md` (`5e46101`).

**Quando o Gemini retomar**: não precisa de refazer nada desta correção. Só
precisa de ler `.agent-sync/CLAUDE_REVIEW.md` (última entrada) para saber
que já está resolvido, e opcionalmente acrescentar uma entrada em
`GEMINI_STATUS.md` a reconhecer isto antes de avançar para trabalho novo.

## 4. Duas notas de qualidade registadas, não bloqueantes (ainda por resolver)

Estas não impedem nada de funcionar, mas ficaram por corrigir — vale a pena
lembrar o Gemini destas na próxima ronda de trabalho, se não houver nada
mais urgente:

1. **`core/i18n_helpers.py` importa de `gui/i18n.py`** — inverte a regra
   documentada de que `core/` deve ser independente da GUI. Correção
   sugerida: mover o estado de idioma para `core/i18n.py`.
2. **`audio/backing_tracks.py` tem o seu próprio relógio**, independente do
   `Metronome` já existente — risco de dessincronização se os dois
   estiverem ativos ao mesmo tempo (raro, mas possível). Também tem um
   pequeno busy-wait no `_run_loop`.

## 5. O protocolo de colaboração (já montado, funciona)

- **`CLAUDE.md`** e **`GEMINI.md`** na raiz — cada ferramenta lê o seu ao
  abrir o projeto, e aponta para `.agent-sync/PROTOCOL.md` para o protocolo
  completo.
- **`.agent-sync/GEMINI_STATUS.md`** — o Gemini regista cada fase concluída.
- **`.agent-sync/CLAUDE_REVIEW.md`** — eu registo o veredito de cada revisão
  (APROVADO / AÇÃO NECESSÁRIA / TRABALHO PEDIDO).
- Regra importante já documentada: usar `git add <ficheiros específicos>`
  em vez de `git add -A`, para não misturar commits de ambos sem querer
  (já aconteceu uma vez).
- O Gemini tem um cron próprio (Antigravity) a verificar `CLAUDE_REVIEW.md`
  periodicamente — o utilizador reduziu o intervalo para 2 minutos. Eu tinha
  um monitor em segundo plano a vigiar commits novos no GitHub a cada 30s,
  que **parei** no fim desta sessão (estava a consumir recursos sem sentido
  enquanto o Gemini está sem quota). **Para retomar, é preciso pedir-me
  explicitamente para voltar a ativar o monitor.**

## 6. Como retomar

1. Confirma que o Gemini já tem quota de novo.
2. Se quiseres que eu volte a vigiar automaticamente os commits dele,
   pede-me para reativar o monitor (já não está ativo).
3. Não há nada pendente para pedires ao Gemini imediatamente — o projeto
   está num estado limpo e aprovado. As próximas fases dependem do que
   quiseres pedir a seguir (ex: as duas notas de qualidade da secção 4, ou
   funcionalidades novas).
4. Este ficheiro (`RESUME_NOTES.md`) pode ser apagado depois de retomares
   — é só para continuidade entre sessões, não faz parte do protocolo
   permanente (esse continua a ser `PROTOCOL.md` + `GEMINI_STATUS.md` +
   `CLAUDE_REVIEW.md`).
