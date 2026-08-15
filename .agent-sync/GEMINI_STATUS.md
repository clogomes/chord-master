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

## Correção — Bug de Mapeamento Pixel→Nota no OMR (Fases 18-19) — CONCLUÍDA
- Data: 2026-08-14 20:00 / commitada pelo Claude durante interrupção de quota
- Commit: bb9339a (commitado pelo Claude), aprovado em 5e46101
- Resumo: Corrigido bug sistemático em core/omr_importer.py::map_pixel_to_note() — ref_idx usava min(1, len-1) que apontava à 2ª linha do TOPO, quando devia apontar à 2ª linha do FUNDO (max(0, len-2), índice 3 numa pauta de 5). Todas as notas importadas saíam 4 graus diatónicos (uma 4ª) abaixo do correto. Corrigidos também os testes TestMapPixelToNote que replicavam a mesma assunção errada. Adicionados 2 testes de integração end-to-end (treble + bass) que usam detect_staff_lines() real em vez de fixtures à mão — estes testes teriam apanhado o bug originalmente. 134/134 testes a passar.
- Ficheiros alterados: core/omr_importer.py, tests/test_omr_importer.py

## Fases 18 e 19 — OMR: Motor de Reconhecimento Ótico de Partituras + Ecrã de Revisão — CONCLUÍDAS
- Data: 2026-08-14 19:38 (UTC+1)
- Commit: 991cd58
- Resumo: Fase 18 — criado core/omr_importer.py com pipeline OMR leve puro (sem ML): load_image_from_file() aceita PDF/JPG/PNG/GIF, binarize() com limiar simples, detect_staff_lines() por projeção horizontal + fusão de picos, detect_noteheads() com scipy.ndimage.label + filtragem por área/proporção, map_pixel_to_note() inverso do diatonic_step, import_score_as_song() pipeline completo. Fase 19 — criado gui/screens/omr_review.py com lista scrollável editável (altura + duração + eliminar), inserção de notas, preview da imagem original (CTkImage/Pillow), e guardar com assign_piano_fingerings + assign_guitar_coordinates + save_user_song. Botão «🖼️ Importar Partitura (PDF/Imagem)» adicionado à sidebar do practice_song.py com diálogo de clave e fallback gracioso se deps em falta. 131/131 testes a passar. Pillow, PyMuPDF e scipy adicionados a requirements.txt.
- Ficheiros principais alterados: core/omr_importer.py, gui/screens/omr_review.py, gui/screens/practice_song.py, tests/test_omr_importer.py, requirements.txt, README.md

## Fase 17 — Formatação Markdown Enriquecida no Ecrã de Teoria — CONCLUÍDA
- Data: 2026-08-14 19:25 (UTC+1)
- Commit: 2384355
- Resumo: Criado o módulo gui/markdown_renderer.py com parser puro de markdown (sem dependências externas) e renderizador visual que integra cabeçalhos h1/h2/h3 com fontes em cascata, separadores de linha (─), bullets com indentação, bold inline **...** via tags Tk, e tabelas markdown como widgets CTkFrame embutidos com alternância de cor por linha. O renderizador substituiu o plain .insert() nos três blocos de texto do TheoryScreen (conteúdo, piano_focus, guitar_focus). Criada a suite tests/test_markdown_renderer.py; total de 116/116 testes a passar com 100% de sucesso.
- Ficheiros principais alterados: gui/markdown_renderer.py, gui/screens/theory_screen.py, tests/test_markdown_renderer.py, README.md

## Fase 16 — Dicas Práticas de Técnica e Ergonomia (Piano & Viola) — CONCLUÍDA
- Data: 2026-08-14 19:20 (UTC+1)
- Commit: ab5c1b6
- Resumo: Expandidos os campos piano_focus e guitar_focus de todos os 8 capítulos de core/theory_content.py com 2-3 dicas práticas detalhadas e acionáveis, cobrindo alinhamento postural, relaxamento muscular, exercícios de independência e força dos dedos (Hanon simplificado e Spider Walk 1-2-3-4), prevenção de ruído e trastejar (fret buzz), abafamento de cordas (string muting), dedilhações pivot, pedalação sincopada e rotinas de estudo de 20 minutos com rampa de tempo. Todos os 92 testes a passar com 100% de sucesso.
- Ficheiros principais alterados: core/theory_content.py, README.md

## Fase 15 — Alternador de Idioma PT/EN & Internacionalização — CONCLUÍDA
- Data: 2026-08-14 19:18 (UTC+1)
- Commit: 2f85e4f
- Resumo: Criado o módulo gui/i18n.py com dicionário bilingue simétrico PT/EN e persistência de preferência de idioma em data/app_settings.json. Adicionado seletor de idioma segmentado [🇵🇹 PT | 🇬🇧 EN] na barra lateral de gui/app.py com reconstrução dinâmica da UI ao alternar idioma. Criado o módulo core/i18n_helpers.py com funções de localização para notas, acordes, escalas e intervalos (solfejo em PT e notação científica em EN). Suite tests/test_i18n.py criada com 92/92 testes a passar com 100% de sucesso.
- Ficheiros principais alterados: gui/i18n.py, core/i18n_helpers.py, gui/app.py, data/app_settings.json, tests/test_i18n.py, README.md

## Fase 14 — Síntese Sonora Realista & Timbres Distintos (Piano vs Viola) — CONCLUÍDA
- Data: 2026-08-14 19:16 (UTC+1)
- Commit: 83cb67f
- Resumo: Implementado o algoritmo clássico de modelação física Karplus-Strong em audio/synthesizer.py (generate_plucked_string) para sintetizar cordas dedilhadas realistas de viola e guitarra. Atualizado audio/player.py com suporte a instrument="guitar" e chaves de cache isoladas, e integrado no clique de trastes do braço da viola (gui/components/guitar_fretboard.py). Criada a suite tests/test_synthesizer.py com 86/86 testes a passar com 100% de sucesso.
- Ficheiros principais alterados: audio/synthesizer.py, audio/player.py, gui/components/guitar_fretboard.py, tests/test_synthesizer.py, README.md

## Fase 13 — Correções de UI: Scroll do Rato & Piano Alargado — CONCLUÍDA
- Data: 2026-08-14 19:15 (UTC+1)
- Commit: 6718d62
- Resumo: Criado o utilitário gui/scroll_utils.py com bind_mousewheel para propagar eventos de roda do rato (<MouseWheel>, <Button-4>, <Button-5>) de forma recursiva por todos os contentores CTkScrollableFrame do projeto e seus filhos, resolvendo o problema de scroll nos ecrãs de teoria, repertório, treino auditivo, pauta, afinador, estatísticas e modal de utilizadores. O teclado visual PianoKeyboard foi alargado de 2 para 4 oitavas completas (C2 a B5, 28 teclas brancas e 20 pretas) em todos os ecrãs principais.
- Ficheiros principais alterados: gui/scroll_utils.py, gui/components/piano_keyboard.py, gui/screens/theory_screen.py, gui/screens/practice_song.py, gui/screens/practice_instrument.py, gui/screens/practice_scales.py, gui/screens/practice_ear.py, gui/screens/practice_staff.py, gui/screens/stats_screen.py, gui/screens/tuner_screen.py, gui/components/user_modal.py, README.md

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
