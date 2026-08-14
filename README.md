# 🎵 ChordMaster — Estúdio Interativo de Teoria & Prática Musical

> **ChordMaster** é uma aplicação desktop moderna, completa e profissional para a aprendizagem de **Teoria Musical**, **Piano**, **Viola / Guitarra**, **Treino Auditivo & Solfejo Cantado**, **Leitura de Pauta**, **Afinador / Lamiré** e **Repertório Interativo**. 
> Desenvolvida em Python com **CustomTkinter**, motor de síntese sonora harmónica ADSR, deteção de afinação por microfone em tempo real, suporte a **Teclados MIDI USB**, sistema **Multi-Utilizador**, **Gamificação com Níveis e Medalhas**, e **Exportação de Progresso**.

---

## 🌟 Destaques & Funcionalidades Principais

### 1. 👥 Perfis Multi-Utilizador & Gestão de Estudantes
- **Múltiplos Alunos no Mesmo Computador**: Criação, edição e remoção de perfis de estudantes com escolha de avatares expressivos (🎵, 🎹, 🎸, 🎼, 🎻, 🎺, 🎷, 🥁, 🎧, 🌟, ⚡, 🔥).
- **Acompanhamento Individual de Progresso**: Cada aluno possui histórico independente de exercícios, sequências de acertos (*streaks*), taxa de precisão global, lições teóricas concluídas e pontos de experiência (**XP**).
- **Troca Instantânea de Aluno**: Acesso rápido a qualquer momento através do cartão de perfil na barra lateral ou no menu superior.
- **Botão de Reinício de Progresso (Reset)**: Opção de recomeçar a aprendizagem do zero a qualquer momento, com caixa de confirmação de segurança.
- **Tabela Geral de Classificação (*Leaderboard*)**: Ranking de estudantes ordenado por XP, lições concluídas e precisão global.

---

### 2. 🏆 Sistema Completo de Gamificação (XP, Níveis & Conquistas)
- **Pontos de Experiência (XP)**:
  - **$+100\text{ XP}$** por cada capítulo de teoria concluído.
  - **$+15\text{ XP}$** por cada exercício acertado (+ bónus por sequências *streaks*).
  - **$+50\text{ a }+100\text{ XP}$** por cada música tocada no repertório.
  - **$+25\text{ XP}$** por exercícios de afinação e prática com instrumento acústico real.
- **7 Níveis de Maestria Musical**:
  1. 🌱 **Nível 1:** *Iniciante Curioso* (0 - 149 XP)
  2. 🎼 **Nível 2:** *Aprendiz de Pauta* (150 - 399 XP)
  3. 🎹 **Nível 3:** *Mestre dos Intervalos* (400 - 799 XP)
  4. 🎸 **Nível 4:** *Harmonista Prático* (800 - 1399 XP)
  5. 🌟 **Nível 5:** *Virtuoso em Palco* (1400 - 2199 XP)
  6. 👑 **Nível 6:** *Mestre Compositor* (2200 - 3199 XP)
  7. 🏆 **Nível 7:** *Lenda da Música* (3200+ XP)
- **Vitrine de 12 Medalhas & Conquistas Desbloqueáveis**:
  - 🥇 *Primeiro Passo*, 📖 *Académico da Teoria*, 🎓 *Mestre da Teoria*, 🎵 *Primeira Canção*, 🎹 *Virtuoso das Teclas*, 🎸 *Mestre das 6 Cordas*, 🎧 *Ouvido Apurado*, 🎼 *Leitor de Pauta Ágil*, 🎙️ *Afinação Impecável*, 🔥 *Em Chamas!*, ⭐ *Estudante Dedicado* e ⏱️ *Mestre do Tempo*.

---

### 3. 📖 Academia Completa de Teoria Musical (8 Capítulos com Áudio & Visualizadores Sincronizados)
Um curso completo de harmonia e teoria desde os conceitos fundamentais até técnicas avançadas, com sincronização em tempo real entre **Pauta Musical**, **Teclado de Piano** e **Braço de Viola (15 Trastes)**:
- **Capítulo 1 — Fundamentos & Notação**: Som, altura, notação internacional (`C, D, E...`), Solfejo português (`Dó, Ré, Mi...`), acidentes (♯ / ♭), oitavas científicas e claves.
- **Capítulo 2 — Intervalos Musicais & Física Harmónica**: Frequências em Hz, semitons, classificação de intervalos (2ªm a 8ªJ), consonâncias/dissonâncias e mnemónicas de músicas conhecidas.
- **Capítulo 3 — Escalas, Círculo de 5ªs & Modos Gregos**: Estruturas de Escala Maior, Menores (Natural, Harmónica e Melódica), Pentatónicas e os 7 Modos Gregos (Jónio, Dórico, Frígio, Lídio, Mixolídio, Eólio e Lócrio).
- **Capítulo 4 — Formação de Acordes & Tríades**: Como empilhar terças para construir tríades Maiores, Menores, Diminutas, Aumentadas e Suspensas ($Sus2, Sus4$), com inversões (Estado Fundamental, 1ª e 2ª Inversão).
- **Capítulo 5 — Campo Harmónico & Tétrades**: Harmonização da escala maior, graus harmónicos ($I, ii, iii, IV, V, vi, vii^\circ$) e acordes de quatro notas ($Maj7, 7, m7, m7\flat5, dim7$).
- **Capítulo 6 — Harmonia Avançada & Modulação**: Funções tonais (Tónica, Subdominante, Dominante), cadências harmónicas ($II\text{-}V\text{-}I, IV\text{-}V\text{-}I$), dominantes secundários, empréstimo modal e modulação.
- **Capítulo 7 — Guia Prático de Piano**: Técnica de dedilhação (Dedos 1 a 5 para mão direita e esquerda), postura, passagem de polegar e mapas de dedilhação para escalas e acordes.
- **Capítulo 8 — Guia Prático de Viola / Guitarra (Sistema CAGED)**: Afinação padrão das 6 cordas ($E2, A2, D3, G3, B3, E4$), sistema CAGED para mapear qualquer acorde ao longo do braço, e biblioteca interativa de formas de acordes.
- **Acompanhamento de Lição Concluída**: Botão interativo para registar a lição como concluída/estudada no perfil ativo.

---

### 4. 🎶 Estúdio de Repertório & Tocar Peças (16 Músicas Completas)
Estúdio de execução interativa com pauta iluminada, teclas destacadas com número de dedo e posição de corda/traste, contendo as **16 músicas completas na íntegra** (clássicos, cancioneiro tradicional e temas lendários de rock acústico):
- **16 Peças do Repertório Clássico, Tradicional & Rock**:
  1. *Hino à Alegria* (Ludwig van Beethoven — 9ª Sinfonia Completa: Frase A + A' + Ponte B + Conclusão)
  2. *Brilha, Brilha Estrelinha* (W. A. Mozart / Tradicional — Forma Ternária Completa A-B-A)
  3. *Papagaio Loiro* (Folclore Português — 3 Estrofes e Refrão Tradicional Integral)
  4. *Pombinha Branca* (Cancioneiro Tradicional Português — Versão Integral de 4 Frases)
  5. *Für Elise* (L. van Beethoven — Bagatela WoO 59: Motivo Cromático, Arpejos Am/E e Cadência)
  6. *Minueto em Sol Maior* (J. S. Bach / Petzold — BWV Anh. 114: Seção A Completa de 16 Compassos)
  7. *Marcha Nupcial* (Richard Wagner — Lohengrin: Tema Coral e Frase Central Solene)
  8. *Canon em Dó / Ré* (Johann Pachelbel — Tema Principal e Variação em Colcheias)
  9. *Eine kleine Nachtmusik* (W. A. Mozart — Serenata K. 525: Allegro Completo com Resolução)
  10. *Greensleeves* (Melodia Renascentista Inglesa — Verso e Refrão Tradicional Completo)
  11. *O Cravo e a Rosa* (Cantiga Tradicional Lusófona — 4 Estrofes Integrais)
  12. *Grândola, Vila Morena* (José Afonso / Zeca Afonso — Hino Completo com Estrofes e Cadência)
  13. *Stairway to Heaven* (Led Zeppelin — Introdução Acústica Dedilhada em Lá Menor)
  14. *Nothing Else Matters* (Metallica — Introdução Clássica em Cordas Soltas de Mi Menor)
  15. *Enter Sandman* (Metallica — Riff Principal em Mi Menor)
  16. *Smoke on the Water* (Deep Purple — O Riff Lendário em Sol Menor)
- **3 Métodos Flexíveis de Execução**:
  - **Teclado do Computador**: Mapeamento QWERTY ergonómico no Piano (`A..L` para notas brancas Dó4 a Mi5; `W..P` para notas pretas) e cordas da Viola (`1..6`).
  - **Teclados MIDI USB**: Deteção automática *Plug-and-Play* de pianos digitais e sintetizadores USB físicos.
  - **Cliques no Ecrã**: Tocar diretamente no teclado de piano ou no braço da viola virtual.
- **Metrónomo Acústico & Modo Desafio Rítmico**:
  - Metrónomo sonoro integrado com sons de *woodblock* sintetizados (clique agudo no primeiro tempo e suave nos restantes).
  - Slider de andamento (40 a 180 BPM) com ajuste em tempo real.
  - Avaliação de precisão de tempo em milissegundos (*PERFEITO ⭐*, *BOM 👍*, *FORA DE TEMPO ⚠️*).
  - Sistema de combos consecutivos ($1\times, 2\times, 3\times, 4\times$) que multiplicam a pontuação e o ganho de XP!
- **Modo Demonstração Sonora**: Reprodução automática nota a nota para ouvir a peça antes de praticar.

---

### 5. 🎤 FASE 5 — Ditado de Solfejo Cantado com Validação Vocal por Microfone
- **Nova Categoria de Exercício (`QuestionType.SOLFEGE_SING`)**:
  - O motor de quiz pede uma nota em solfejo (ex: *"Canta a nota Sol (G4)"*, *"Entoa a nota Mi (E4) usando a tua voz"*).
  - Botão **«🔊 Ouvir Tom de Referência»** para dar ao aluno uma base auditiva sólida (Dó Central 261.6 Hz ou nota tónica).
  - **Validação Vocal ao Vivo com `PitchListener`**:
    - O aluno clica em **«🎙️ Ativar Microfone & Cantar»** e entoa a nota vocalmente.
    - Mostrador em tempo real com nome da nota cantada, frequência em Hz e desvio em cents.
    - Ao sustentar a nota pedida afinada ($\pm 40\text{ cents}$) durante 0.35s, o exercício valida automaticamente o acerto com som comemorativo, bónus de XP e explicação detalhada!
    - Fallback com botões de opções disponível para situações sem microfone.

---

### 6. 🧠 FASE 6 — Motor de Prática Adaptativa & Deteção de Pontos Fracos ([`core/adaptive_engine.py`](file:///Users/clogomes/repo/chord-master/core/adaptive_engine.py))
- **Análise Inteligente do Histórico de Exercícios**:
  - Analisa as últimas 50 tentativas do perfil do aluno em `user.history` com decaimento exponencial de recência (os erros recentes têm maior peso).
  - Identifica automaticamente as áreas de maior dificuldade (*pontos fracos*) entre Treino Auditivo, Leitura de Pauta, Teoria, Repertório e Instrumento.
- **Cartão Personalizado no Dashboard Inicial**:
  - Exibe no topo do menu principal o cartão **«🎯 Recomendado para ti hoje: [Categoria Mais Fraca]»** com explicação do motivo da recomendação e botão direto **«Praticar Agora →»**.
- **Geração de Desafios Adaptativos**:
  - 60% de probabilidade de direcionar exercícios para as áreas com menor taxa de acerto e 40% de exploração equilibrada.

---

### 7. 📈 FASE 7 — Painel de Análise de Progresso com Gráficos em Canvas ([`gui/screens/stats_screen.py`](file:///Users/clogomes/repo/chord-master/gui/screens/stats_screen.py))
- **Gráfico de Linha de Tendência de Precisão (Últimas 4 Semanas)**:
  - Renderizado nativamente em `tk.Canvas` com interpolação suave, eixos graduados de $0\%$ a $100\%$, linhas de grelha subtis e pontos com halo que destacam a percentagem de cada semana.
- **Gráfico de Barras Horizontais de Comparação entre Categorias**:
  - Comparação lado a lado do aproveitamento em Treino Auditivo, Leitura de Pauta, Teoria Musical e Repertório, facilitando a identificação imediata de onde o aluno precisa focar o estudo.
- **Calendário de Atividade Estilo GitHub (~90 Dias)**:
  - Grelha de consistência de 14 semanas ($14 \times 7$ dias) com escala de intensidade em esmeralda (*Dark Slate* a *Vibrant Emerald* `#34D399`), marcadores de meses e dias da semana, e contador de dias ativos.

---

### 8. 🎙️ Lamiré & Afinador Cromático de Alta Precisão
- **Deteção de Frequência Fundamental ($f_0$) via Microfone**: Algoritmo de autocorrelação no domínio do tempo acelerado por FFT, com interpolação parabólica para precisão sub-amostra e rejeição inteligente de ruído ambiente (60 Hz a 1200 Hz).
- **Mostrador Visual com Agulha Dinâmica**: Medidor de $-50$ a $+50$ cents com faixa de tolerância verde ($\pm 10$ cents) e orientações em tempo real (*"▲ Muito Grave — Estica a corda"*, *"▼ Muito Agudo — Afrouxa a corda"*, *"✓ AFINADO (No Ponto Perfeito!)"*).
- **Afinador de Viola (6 Cordas)**: Cartões visuais para as 6 cordas padrão ($E2, A2, D3, G3, B3, E4$) que se iluminam automaticamente ao detetar a corda tocada, com botão para ouvir o tom de cada corda.
- **Gerador de Diapasão / Lamiré de Referência**: Botão de reprodução imediata do **Lá Central padrão internacional (A4 - 440 Hz)** e teclado de 12 tons cromáticos de referência para treino de afinação de ouvido.

---

### 9. 🎯 Prática com Instrumento Acústico Real
- Prática de escalas, arpejos e repertório utilizando o teu **piano acústico** ou **viola/guitarra física**.
- A aplicação "escuta" através do microfone, valida a nota e o desvio em cents, exigindo uma sustentação de 300 ms afinada antes de avançar automaticamente para a nota seguinte.

---

### 10. 🎧 Treino Auditivo & Leitura de Pauta
- **Treino Auditivo (Ear Training)**:
  - Identificação de **Intervalos Melódicos** (ascendentes/descendentes) e **Harmónicos** (duas notas em simultâneo).
  - Identificação de **Qualidade de Acordes** (Maiores, Menores, Diminutos, Aumentados, Sétimas).
  - Ditado de Solfejo Cantado com voz e microfone.
  - Níveis de dificuldade: *Iniciante*, *Intermédio* e *Avançado*.
- **Leitura de Pauta Musical (Sight Reading)**:
  - Exercícios nas **Claves de Sol (𝄞)** e **Clave de Fá (𝄢)**.
  - Renderizador vetorial de alta definição com linhas da pauta, linhas suplementares superiores/inferiores, cabeças de nota e acidentes (♯ / ♭).
  - Resposta por botões rápidos ou clicando diretamente no teclado de piano interativo.

---

### 11. 📥 Exportação de Progresso & Certificado de Estudo
- Botão **«📥 Exportar Progresso»** no ecrã de Estatísticas:
  - Gera um relatório formatado em Markdown (`relatorio_progresso_<aluno>.md`) pronto a imprimir ou partilhar.
  - Inclui data de emissão, nível e título de maestria, XP total, estado das 8 lições de teoria, métricas de precisão por categoria e lista de todas as medalhas e conquistas alcançadas.

---

### 12. 🎨 Design System & Interface Moderna ([`gui/theme.py`](file:///Users/clogomes/repo/chord-master/gui/theme.py))
- **Paleta de Cores Harmoniosa**: Base moderna em tons de ardósia escura (*Slate-950* `#0B0F19`, *Slate-900* `#111827`, *Slate-800* `#1F2937`), com destaques em *Royal Indigo* (`#4F46E5`), *Emerald* (`#10B981`), *Sky Blue* (`#0284C7`), *Amber* (`#F59E0B`) e *Crimson* (`#EF4444`).
- **Tipografia Otimizada e Legível**: Escala com mínimo de $14\text{px}$ para textos de corpo e $28\text{--}32\text{px}$ para títulos principais, garantindo máxima legibilidade.
- **Proteção de Threads & Rate-Limiting**: Processamento assíncrono seguro com limitação de taxa de atualização gráfica (15 FPS), evitando travamentos ou sobrecarga da GUI.

---

## 🏗️ Arquitetura do Código

```text
chord-master/
├── main.py                         # Ponto de entrada da aplicação (arranque com Tkinter moderno)
├── requirements.txt                # Dependências externas (customtkinter, numpy, pygame, sounddevice)
├── README.md                       # Documentação técnica exaustiva
├── user_profiles.json              # Perfis, progresso de lições, XP e histórico dos utilizadores
│
├── core/                           # Lógica Musical Pura & Regras de Negócio (Sem dependência de GUI)
│   ├── __init__.py
│   ├── notes.py                    # Classes de Notas, Frequências em Hz, MIDI, Solfejo e Acidentes
│   ├── intervals.py                # Intervalos musicais, Semitons, Mnemónicas e Transposição
│   ├── scales.py                   # Fórmulas de Escalas Maiores, Menores, Pentatónicas e Modos Gregos
│   ├── chords.py                   # Formação de Tríades, Tétrades e Inversões de Acordes
│   ├── fingering.py                # Mapeamento de Dedilhações para Piano (Mão Direita e Esquerda)
│   ├── guitar.py                   # Mapeamento de Braço de Viola (CAGED, 15 Trastes, Afinações)
│   ├── songs.py                    # Biblioteca de 16 Músicas Completas com notas, dedilhações e tablaturas
│   ├── gamification.py             # Sistema de Gamificação (XP, 7 Níveis, 12 Conquistas/Medalhas)
│   ├── exporter.py                 # Exportador de Relatórios de Progresso e Certificados em Markdown
│   ├── adaptive_engine.py          # Motor de Prática Adaptativa & Identificação de Pontos Fracos
│   ├── quiz_engine.py              # Motor de Geração de Questões (Intervalos, Acordes, Pauta, Solfejo Cantado)
│   ├── score_tracker.py            # Gestor de Pontuações e Métricas
│   └── user_manager.py             # Gestor Multi-Utilizador, Persistência e Progressão
│
├── audio/                          # Motores de Síntese Sonora, Microfone e MIDI
│   ├── __init__.py
│   ├── synthesizer.py              # Síntese Harmónica Aditiva com Envelope ADSR
│   ├── player.py                   # Reprodução Sonora Assíncrona Thread-Safe (Pygame Mixer)
│   ├── pitch_listener.py           # Captura de Microfone e Deteção de Afinação por Autocorrelação FFT
│   ├── metronome.py                # Metrónomo Acústico Thread-Safe e Avaliador de Precisão Rítmica
│   └── midi_manager.py             # Gestor de Teclados MIDI USB Hardware (Plug-and-Play)
│
├── gui/                            # Interface Gráfica com CustomTkinter
│   ├── __init__.py
│   ├── app.py                      # Janela Principal, Barra Lateral com Perfil de Aluno e Router
│   ├── theme.py                    # Sistema Centralizado de Tokens de Design (Cores, Tipografia, Raios)
│   ├── components/                 # Componentes Visuais Reutilizáveis
│   │   ├── __init__.py
│   │   ├── piano_keyboard.py       # Teclado de Piano Interativo de 2 Oitavas com Dedilhação
│   │   ├── guitar_fretboard.py     # Braço de Viola Interativo de 15 Trastes (CAGED)
│   │   ├── staff_canvas.py         # Desenho Vetorial de Pauta Musical (Claves de Sol e Fá)
│   │   ├── score_card.py           # Cartão de Feedback Imediato, Streaks e XP
│   │   └── user_modal.py           # Diálogo Modal de Gestão e Criação de Alunos
│   └── screens/                    # Ecrãs Principais da Aplicação
│       ├── __init__.py
│       ├── main_menu.py            # Dashboard Inicial com Nível de XP, Progresso e Acessos Rápidos
│       ├── theory_screen.py        # Academia de Teoria (8 Capítulos com Piano e Viola Sincronizados)
│       ├── practice_song.py        # Estúdio de Repertório (16 Músicas Completas, Metrónomo e Suporte a MIDI)
│       ├── tuner_screen.py         # Lamiré & Afinador Cromático com Agulha e Deteção por Microfone
│       ├── practice_instrument.py  # Treino Acústico com Microfone para Piano e Viola Físicos
│       ├── practice_ear.py         # Treino Auditivo & Ditado de Solfejo Cantado com Microfone
│       ├── practice_staff.py       # Exercícios de Leitura de Pauta
│       └── stats_screen.py         # Painel de Estatísticas, Conquistas, Leaderboard e Exportação
│
└── tests/                          # 68 Testes Unitários Automatizados (100% de Sucesso)
    ├── __init__.py
    ├── test_notes.py               # Testes de notas, frequências e conversões MIDI
    ├── test_intervals.py           # Testes de intervalos e transposição
    ├── test_scales.py              # Testes de fórmulas de escalas e modos
    ├── test_chords.py              # Testes de acordes, tríades e inversões
    ├── test_fingering.py           # Testes de regras de dedilhação no piano
    ├── test_guitar.py              # Testes de afinações, trastes e sistema CAGED
    ├── test_songs.py               # Testes de integridade das 16 peças completas de repertório
    ├── test_pitch.py               # Testes de deteção de pitch por autocorrelação e rejeição de ruído
    ├── test_metronome.py           # Testes de temporização do metrônomo e avaliação rítmica
    ├── test_gamification.py        # Testes de níveis de XP, cálculo de progresso e medalhas
    ├── test_exporter.py            # Testes de exportação de relatórios Markdown
    ├── test_adaptive.py            # Testes do motor adaptativo e decaimento de recência
    ├── test_theme.py               # Testes de tokens de cores e tipografia
    ├── test_quiz.py                # Testes do motor de perguntas, solfejo cantado e streaks
    └── test_users.py               # Testes de perfis multi-utilizador e persistência
```

---

## 🚀 Instalação & Execução

### 1. Pré-requisitos
- Python 3.10 ou superior instalado.
- Sistema Operativo: macOS, Linux ou Windows.

### 2. Clonar o Repositório
```bash
git clone https://github.com/clogomes/chord-master.git
cd chord-master
```

### 3. Criar Ambiente Virtual e Instalar Dependências
```bash
# Criar ambiente virtual
python3 -m venv .venv

# Ativar ambiente virtual
# No macOS/Linux:
source .venv/bin/activate
# No Windows:
# .venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 4. Executar a Aplicação
```bash
python3 main.py
```

---

## 🧪 Execução da Suíte de Testes Automatizados

A aplicação inclui **64 testes unitários** que cobrem toda a lógica musical, motores de áudio, ditado de solfejo cantado, gamificação, gestão de utilizadores e integridade das peças de repertório:

```bash
# Executar todos os 64 testes com detalhes
python3 -m unittest discover -v tests
```

---

## 📄 Licença & Autoria

- **Projeto:** ChordMaster
- **Conta / Repositório:** [`clogomes@gmail.com`](https://github.com/clogomes/chord-master)
- **Tecnologias:** Python 3, CustomTkinter, NumPy, Pygame, SoundDevice.
- **Licença:** MIT License (Código aberto para estudo e prática musical).
