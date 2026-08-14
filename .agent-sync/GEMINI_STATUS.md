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

## Correção — Otimização do Relógio do BackingTrackPlayer — CONCLUÍDA
- Data: 2026-08-14 18:40 (UTC+1)
- Commit: 5c2c628
- Resumo: Refatorado o método `BackingTrackPlayer._run_loop()` em `audio/backing_tracks.py` para eliminar por completo o busy-wait spin loop (`while pass`), substituindo-o por agendamento monotónico drift-free via `_stop_event.wait(timeout=sleep_time)`. O relógio agora mantém precisão milimétrica sem acumulação de deriva temporal e com 0% de uso desnecessário de CPU, reagindo imediatamente ao comando de paragem.
- Ficheiros principais alterados: audio/backing_tracks.py

## Fase 12 — Estúdio de Prática de Escalas & Modos — CONCLUÍDA
- Data: 2026-08-14 18:36 (UTC+1)
- Commit: 826efdc
- Resumo: Criado o novo ecrã gui/screens/practice_scales.py com suporte a qualquer tónica cromática e às 16 escalas/modos teóricos, execução bidirecional (ascendente/descendente), modos de visualização isolados ou combinados para Piano e Viola, dedilhação inteligente partilhada (core/fingering.py) e coordenadas no braço da viola (core/guitar.py), acompanhamento de bateria sintetizada com BackingTrackPlayer, Metronome com avaliação de precisão rítmica em milissegundos, Rampa de Tempo Automática (70% ➔ 100% BPM), teclado de PC, teclado MIDI USB e demonstração sintetizada. Adicionados atalhos e rotas em gui/app.py e gui/screens/main_menu.py, com 82/82 testes unitários a passar com 100% de sucesso.
- Ficheiros principais alterados: gui/screens/practice_scales.py, core/fingering.py, core/guitar.py, core/midi_importer.py, gui/app.py, gui/screens/main_menu.py, gui/screens/__init__.py, tests/test_fingering.py, tests/test_guitar.py, README.md

## Fase 11 — Expansão do Catálogo de Escalas & Modos — CONCLUÍDA
- Data: 2026-08-14 18:33 (UTC+1)
- Commit: b5ed5df
- Resumo: Expandido o catálogo SCALE_TYPES em core/scales.py com 7 novas escalas e modos: Frígio, Lídio, Lócrio (completando os 7 modos gregos), Tons Inteiros (Hexatónica), Cromática (12 semitons), Bebop Dominante e Menor Húngara (Cigana). Adicionado teste automatizado genérico em tests/test_scales.py que valida para todas as escalas a progressão estrita de 0 a 12 semitons e a integridade descritiva.
- Ficheiros principais alterados: core/scales.py, tests/test_scales.py, README.md

## Fase 10 — Motor de Acompanhamento Rítmico Sintetizado — CONCLUÍDA
- Data: 2026-08-14 18:32 (UTC+1)
- Commit: c6436bc
- Resumo: Criado o módulo audio/backing_tracks.py com geradores sintetizados em NumPy puro para bombo (kick com pitch sweep), tarola/caixa (snare com esteira de ruído), prato de choque (hihat aberto/fechado) e prato de condução (ride ressonante). Definida a biblioteca BACKING_TRACK_LIBRARY com 5 estilos rítmicos (Rock Básico, Balada Lenta, Bossa Nova, Blues Shuffle e Valsa Clássica) e implementado o BackingTrackPlayer com reprodução em loop precisa em thread daemon, integrado no estúdio de repertório (practice_song.py) com sincronização ao slider de BPM e à Rampa de Tempo.
- Ficheiros principais alterados: audio/backing_tracks.py, gui/screens/practice_song.py, tests/test_backing_tracks.py, README.md

## Fase 9 — Notação Rítmica Real & Prática de Tempo Guiada + Correção Notes — CONCLUÍDA
- Data: 2026-08-14 18:15 (UTC+1)
- Commit: 647b4cd (anterior d7d54d8)
- Resumo: Corrigida a duplicação de __str__ e __repr__ na classe Note em core/notes.py conforme apontado na revisão da Fase 8. Adicionado o campo time_signature ao dataclass Song com suporte a 4/4, 3/4 e 6/8. A StaffCanvas foi estendida para renderizar fórmulas de compasso e barras de compasso (barlines) dinâmicas, com cabeças de nota ocas para figuras longas. O ecrã de treino acústico (practice_instrument.py) foi integrado com o Metronome e avaliação de precisão rítmica. Foi também implementada a funcionalidade de "Rampa de Tempo Automática" (70% ➔ 100% BPM) em practice_song.py e practice_instrument.py.
- Ficheiros principais alterados: core/notes.py, core/quiz_engine.py, core/songs.py, gui/components/staff_canvas.py, gui/screens/practice_song.py, gui/screens/practice_instrument.py, tests/test_songs.py, README.md

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
