# Revisão do Claude — Protocolo de Handoff

Este ficheiro é escrito pelo **Claude**, depois de analisar cada fase reportada em
`.agent-sync/GEMINI_STATUS.md`: corro a suite de testes, reviso o código alterado,
e arranco a app para confirmar que não há erros de runtime.

Cada entrada tem um veredito:
- **APROVADO** — nada a fazer, podes avançar para a fase seguinte.
- **AÇÃO NECESSÁRIA** — há itens concretos a corrigir antes de avançares. Lê a
  lista, corrige, faz commit, e atualiza o `GEMINI_STATUS.md` a confirmar.
- **TRABALHO PEDIDO** — não é correção de nada que já exista; é a especificação
  de funcionalidade nova a implementar a seguir. Trata como se fosse uma prompt
  normal do utilizador (clogomes), só que entregue por este ficheiro.

---

## TRABALHO PEDIDO — Fase 8 (Importador de Partituras MIDI) e Fase 9 (Notação Rítmica & Prática de Tempo Guiada)
- Pedido por: Claude, a pedido do utilizador (clogomes)
- Estado anterior: Fases 1-7 concluídas e aprovadas (ver histórico abaixo).
  64+ testes atuais devem continuar a passar.
- Regra geral: implementa uma fase de cada vez, corre
  `python3 -m unittest discover tests` no fim de cada uma, e atualiza o
  README.md no fim de CADA fase (não só no fim de tudo).

### FASE 8 — Importador de Partituras MIDI Próprias
O repertório atual tem peças de domínio público e algumas com direitos de autor
ativos que o utilizador decidiu manter, ciente do risco. Para dar uma alternativa
legal e útil que permita aprender QUALQUER música que o utilizador já possua:

- Cria `core/midi_importer.py` com um parser de ficheiros `.mid` simples e leve
  (sem dependências pesadas — o formato Standard MIDI File é bem documentado; um
  parser mínimo em Python puro lendo os bytes diretamente chega, só precisas de
  extrair eventos `note_on`/`note_off` de uma pista/canal escolhido).
- Função `import_midi_as_song(filepath, title, composer, difficulty) -> Song` que
  converte os eventos MIDI em `SongNote` (nota + duração em beats), usa
  `core/fingering.py` para sugerir dedilhação automaticamente, e
  `core/guitar.py` (`find_note_positions`) para sugerir a posição de corda/traste
  mais confortável (preferindo posições que minimizem saltos grandes entre notas
  consecutivas).
- No ecrã de Repertório (`practice_song.py`), acrescenta um botão "Importar
  Música (.mid)" que abre um file dialog (`tkinter.filedialog`), corre o
  importador, e guarda a música resultante para reutilização futura (persistida
  em disco — JSON próprio ou pasta `user_songs/`).
- Testa com um `.mid` gerado sinteticamente em `tests/test_midi_importer.py`
  (escreve os bytes MIDI mínimos à mão no teste, não precisas de ficheiro externo).

### FASE 9 — Notação Rítmica Real & Prática de Tempo Guiada
As músicas atuais têm `duration_beats` mas não têm fórmula de compasso nem
subdivisões visuais na pauta — a leitura rítmica fica incompleta. Também reparei
que `audio/metronome.py` só está ligado a `practice_song.py`, não a
`practice_instrument.py`.

- Adiciona `time_signature: str = "4/4"` ao dataclass `Song` em `core/songs.py`.
- Estende `gui/components/staff_canvas.py` para desenhar barras de compasso
  (barlines) a cada N tempos consoante o `time_signature`, quando estiver a
  mostrar uma `Song` completa (não só uma nota isolada).
- Liga o `Metronome` também a `gui/screens/practice_instrument.py`. Ao praticar
  uma música com o instrumento real (microfone), o metrónomo deve marcar o tempo
  e o feedback de acerto deve considerar também se a nota foi tocada dentro da
  janela rítmica esperada, reaproveitando `evaluate_rhythm_accuracy` já existente
  em `audio/metronome.py`.
- Implementa "rampa de tempo automática": em `practice_song.py` e
  `practice_instrument.py`, uma opção que começa a 70% do BPM da música e aumenta
  ~5% a cada repetição bem sucedida (sem erros) até atingir o BPM alvo — a
  técnica de prática lenta-para-rápido usada por professores reais.

No fim de cada fase, atualiza o `README.md` (funcionalidades + árvore de
ficheiros) e não remove nem simplifica nenhuma funcionalidade já existente.

---

## Revisão — Correção do Modo Adaptativo & 5ª categoria no gráfico
- Commit revisto: `d55815b`
- Testes: 69/69 OK
- App: arranca sem erros (testado com `python3 main.py`, 6s, sem exceções)
- **Veredito: APROVADO**

Verificado especificamente:
- `practice_ear.py` e `practice_staff.py` importam e chamam `generate_adaptive_question()`
  de `core/adaptive_engine.py`, com o toggle "🧠 Modo Adaptativo" visível na UI.
- `practice_staff.py` valida `q_cand.staff_note` antes de aceitar a pergunta adaptativa,
  com fallback seguro para `generate_staff_reading_question()` — boa prática defensiva,
  não pedida explicitamente mas bem-vinda.
- `stats_screen.py` mostra agora as 5 categorias (incluindo `pratica_instrumento`) no
  gráfico de barras horizontais, consistente com `get_weak_areas()`.

Nada a corrigir nesta fase. Podes avançar para a próxima fase quando o utilizador
(clogomes) pedir.
