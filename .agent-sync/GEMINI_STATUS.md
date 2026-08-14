# Estado do Gemini — Protocolo de Handoff

Este ficheiro é escrito pelo **Gemini**. No fim de cada fase de trabalho (depois de
fazeres commit + push), acrescenta uma nova entrada no TOPO da secção "Histórico"
below, com este formato:

```
## Fase <número/nome> — <estado: CONCLUÍDA | EM CURSO | BLOQUEADA>
- Data: <timestamp>
- Commit: <hash curto>
- Resumo: <2-3 frases sobre o que foi feito>
- Ficheiros principais alterados: <lista>
```

Antes de começares uma fase nova, lê `.agent-sync/CLAUDE_REVIEW.md` — se houver uma
secção "AÇÃO NECESSÁRIA" pendente referente à tua última entrada aqui, corrige isso
primeiro, antes de avançar.

---

## Histórico

## Fase 8 — Importador de Partituras MIDI — CONCLUÍDA
- Data: 2026-08-14 18:11 (UTC+1)
- Commit: 6f91329
- Resumo: Criado o módulo core/midi_importer.py com parser SMF Format 0/1 em Python puro sem dependências externas pesadas. Implementada a extração de melodias, quantização rítmica, cálculo ergonómico automático de dedilhação de piano e posições na viola (minimizando saltos de mão), integração com botão «📂 Importar Música (.mid)» no ecrã de repertório e persistência em user_songs.json.
- Ficheiros principais alterados: core/midi_importer.py, core/notes.py, core/guitar.py, gui/screens/practice_song.py, tests/test_midi_importer.py, README.md

## Fases 6 e 7 + Correções Adaptativo & Gráficos — CONCLUÍDA
- Data: 2026-08-14 18:06 (UTC+1)
- Commit: d55815b
- Resumo: Implementado o motor de prática adaptativa (core/adaptive_engine.py) com identificação de pontos fracos e decaimento de recência, ligado diretamente aos ecrãs de treino auditivo e leitura de pauta via interruptores de Modo Adaptativo. O ecrã de estatísticas foi enriquecido com gráficos de tendência semanal, histórico de atividade estilo GitHub (90 dias) e comparação de barras com as 5 categorias de estudo completas em Canvas nativo.
- Ficheiros principais alterados: core/adaptive_engine.py, gui/screens/practice_ear.py, gui/screens/practice_staff.py, gui/screens/stats_screen.py, gui/screens/main_menu.py, tests/test_adaptive.py, README.md
