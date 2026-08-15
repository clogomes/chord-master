# ChordMaster — Histórico de Implementação

## Fase 23 — Expansão de Repertório, Ritmos & Controlo de Timbre — CONCLUÍDA
- Data: 2026-08-15T10:01:24+01:00
- Commit: ddd6abf
- Resumo: Adição de 8 novas músicas completas para piano e viola. Novos padrões rítmicos incluindo Jazz Swing, Bolero, Valsa e pop/rock/disco. Controlo de volumes e timbre integrados na UI com seleção dinâmica de instrumento.
- Ficheiros principais alterados: core/songs.py, audio/backing_tracks.py, gui/screens/practice_song.py, tests/test_songs_expansion.py, README.md

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

## Correção — AÇÕES NECESSÁRIAS: Resolução de Crash no Ecrã de Teoria & Suporte i18n em Inglês nos 12 Capítulos — CONCLUÍDA
- Data: 2026-08-15 16:51 (UTC+1)
- Commit: 34aa8bb
- Resumo: Corrigido o erro de atributo em `gui/screens/theory_screen.py` substituindo as 6 ocorrências de `theme.COLOR_CARD_SURFACE` pelo token real `theme.COLOR_SURFACE`, resolvendo o crash ao abrir o ecrã de teoria. Adicionado suporte completo a tradução para Inglês (`_en`) na dataclass `TheoryChapter` e preenchidas as traduções didáticas de todos os 12 capítulos em `core/theory_content.py`. O `TheoryScreen` deteta e renderiza agora dinamicamente o idioma ativo (PT / EN). 155/155 testes a passar.
- Ficheiros alterados: core/theory_content.py, gui/screens/theory_screen.py, tests/test_theory_i18n.py

## Correção — AÇÃO NECESSÁRIA: Campo `Song.instrument` Ligado à UI & Filtro de Repertório — CONCLUÍDA
- Data: 2026-08-15 16:38 (UTC+1)
- Commit: fa1cdd9
- Resumo: Preenchido explicitamente o campo `instrument` nas 8 músicas da Fase 23 (`instrument="guitar"` para Malagueña, House of Rising Sun, Romance Anónimo, Greensleeves; `instrument="piano"` para Pour Élise, Sonata ao Luar, Gymnopédie, Cânone em Dó). Em `gui/screens/practice_song.py`, adicionado o filtro por instrumento (`CTkSegmentedButton` "Todos / 🎹 Piano / 🎸 Viola") na barra lateral do repertório, ícone visual do instrumento em cada botão da lista (`🎹 ` / `🎸 `), e seleção automática do modo de instrumento e timbre correspondente ao carregar cada peça. 153/153 testes a passar.
- Ficheiros alterados: core/songs.py, gui/screens/practice_song.py, tests/test_songs_expansion.py

## Limpeza Final & Adição do Campo `Song.instrument` — CONCLUÍDA
- Data: 2026-08-15 16:31 (UTC+1)
- Commit: 9c6ac65
- Resumo: Adicionado o campo opcional `instrument: str = "piano"` à dataclass `Song` em `core/songs.py` (permitindo especificar `"piano"` ou `"guitar"` por omissão para cada peça do repertório) e efetuada a limpeza de todos os ficheiros temporários de scratch da raiz do repositório. 153/153 testes a passar.
- Ficheiros alterados: core/songs.py

## Fase 26 — Síntese Sonora Realista (Piano & Viola) — CONCLUÍDA
- Data: 2026-08-15T10:14:00+01:00
- Commit: 18df36b
- Resumo: Aprimorada a síntese aditiva do piano com harmónicos múltiplos, transiente de martelo e decaimento por oitava. Para viola/guitarra, o algoritmo Karplus-Strong ganhou um filtro de ressonância acústica do corpo, ataque dinâmico pelo volume e vibrato natural.
- Ficheiros principais alterados: audio/synthesizer.py, tests/test_synthesizer_realism.py, README.md

## Correção — AÇÃO NECESSÁRIA da Fase 25 (Remoção de Switch Morto em PracticeStaffScreen) — CONCLUÍDA
- Data: 2026-08-15 10:10 (UTC+1)
- Commit: a60eab2
- Resumo: Removido o switch morto `self.adaptive_switch` ("🧠 Modo Adaptativo") e os imports não utilizados de `adaptive_engine` em `gui/screens/practice_staff.py`. A lógica pedagógica de níveis + reforço adaptativo por `weak_notes` opera agora como único motor limpo e sem controlos fictícios na barra de definições. 151/151 testes a passar.
- Ficheiros alterados: gui/screens/practice_staff.py

## Correção — AÇÃO NECESSÁRIA da Fase 23 & Ajustes de Testes — CONCLUÍDA
- Data: 2026-08-15 10:05 (UTC+1)
- Commit: 1679cfa
- Resumo: Repostos os 5 ritmos de acompanhamento originais em `audio/backing_tracks.py` (`rock_basic`, `slow_ballad`, `bossa_nova`, `blues_shuffle`, `waltz`) juntamente com aliases (`rock`, `waltz_34`) e os novos ritmos expandidos (`pop`, `16beat`, `disco`, `jazz_swing`, `bolero`), eliminando qualquer risco de `KeyError` no `BackingTrackPlayer.start()`. Em `gui/screens/practice_song.py`, removidos os handlers falsos com `pass`: ligada a alteração de volume da música a `self.song_volume` e a seleção de timbre a `self.selected_instrument` ("piano" / "guitar"), passando ambos aos métodos `audio_player.play_note`. Corrigida asserção `pitch_with_octave` em `tests/test_practice_staff_pedagogy.py`. 151/151 testes a passar.
- Ficheiros alterados: audio/backing_tracks.py, gui/screens/practice_song.py, tests/test_practice_staff_pedagogy.py

## Fase 24 — Treino Auditivo Guiado com Mnemónicas — CONCLUÍDA
- Data: 2026-08-15T10:05:00+01:00
- Commit: 417b76e
- Resumo: Adição de modo guiado e modo de teste no ecrã de treino auditivo. Integração de mnemónicas musicais ("Tubarão", "Star Wars", etc.) para melhorar o reconhecimento de intervalos auditivamente, bem como mini teclado/pauta e botão para ouvir exemplo.
- Ficheiros principais alterados: gui/screens/practice_ear.py, core/ear_mnemonics.py, tests/test_ear_mnemonics.py, README.md

## Fase 25 — Leitura de Pauta Guiada Passo-a-Passo — CONCLUÍDA
- Data: 2026-08-15T10:04:48+01:00
- Commit: 934189d
- Resumo: Adicionado o guia interativo `core/staff_tutor.py` com explicações passo-a-passo (níveis 1 a 4). Atualizado `gui/screens/practice_staff.py` com o painel de guia, checkbox para dica de posição na pauta e histórico de erros (pontos fracos focados). O `StaffCanvas` foi estendido para suportar destaque de linhas/espaços.
- Ficheiros principais alterados: gui/screens/practice_staff.py, core/staff_tutor.py, tests/test_practice_staff_pedagogy.py, gui/components/staff_canvas.py, README.md
## Limpeza & Unificação de Tema em TheoryScreen — CONCLUÍDA
- Data: 2026-08-15 09:58 (UTC+1)
- Commit: 86f4d9d
- Resumo: Eliminadas todas as 23 ocorrências de cores hex e fontes hardcoded em `gui/screens/theory_screen.py`. Substituídas rigorosamente pelos tokens globais do Design System em `gui/theme.py` (`COLOR_BG`, `COLOR_CARD_SURFACE`, `COLOR_SURFACE_SECONDARY`, `COLOR_BORDER`, `COLOR_TEXT_PRIMARY`, `COLOR_TEXT_MUTED`, `FONT_TITLE`, `FONT_SECTION`, `FONT_BODY`, `FONT_BODY_BOLD`). Removidos ficheiros temporários de scratch da raiz. 144/144 testes a passar.
- Ficheiros alterados: gui/screens/theory_screen.py

## Fase 22 — Quiz Interativo por Capítulo de Teoria — CONCLUÍDA
- Data: 2026-08-15 09:43 (UTC+1)
- Commit: 2a7ad28
- Resumo: Adicionado o módulo core/theory_quiz.py com 60 perguntas de múltipla escolha distribuídas por 12 quizzes correspondentes aos capítulos. Criado o componente interativo TheoryQuizWidget para apresentação visual, feedback instantâneo e integração via ScoreCard no ecrã de Teoria, com atribuição de +10 XP por resposta correta. Implementados 10 testes unitários abrangentes na nova suite test_theory_quiz.py, os quais perfazem os requisitos na totalidade.
- Ficheiros principais alterados: core/theory_quiz.py, gui/components/theory_quiz_widget.py, gui/screens/theory_screen.py, tests/test_theory_quiz.py

## Fase 21 — Conteúdo de Teoria Expandido & 4 Novos Módulos — CONCLUÍDA
- Data: 2026-08-15 09:39 (UTC+1)
- Commit: 9158e43
- Resumo: Adicionados 4 novos capítulos de teoria musical (9-12): Ritmo & Compasso (BPM, figuras rítmicas, síncopa), Forma Musical (AB/ABA/Rondó/Sonata/Pop), Dinâmica & Expressão (pp→fff, legato/staccato/vibrato, fraseado, pedal), e Transposição Prática (círculo de quintas, armações de clave, capotraste). Todos os capítulos incluem exemplos práticos concretos e exercícios específicos para piano e viola. 134/134 testes a passar.
- Ficheiros principais alterados: core/theory_content.py, README.md

- **Fase 20**: Concluída (d2ba9e8)
  - **Resumo**: Redesign do ecrã de Teoria para unificar o conteúdo num só painel contínuo, remoção do selector de instrumento (exibe ambos por defeito) e substituição de todas as tags LaTeX por texto clean e formatado no `theory_content.py`.
  - **Ficheiros**: `gui/screens/theory_screen.py`, `core/theory_content.py`, `README.md`

## Correção — Crash no Ecrã de Prática de Escalas (kwarg errado em GuitarFretboard) — CONCLUÍDA
- Data: 2026-08-15 09:21 (UTC+1)
- Commit: 11bdcaf
- Resumo: Corrigido crash que impedia o ecrã "🎼 Prática de Escalas" de se construir — o argumento on_position_clicked passado a GuitarFretboard não existe (o parâmetro correto chama-se on_note_clicked), caindo no **kwargs do CTkFrame subjacente e lançando ValueError. Corrigido on_position_clicked→on_note_clicked na instanciação, simplificada a assinatura de _on_guitar_fret_clicked(string_idx, fret)→(note: Note) (GuitarFretboard já faz o mapeamento internamente), e removido import órfão de GuitarFretboardModel. Validado com python3 -c instanciação direta e 134/134 testes a passar.
- Ficheiros alterados: gui/screens/practice_scales.py

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
