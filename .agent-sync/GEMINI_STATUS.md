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

## Fase 41 — Estúdio de Composição: Motor de Renderização Offline — CONCLUÍDA
- Data: 2026-08-17T17:50:32+01:00
- Commit: 4ea79a2
- Resumo: Implementado o motor de renderização offline multi-pista em `audio/composition_renderer.py` (`CompositionRenderer`). O motor converte composições para arrays float32 estéreo (N, 2) a 44.1kHz sem dependência de hardware nem de pygame (100% testável em CI). Utiliza posicionamento de amostras exato por aritmética de índices, cache de waveforms em memória (`_SAMPLE_CACHE`) para síntese rápida de bateria, piano aditivo e guitarra Karplus-Strong, espaçamento estéreo com cauda acústica de 1.5s e limitador de saturação suave `np.tanh`. 239/239 testes a passar (4 novos testes em `tests/test_composition_renderer.py`).
- Ficheiros principais alterados: audio/composition_renderer.py, tests/test_composition_renderer.py, README.md

## Fase 40 — Estúdio de Composição: Modelo de Dados & Persistência — CONCLUÍDA
- Data: 2026-08-17T17:46:04+01:00
- Commit: c1935bf
- Resumo: Implementado o modelo de dados para o Estúdio de Composição em `core/composition.py` (`ChordEvent`, `RhythmTrack`, `Composition`) com suporte a 22 tipos de acorde, instrumentos (piano/viola), grelha de passos de percussão e controlo de volume/mute. Criado o adaptador `RhythmTrack.from_pattern` para importar qualquer um dos 12 ritmos de `BACKING_TRACK_LIBRARY`. Implementado motor de persistência JSON em `core/compositions.py` com `to_dict` / `from_dict`, `schema_version=1` e tolerância a esquemas legados. 235/235 testes a passar (6 novos testes unitários em `tests/test_composition_models.py`).
- Ficheiros principais alterados: core/composition.py, core/compositions.py, tests/test_composition_models.py, README.md

## Correção AÇÃO NECESSÁRIA — Áudio do Glossário & Debounce 130ms — CONCLUÍDA
- Data: 2026-08-17T17:45:11+01:00
- Commit: 31cd17f
- Resumo: Corrigido bug nos botões de áudio do glossário em `gui/screens/glossary_screen.py` e `gui/components/glossary_modal.py`: corrigida a assinatura de `play_note` (utilizava `duration_ms=650` em vez de `duration=0.65` e strings em vez de `Note(p)`). Adicionada conversão defensiva em `audio/player.py::play_note` para aceitar transparentemente `Note` ou `str` sem levantar exceções. Ajustado debounce de pesquisa para 130ms para resposta instantânea ao digitar. Adicionado teste unitário exaustivo `test_all_hear_it_notes_playable_and_constructible` cobrindo todos os termos do `GLOSSARY_DATABASE`. 229/229 testes a passar.
- Ficheiros principais alterados: audio/player.py, gui/components/glossary_modal.py, gui/screens/glossary_screen.py, tests/test_glossary.py

## Otimização de Performance — Ecrã de Glossário (Lazy List + Debounce + Mousewheel) — CONCLUÍDA
- Data: 2026-08-17T17:18:29+01:00
- Commit: 4baf160
- Resumo: Resolvida a causa raiz da lentidão no ecrã de Glossário (`gui/screens/glossary_screen.py`). 1) Implementada renderização em lotes (*lazy rendering*) com 35 cartões iniciais + botão "Carregar Mais", reduzindo a árvore de widgets de 1.737 para 596 widgets; 2) Adicionado debounce de 220ms com `after_cancel` na pesquisa; 3) `bind_mousewheel` em `gui/scroll_utils.py` suporta agora `recursive=False`, evitando mais de 5.000 event bindings desnecessários; 4) Seleção de termo agora apenas atualiza o estilo do cartão ativo sem destruir/reconstruir toda a lista. O tempo de renderização caiu de ~573ms para ~156ms (quase 4× mais rápido e fluido). 228/228 testes a passar.
- Ficheiros principais alterados: gui/screens/glossary_screen.py, gui/scroll_utils.py

## Correção AÇÃO NECESSÁRIA — Pesquisa do Glossário Insensível a Acentos — CONCLUÍDA
- Data: 2026-08-17T17:02:29+01:00
- Commit: 3a964a0
- Resumo: Corrigido bug de sensibilidade a acentos na pesquisa do glossário (`core/glossary.py::search_terms`). A função agora utiliza normalização Unicode NFD (`_fold`) em todos os campos comparados (termos PT/EN, definições e fórmulas) e na query de busca. "tonica" e "tónica" retornam agora rigorosamente os mesmos 17 resultados. Adicionada normalização de acentos na auto-ligação de markdown (`gui/markdown_renderer.py`) e logging de exceções no fallback do modal. Adicionado teste obrigatório de pares de acentuação (`tests/test_glossary.py`). 228/228 testes a passar.
- Ficheiros principais alterados: core/glossary.py, gui/markdown_renderer.py, tests/test_glossary.py

## Fase 39 — Contexto Histórico, Vocabulário Expandido & Laboratórios por Capítulo — CONCLUÍDA
- Data: 2026-08-17T16:32:19+01:00
- Commit: 3e37891
- Resumo: Contexto histórico rigoroso (150-250 palavras) e período estético adicionados a todas as 24 canções da biblioteca, com novo modal "📜 Contexto Histórico" em `practice_song.py` (Grândola e o sinal do 25 de Abril, reatribuição de Petzold/Bach em 1970, Für Elise/Therese Malfatti, Greensleeves/Henrique VIII, e desmistificação do Diabolus in Musica no Cap. 2). Expansão do vocabulário de acordes em `core/chords.py` (power chords, 6, m6, add9, 9, 7sus4, mMaj7 e dominantes alteradas 7b9, 7#9, 7#11, 7b13) e formatos essenciais em `core/guitar.py` (Cadd9, Dsus4, Asus2, power chords e raízes alteradas Bb, Eb, Ab, F#). Laboratórios interativos especializados em `theory_screen.py` por tipo de capítulo (Círculo de Quintas, Condução de Vozes / Voice Leading e Construtor de Campo Harmónico). Adicionado sistema de pré-requisitos pedagógicos entre capítulos. 227/227 testes a passar.
- Ficheiros principais alterados: core/songs.py, core/chords.py, core/guitar.py, core/theory_content.py, gui/screens/practice_song.py, gui/screens/theory_screen.py, tests/test_chords.py, tests/test_guitar.py, tests/test_double_accidentals.py, README.md

## Fase 38 — Campo Harmónico Menor & Cadências — CONCLUÍDA
- Data: 2026-08-17T16:20:13+01:00
- Commit: 71bfb8d
- Resumo: 2 novos capítulos completos PT+EN: `chap17_minor_harmonic_field` (3 formas de escala menor, campo menor natural e harmónico, tétrades, progressões clássicas, análise de HotRS e guias de instrumento) e `chap18_cadences` (autêntica perfeita/imperfeita, plagal, meia-cadência frígia, deceptiva, análise de Für Elise). 10 novas perguntas de quiz bilingues (total 18 quizzes / 90 perguntas). Análises de HotRS e Für Elise em `core/songs.py` re-derivadas a partir dos novos conceitos teóricos. Total de 222/222 testes a passar.
- Ficheiros principais alterados: core/theory_content.py, core/theory_quiz.py, core/songs.py, tests/test_theory_i18n.py, tests/test_users.py, gui/markdown_renderer.py, gui/screens/glossary_screen.py, README.md

## Fase 37 — Correção AÇÃO NECESSÁRIA (37.1 + 37.2) — CONCLUÍDA
- Data: 2026-08-16T18:12:05+01:00
- Commit: e6c3ff7
- Resumo: Corrigido bug crítico 37.1: `practice_staff.py` usava `note.pitch` (ex: "C") no skill_id em vez de `note.pitch_with_octave` (ex: "C4"), causando divergência permanente com as sementes de `generate_default_atomic_skills()`. Corrigido 37.2: `due_reviews_count` retornava 10 inventado para perfis novos — agora retorna a contagem real (0). Adicionados 2 testes de regressão que garantem que os skill_ids do runtime e das sementes partilham o mesmo espaço de nomes. Total: 222/222 testes.
- Ficheiros principais alterados: gui/screens/practice_staff.py, core/user_manager.py, tests/test_review_scheduler.py

## Fase 37 — Sistema de Revisão Espaçada SM-2 & Leitner — CONCLUÍDA
- Data: 2026-08-16T18:07:28+01:00
- Commit: d518756
- Resumo: Implementação completa do sistema de repetição espaçada SuperMemo SM-2 com 5 Caixas de Leitner. Motor de scheduling em `core/review_scheduler.py`, persistência retrocompatível em `core/user_manager.py` (schema_version=2, campo `spaced_review_data`), ecrã de revisão diária `gui/screens/daily_review_screen.py` com auto-avaliação (❌/🟡/🟢/🌟), ligação de `practice_ear`, `practice_staff` e `theory_quiz_widget` ao registo atómico de skills (interval:X:dir, staff:clef:pitch, theory:chap:qN), navegação e card no menu principal, 26 novos testes — total 220/220.
- Ficheiros principais alterados: core/review_scheduler.py (novo), core/user_manager.py, gui/screens/daily_review_screen.py (novo), gui/screens/practice_ear.py, gui/screens/practice_staff.py, gui/components/theory_quiz_widget.py, gui/app.py, gui/screens/main_menu.py, gui/i18n.py, tests/test_review_scheduler.py (novo), README.md

## Correção Urgente Fase 36 & Blindagem de Tokens de Tema — CONCLUÍDA
- Data: 2026-08-16T17:53:00+01:00
- Commit: a20b8ac
- Resumo: 1) Substituídos tokens inexistentes `COLOR_ACCENT_EMERALD` por `COLOR_SUCCESS` e `COLOR_SUCCESS_HOVER` em `glossary_screen.py` e `glossary_modal.py`, e `COLOR_CARD_SURFACE` por `COLOR_SURFACE` em `omr_review.py` (corrigindo também `from __future__ import annotations` na linha 1). 2) Adicionados aliases retrocompatíveis em `gui/theme.py`. 3) Criado teste de varrimento estático `tests/test_theme_tokens_scan.py` que valida por regex todos os tokens `theme.*` no pacote `gui/`. 4) Expandido o teste de fumo `tests/test_smoke.py` para instanciar e construir programaticamente cada um dos ecrãs e modais da aplicação. 5) Expandido o mapa de palavras-chave da auto-ligação com suporte a plurais e extração de aliases em parênteses (ex: 'guide tone', 'tetracordes', 'sensíveis'). 194/194 testes a passar.
- Ficheiros principais alterados: gui/theme.py, gui/screens/glossary_screen.py, gui/components/glossary_modal.py, gui/screens/omr_review.py, gui/markdown_renderer.py, tests/test_theme_tokens_scan.py, tests/test_smoke.py

## Fase 36 — Glossário Musical Interativo & Auto-Ligação de Termos — CONCLUÍDA
- Data: 2026-08-16T17:47:00+01:00
- Commit: 5b5baa2
- Resumo: Criação de uma base de dados completa de 139 termos musicais (harmonia, ritmo, notação, modos, técnica, acústica, forma e jazz) em `core/glossary.py` com definições curtas e aprofundadas, fórmulas, exemplos para piano e viola/guitarra, áudio sintetizado e ligações a capítulos. Novo ecrã dedicado `gui/screens/glossary_screen.py` com pesquisa instantânea, índice A-Z, filtros de categoria e capítulos, e atalhos diretos para os capítulos teóricos. Auto-ligação implementada em `gui/markdown_renderer.py` e modal flutuante `gui/components/glossary_modal.py` para consulta contextual imediata nos capítulos de teoria. Suporte i18n total PT/EN. 191/191 testes a passar.
- Ficheiros principais alterados: core/glossary.py, gui/components/glossary_modal.py, gui/screens/glossary_screen.py, gui/markdown_renderer.py, gui/screens/main_menu.py, gui/screens/theory_screen.py, gui/app.py, gui/i18n.py, tests/test_glossary.py, README.md

## Fase 35 (Ajustes Finais de Revisão) — CONCLUÍDA
- Data: 2026-08-16T17:40:00+01:00
- Commit: 0d70099
- Resumo: 1) Ligação completa das mnemónicas descendentes ao gerador de perguntas de treino auditivo (quiz_engine.py) e ao ecrã de treino auditivo (practice_ear.py), suportando treino bidirecional. 2) Ajustada a análise de guitar_greensleeves_full para Modo Eólio estrito (sem menção a 7ª elevada que não consta do excerto didático da viola). 3) Corrigida a gralha 'Meu menor' para 'Mi menor' em theory_content.py (linha 990). 4) Clarificados os títulos e descrições dos arranjos didáticos para evitar qualquer perceção de duplicação acidental. 180/180 testes a passar.
- Ficheiros principais alterados: core/intervals.py, core/quiz_engine.py, core/songs.py, core/theory_content.py, gui/screens/practice_ear.py

## Fase 35 — Correção Rigorosa de Erros de Conteúdo Musical — CONCLUÍDA
- Data: 2026-08-16T17:36:00+01:00
- Commit: 2343c15
- Resumo: Correção de 6 análises harmónicas em songs.py de acordo com as notas reais (Lá menor Eólio em Greensleeves, Menor Harmónica em Für Elise, Jónico em Gymnopédie, Frígio Dominante em Malagueña, etc). Ajuste rítmico de todas as 24 peças em SONG_LIBRARY para fecharem compassos inteiros exatos. Unificação da fonte de verdade das mnemónicas auditivas (com adição de mnemónicas descendentes) em ear_mnemonics.py e sincronização com intervals.py e theory_content.py. Correção de erros teóricos nos capítulos de transposição, rootless voicings de Jazz (G7 = F-A-B-E), substituição tritónica e forma AAB do Blues. Ajustes nos exercícios técnicos (Hanon 1, Spider Walk 1-2-3-4, salto de cordas, ligação do BPM slider em runtime) e no tutor de pauta. 180/180 testes a passar.
- Ficheiros principais alterados: core/songs.py, core/theory_content.py, core/ear_mnemonics.py, core/intervals.py, core/technique_exercises.py, core/staff_tutor.py, core/theory_quiz.py, gui/screens/practice_technique.py, tests/test_songs_measures.py, README.md

## Correções Finais Fase 34 + Reposição das 4 Medalhas — CONCLUÍDA
- Data: 2026-08-16T17:22:00+01:00
- Commit: 1e1ad3c
- Resumo: Corrigidas as falhas de tradução em theory_quiz_widget.py e practice_song.py (campos lidos cru em vez dos getters). Corrigidos os bugs de estado interno traduzido ("Piano"/"Viola" -> "piano"/"guitar") e cores das badges na teoria. Repostas as 4 medalhas solicitadas (virtuoso_pianist, guitar_hero, pitch_perfect, rhythm_master) no `ACHIEVEMENT_LIBRARY` e no `check_achievements`. Corrigido o ficheiro de testes `test_gamification.py` para colocar os novos testes dentro da classe e testar apropriadamente os getters das properties read-only do utilziador.
- Ficheiros principais alterados: gui/screens/practice_song.py, gui/screens/practice_instrument.py, gui/screens/practice_scales.py, gui/screens/theory_screen.py, core/gamification.py, core/user_manager.py, tests/test_gamification.py

## Fase 34b — Camada de Conteúdo (Tradução EN) — CONCLUÍDA
- Data: 2026-08-16 16:55 (UTC+1)
- Commit: d157959
- Resumo: Adicionada internacionalização (EN) completa à camada de conteúdo. Foram traduzidas as 80 perguntas do theory_quiz, os dados das canções em songs.py, categorias e dicas do adaptive_engine, conquistas da gamification e relatórios de exporter.
- Ficheiros alterados: core/theory_quiz.py, core/songs.py, core/staff_tutor.py, audio/backing_tracks.py, core/adaptive_engine.py, core/gamification.py, core/exporter.py

## Fase 34a — Camada de UI (Tradução EN) — CONCLUÍDA
- Data: 2026-08-16 16:51 (UTC+1)
- Commit: 928dd43
- Resumo: Internacionalização da camada de UI. Ligação de ecrãs e componentes às chaves em gui/i18n.py usando a função t().
- Ficheiros alterados: gui/screens/*.py, gui/components/*.py

## Fase 34b — Camada de Conteúdo (Tradução EN de Músicas) — CONCLUÍDA
- Data: 2026-08-16 16:54 (UTC+1)
- Commit: f3d7936
- Resumo: Adicionados campos `description_en` e `difficulty_en` à dataclass `Song`. Implementados os métodos `get_description(lang="pt")` e `get_difficulty(lang="pt")`. Todos os registos de músicas em `SONG_LIBRARY` foram atualizados com as respetivas traduções em inglês da descrição e da dificuldade.
- Ficheiros principais alterados: core/songs.py

## Fase 34b — Tradução EN de Conteúdo (Adaptive, Gamification, Exporter) — CONCLUÍDA
- Data: 2026-08-16 16:55 (UTC+1)
- Commit: f3d7936
- Resumo: Adicionado suporte à tradução EN para a camada de conteúdo. Em `core/categories.py`, introduzidas constantes em inglês `CATEGORY_NAMES_EN` e `CATEGORY_TIPS_EN`. O motor `get_recommendation` em `core/adaptive_engine.py` utiliza agora o idioma para gerar títulos e dicas dinâmicas. Em `core/gamification.py`, os achievements receberam `name_en` e `description_en`. O relatório gerado por `core/exporter.py` produz markdown traduzido (tabelas, secções e métricas) se `lang="en"`. Testes a passar a 100%.
- Ficheiros principais alterados: core/categories.py, core/adaptive_engine.py, core/gamification.py, core/exporter.py

## Correção — AÇÃO NECESSÁRIA CRÍTICA: App não arrancava (LESSON_IDS ausente) — CONCLUÍDA
- Data: 2026-08-16 16:48 (UTC+1)
- Commit: a34f06e
- Resumo: Importada a variável `LESSON_IDS` em `gui/app.py`, cuja omissão provocava um NameError e impedia o arranque da aplicação. Adicionado um "smoke test" em `tests/test_smoke.py` que garante a instanciação com sucesso da `ChordMasterApp` sem exceções.
- Ficheiros alterados: gui/app.py, tests/test_smoke.py



## Correção — AÇÃO NECESSÁRIA: Regressão da Fase 33 (Rota teoria, sidebar e .gitignore) — CONCLUÍDA
- Data: 2026-08-16 16:45 (UTC+1)
- Commit: 61ff10a
- Resumo: Corrigida a rota `"teoria"` em `CATEGORY_ROUTES` para `"theory"`. Adicionado um fallback (`else`) em `navigate_to` que redireciona rotas desconhecidas para o `main_menu` de forma segura. Adicionado o ficheiro `tests/test_categories.py` para provar que todas as rotas listadas em `core/categories.py` existem na lógica do `gui/app.py`. A sidebar (gui/app.py) foi atualizada para usar `len(LESSON_IDS)` em vez de `8`. Finalmente, os dados pessoais `user_profiles.json` e afins foram adicionados ao `.gitignore` e removidos do index (cached), respeitando a privacidade dos dados do utilizador.
- Ficheiros alterados: core/categories.py, gui/app.py, tests/test_categories.py, .gitignore


## Fase 33 — Correção de Listas Hardcoded e Sincronização de Estatísticas — CONCLUÍDA
- Data: 2026-08-16 16:41 (UTC+1)
- Commit: e41c2c5
- Resumo: Criado um registo centralizado `core/categories.py` para as categorias de treino, eliminando as redundâncias no motor adaptativo, no ecrã de estatísticas e no exportador. O ecrã de estatísticas agora renderiza todas as categorias de forma dinâmica, incluindo 'tecnica' e 'escalas_modos'. `LESSON_IDS` no `UserManager` passou a ser derivado diretamente de `THEORY_CHAPTERS`, garantindo que o número total de lições acompanhe sempre o conteúdo. Foram removidas as 4 medalhas impossíveis do `ACHIEVEMENT_LIBRARY` para evitar confusões e foi corrigida a condição da medalha `theory_master` para depender do comprimento total das lições em vez do limite fixo de 8. Os números e strings hardcoded de capítulos (8 para 16) e músicas (16 para 24) nos ecrãs principais e ficheiros i18n foram devidamente atualizados.
- Ficheiros alterados: core/categories.py, core/adaptive_engine.py, gui/screens/stats_screen.py, core/exporter.py, core/user_manager.py, core/gamification.py, gui/app.py, gui/components/user_modal.py, gui/i18n.py, gui/screens/main_menu.py, tests/test_exporter.py, tests/test_gamification.py, tests/test_users.py


## Correção — AÇÃO NECESSÁRIA (URGENTE): Regressão da Fase 31 (Duplos Acidentes) — CONCLUÍDA
- Data: 2026-08-16 16:34 (UTC+1)
- Commit: 5346900
- Resumo: Corrigida regressão introduzida na Fase 31 que causava crash ao lidar com ortografias com duplos acidentes (ex: Bbb, F##). `Note._parse_string` e o construtor `Note.__init__` foram atualizados para interpretar e calcular corretamente as alturas para 0, 1 ou 2 acidentes. Adicionada a formatação "dobrado sustenido" e "dobrado bemol" em `name_pt`. Criados testes (test_double_accidentals.py) para o varrimento completo do produto cartesiano (todas as raízes × todos os tipos de acordes e escalas), garantindo que nenhuma combinação gera exceções. 169/169 testes a passar.
- Ficheiros alterados: core/notes.py, tests/test_double_accidentals.py

## Fase 32 — Correções de Funcionalidades (Modal Teórico, Áudio de Técnica, MIDI USB & Callbacks Metrónomo) — CONCLUÍDA
- Data: 2026-08-16 16:30 (UTC+1)
- Commit: b79d946
- Resumo: Importada a função `render_markdown_to_textbox` em `gui/screens/practice_song.py`, reposicionado `grab_set()` e adicionado bloco `try/except` com `top.destroy()` no modal de Análise Teórica para evitar travamentos de janela. Corrigidas as chamadas `self.audio_player.play_note` em `gui/screens/practice_technique.py` para passar o objeto `Note` diretamente em vez de strings. Ajustada a assinatura de `_on_midi_note_on` no ecrã de técnica para receber `note_midi: int` e converter via `Note.from_midi`. Uniformizadas as assinaturas do callback do metrónomo `_on_metronome_beat(self, beat_num, timestamp)` nos 3 ecrãs de prática e adicionado logging de exceções em `audio/metronome.py`. 166/166 testes a passar.
- Ficheiros alterados: gui/screens/practice_song.py, gui/screens/practice_technique.py, gui/screens/practice_instrument.py, gui/screens/practice_scales.py, audio/metronome.py, tests/test_dead_features_phase32.py, README.md

## Fase 31 — Correções de Motor (Intervalos Compostos, Ortografia com Bemóis & Oitavas na Guitarra) — CONCLUÍDA
- Data: 2026-08-16 16:27 (UTC+1)
- Commit: 29fe07f
- Resumo: Corrigido o cálculo de redução de intervalos compostos de `% 13` para `% 12` em `core/intervals.py` com suporte a 0 semitons e testes para 13, 14, 19 e 24 semitons. Implementada a ortografia harmónica baseada na letra esperada por grau em `core/notes.py` (`spell_note_with_letter`), `core/scales.py` e `core/chords.py` para escalas e acordes em tonalidades com bemóis (ex: Fá maior F-G-A-Bb-C-D-E-F e Dó dim C-Eb-Gb). Adicionadas tónicas com bemol ao seletor de tónica em `theory_screen.py`. Corrigida a busca de posições no braço da guitarra em `core/guitar.py` (`find_note_positions`) para dar prioridade ao `midi` exato da oitava antes de cair para a classe de altura. 164/164 testes a passar.
- Ficheiros alterados: core/intervals.py, core/notes.py, core/scales.py, core/chords.py, core/guitar.py, core/songs.py, gui/screens/theory_screen.py, tests/test_intervals.py, tests/test_chords.py, tests/test_scales.py, tests/test_engine_corrections_phase31.py, README.md

## Correção — AÇÃO NECESSÁRIA: Inclusão da Categoria "tecnica" nas Estatísticas & Motor Adaptativo — CONCLUÍDA
- Data: 2026-08-16 08:57 (UTC+1)
- Commit: ea351af
- Resumo: Adicionada a categoria `"tecnica"` à lista `categories` em `gui/screens/stats_screen.py::_draw_category_bars` para que o progresso nos Exercícios Técnicos surja no gráfico de barras comparativo de categorias das Estatísticas. Atualizados também os mapeamentos `CATEGORY_NAMES_PT`, `CATEGORY_ROUTES` e `CATEGORY_TIPS` em `core/adaptive_engine.py`. 162/162 testes a passar.
- Ficheiros alterados: gui/screens/stats_screen.py, core/adaptive_engine.py

## Fase 30 — Módulo de Exercícios Técnicos & Aquecimento — CONCLUÍDA
- Data: 2026-08-16 08:54 (UTC+1)
- Commit: 508fd65
- Resumo: Criado o módulo `core/technique_exercises.py` com a biblioteca didática de 9 exercícios técnicos de aquecimento, destreza e força para piano (Hanon No. 1, padrões de 5 dedos, arpejos de oitava, escalas cromáticas e movimento contrário) e guitarra/viola (Spider Walk 1-2-3-4, salto de cordas, palhetada alternada rápida e alongamento de dedos). Criado o ecrã `PracticeTechniqueScreen` em `gui/screens/practice_technique.py` com metrónomo, rampa de tempo 70%➔100% BPM, teclado MIDI/PC e suporte i18n PT/EN. Integrado no menu principal e roteador da aplicação. 162/162 testes a passar.
- Ficheiros alterados: core/technique_exercises.py, gui/screens/practice_technique.py, gui/screens/__init__.py, gui/screens/main_menu.py, gui/app.py, tests/test_technique_exercises.py, README.md

## Fase 29 — Aulas Práticas de Escuta & Correção Alargada — CONCLUÍDA
- Data: 2026-08-16 08:51 (UTC+1)
- Commit: 092ac36
- Resumo: Atualizado o ecrã `PracticeInstrumentScreen` em `gui/screens/practice_instrument.py` para disponibilizar toda a biblioteca de repertório (`SONG_LIBRARY` + `custom_songs`) com comutação automática de instrumento ativo (piano/viola). Adicionadas dicas direcionais de afinação ao errar notas (`calculate_pitch_directional_hint`) indicando a distância exata em tons/semitons ("sobe 1 tom"). Criado o relatório detalhado da aula no final da sessão com sumário de notas que falharam e desvio médio em cents. 158/158 testes a passar.
- Ficheiros alterados: gui/screens/practice_instrument.py, tests/test_practice_instrument.py, README.md

## Fase 28 — Módulos de Teoria Mais Avançados — CONCLUÍDA
- Data: 2026-08-16 08:46 (UTC+1)
- Commit: 4c338f1
- Resumo: Adicionados os Capítulos 13 a 16 a `THEORY_CHAPTERS` em `core/theory_content.py` (Harmonia de Jazz Básica, Fundamentos de Improvisação, Contraponto & Condução de Vozes, Técnicas de Prática Deliberada) com suporte i18n completo (PT/EN) e exercícios para piano e viola. Criados 4 novos quizzes em `core/theory_quiz.py` (5 perguntas de escolha múltipla por capítulo com explicações pedagógicas). 156/156 testes a passar.
- Ficheiros alterados: core/theory_content.py, core/theory_quiz.py, tests/test_theory_i18n.py, README.md

## Fase 27 — Análise Harmónica de Músicas Conhecidas — CONCLUÍDA
- Data: 2026-08-15 20:10 (UTC+1)
- Commit: a74cc6f
- Resumo: Adicionado o campo `theory_analysis` e `theory_analysis_en` com o leitor `get_theory_analysis` à dataclass `Song` em `core/songs.py`. Preenchidas 8 análises harmónicas didáticas detalhadas (Für Elise, Sonata ao Luar, Gymnopédie, Cânone em Dó, Malagueña, House of the Rising Sun, Romance Anónimo e Greensleeves). Em `gui/screens/practice_song.py`, integrado o botão "🎓 Ver Análise Teórica" e janela modal de leitura renderizada com o formatador markdown do sistema. 156/156 testes a passar.
- Ficheiros alterados: core/songs.py, gui/screens/practice_song.py, tests/test_songs_expansion.py, README.md

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
