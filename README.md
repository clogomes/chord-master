# 🎵 ChordMaster

> **ChordMaster** é uma aplicação desktop moderna e interativa para o ensino de **Teoria Musical**, **Treino Auditivo** e **Leitura de Pauta Musical**, desenvolvida em Python com **CustomTkinter**, suporte **Multi-Utilizador**, acompanhamento de progresso de lições e síntese sonora harmónica local.

---

## ✨ Funcionalidades Principais

### 1. 👥 Perfis Multi-Utilizador & Progresso Individual
- Criação e gestão de múltiplos perfis de estudante com escolha de **Avatares** personalizados (🎵, 🎹, 🎸, 🎻, 🎧, 🎷, 🎺, 🥁, 🌟).
- **Troca Rápida de Perfil**: Alternância instantânea de utilizador através da sidebar ou menu superior.
- **Progresso de Lições**: Cada utilizador acompanha e marca as lições teóricas que já estudou e concluiu (com percentagem e barra de progresso).
- **Tabela de Estudantes (Leaderboard)**: Painel comparativo de pontuações, sequências de acerto (*streaks*) e lições concluídas entre todos os estudantes locais.
- Persistência estruturada em ficheiro `user_profiles.json`.

### 2. 📖 Módulo de Teoria Musical Interativo
- **Notas & Acidentes**: Visualização de notas na notação anglo-saxónica (`C, D, E...`) e Solfejo português (`Dó, Ré, Mi...`), acidentes (sustenidos ♯ / bemóis ♭), frequências em Hz e números MIDI.
- **Intervalos Musicais**: Tabela completa de intervalos (de 2ª Menor a Oitava Justa), cálculo de semitons, mnemónicas de canções famosas e audição melódica/harmónica.
- **Escalas & Modos**: Gerador de escalas Maiores, Menores (Natural, Harmónica e Melódica), Pentatónicas e Modos Gregos com visualização na pauta e no piano.
- **Formação de Acordes**: Tríades (Maiores, Menores, Diminutas, Aumentadas, Suspensas) e Tétrades (7, maj7, m7, m7b5, dim7) com reprodução de acordes em bloco e arpejos.
- **Marcação de Lição Concluída**: Botão interativo no final de cada separador para registar a aprendizagem no perfil ativo.

### 3. 🎧 Treino Auditivo (Ear Training)
- Identificação de **Intervalos Melódicos** (ascendentes/descendentes) e **Harmónicos** (notas tocadas em simultâneo).
- Identificação de **Qualidade de Acordes** (Maior, Menor, Diminuto, Aumentado, Sétimas).
- Modos de dificuldade: **Iniciante**, **Intermédio** e **Avançado**.
- Controlos de repetição de áudio ("Ouvir Novamente" e "Tocar Lento").

### 4. 🎼 Leitura de Pauta Musical (Sight Reading)
- Exercícios nas **Claves de Sol (𝄞)** e **Clave de Fá (𝄢)**.
- Renderizador vetorial de alta precisão com linhas da pauta, linhas suplementares superiores/inferiores, cabeças de nota e acidentes.
- Opção para ativar/desativar acidentes (sustenidos e bemóis).
- Resposta através de botões rápidos ou clicando diretamente nas teclas do teclado de piano interativo.

### 5. 📊 Sistema de Feedback & Estatísticas
- Feedback visual imediato com badges de Acerto/Erro e explicações teóricas detalhadas.
- Contador de sequência de acertos (**Streaks 🔥**).
- Gráficos de barras de progresso e taxas de precisão percentual (%) por categoria para cada utilizador.

---

## 🏗️ Estrutura Modular do Projeto

```text
chord-master/
├── main.py                         # Ponto de entrada da aplicação (com auto-detecção de Tk moderno)
├── requirements.txt                # Dependências externas (customtkinter, numpy, pygame)
├── README.md                       # Documentação do projeto
├── user_profiles.json              # Perfis, progresso e histórico dos utilizadores
│
├── core/                           # Lógica Teórica e Regras de Negócio (Pure Python)
│   ├── __init__.py
│   ├── notes.py                    # Classes de notas, frequências (A4=440Hz), MIDI e notação
│   ├── intervals.py                # Intervalos, semitons, mnemónicas e transposição
│   ├── scales.py                   # Fórmulas de escalas e modos
│   ├── chords.py                   # Fórmulas de acordes, tríades, tétrades e inversões
│   ├── quiz_engine.py              # Motor de geração de desafios e validação
│   ├── score_tracker.py            # Gestão de estatísticas e métricas
│   └── user_manager.py             # Gestor multi-utilizador, perfis e lições concluídas
│
├── audio/                          # Síntese Sonora e Reprodução Local
│   ├── __init__.py
│   ├── synthesizer.py              # Síntese harmónica aditiva com envelope ADSR suave
│   └── player.py                   # Reprodução assíncrona não bloqueante (threads + mixer)
│
├── gui/                            # Interface Gráfica com CustomTkinter
│   ├── __init__.py
│   ├── app.py                      # Janela principal, sidebar com cartão de perfil e router
│   ├── components/                 # Componentes visuais reutilizáveis
│   │   ├── __init__.py
│   │   ├── piano_keyboard.py       # Teclado de piano interativo de 2 oitavas
│   │   ├── staff_canvas.py         # Desenho vetorial da pauta musical (Claves de Sol e Fá)
│   │   ├── score_card.py           # Cartão de feedback imediato e streaks
│   │   └── user_modal.py           # Diálogo modal de criação e troca de perfis
│   └── screens/                    # Ecrãs da aplicação
│       ├── __init__.py
│       ├── main_menu.py            # Menu principal personalizado por utilizador
│       ├── theory_screen.py        # Lições de teoria com acompanhamento de progresso
│       ├── practice_ear.py         # Treino auditivo
│       ├── practice_staff.py       # Exercícios de leitura de pauta
│       └── stats_screen.py         # Painel de estatísticas individuais e tabela de estudantes
│
└── tests/                          # Testes Unitários Automatizados (34 testes com 100% sucesso)
    ├── __init__.py
    ├── test_notes.py               # Testes de notas, frequências e conversões
    ├── test_intervals.py           # Testes de intervalos e transposição
    ├── test_scales.py              # Testes de fórmulas de escalas
    ├── test_chords.py              # Testes de acordes e inversões
    ├── test_quiz.py                # Testes do motor de quiz
    └── test_users.py               # Testes de perfis multi-utilizador e progresso
```

---

## 🚀 Instalação e Execução

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Executar a Aplicação
```bash
python3 main.py
```

---

## 🧪 Execução dos Testes Unitários

```bash
python3 -m unittest discover tests
```
