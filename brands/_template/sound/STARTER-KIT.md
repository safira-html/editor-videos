# Kit básico de som para uma marca nova

O que uma marca precisa ter em `brands/<marca>/sound/` para sonorizar um anúncio com apresentador
como os aprovados (hierarquia A/B/C de [docs/05-som.md](../../../docs/05-som.md)). Os prompts abaixo
são **verbatim** os que geraram os sons das marcas reais (ver `brands/*/sound/SONS.md`).

> 💸 **Gerar custa crédito (ElevenLabs).** Antes de qualquer geração: `estimate_only: true` (grátis),
> diga **o que** vai gerar e **quanto** custa, lembre que o conector **não mostra o saldo** (a pessoa
> vê em elevenlabs.io) e **espere o sim**. Ver [docs/05-som.md §6](../../../docs/05-som.md).
> Marca nova que quer só o essencial pode começar sem trilha própria (o anúncio sai com efeitos) ou
> copiar efeitos genéricos de outra marca do repositório (impact, tap, tick, downer) — sem custo.

## Efeitos (modelo `eleven_text_to_sound_v2`) — 50 cr por variação, 2 variações cada

Pedir **2 variações** de cada: em 2026-09-24/25, 4 de 20 efeitos vieram **mudos** numa das
variações (toque de tela com pico −66 dB; obturador; ambiência noturna). Duas variações e `inspect`
protegem o gasto. Limite do prompt: **450 caracteres**, termine com `dry, no music`; a duração vai
**no texto**, não como parâmetro.

| som | nível | para que serve | prompt (verbatim) | custo |
|---|---|---|---|---|
| **impact** | A / B | o maior som do vídeo (momento A, uma vez só); impact macio no gancho | `Soft cinematic impact with a deep sub bass thump, tight punchy transient, short tail under one second, modern clean advertising sound, 2 seconds, dry, no music.` | 2 × 50 cr |
| **riser** | A | sobe 1,4s antes do impact | *(sem prompt verbatim: o riser das marcas reais veio de uma biblioteca institucional anterior)*. Sugestão ainda **não testada**: `Short tension riser, a clean upward sweep of filtered noise and synth that builds for one second and stops abruptly, modern advertising sound, 2 seconds, dry, no music.` | 2 × 50 cr |
| **tick** | C | matéria-prima da cama de tic-tac (`./ev tick`), urgência de prazo | `Mechanical clock ticking, steady tick-tock, two ticks per second, close mic, crisp and clean, 4 seconds, dry, no music.` — sai 1 tick só ou 1/s; a cama é montada por script a partir de **um** tick | 2 × 50 cr |
| **tap** | B | CTA com ação literal ("toque no botão") | `Single smartphone screen tap, crisp UI button click, very short and clean, close mic, 1 second, dry, no music.` — o aprovado tem **dois toques** (use `offset 0.22`, `length 0.15`) | 2 × 50 cr |
| **downer** | B | "acabou o tempo" / "está fora" | `Short low thud followed by a quick downward pitch drop, like a timer running out, clean and modern, serious not comedic, 1.5 seconds, dry, no music.` | 2 × 50 cr |
| **ding** | C | recompensa pequena ("ganhou um número da sorte") | *(sem prompt verbatim das marcas reais.)* O mais próximo, verbatim, é o chime de conquista da Allevo Tech: `Bright positive achievement chime, a short two-note rising digital notification like unlocking a badge or earning a certificate in an app, clean, satisfying, modern UI, 1 second, dry, no music.` | 2 × 50 cr |
| **whoosh** | A | virada problema → solução, junto do impact | `Short clean modern whoosh transition, airy swipe that rises then resolves, smooth and bright, tech advertising feel, no impact at the end, 1 second, dry, no music.` | 2 × 50 cr |

**Kit completo = 7 efeitos × 2 variações × 50 cr = 700 cr.** Kit mínimo (impact, tap, tick, downer) =
400 cr. Efeitos específicos da narrativa (teclado, moedas, videochamada, cachorro…) entram só quando
o roteiro pede — veja os prompts em `brands/allevo-tech/sound/SONS.md` e
`brands/quero-card/sound/SONS.md`.

## Trilha (modelo `eleven_music_v2`) — 1.641,41 cr por variação

Uma peça **contínua** por anúncio (~30–45s), a mesma em todos os anúncios da campanha.

### Molde do prompt

```
{DURAÇÃO} seconds. {ADJETIVOS DE HUMOR} instrumental bed for a Brazilian social-media ad about {ASSUNTO}.
{BPM} BPM, {GÊNERO}: {PALETA DE INSTRUMENTOS}. {ARCO EMOCIONAL}.
Starts immediately with the beat, no intro. {Lifts to / Builds gently, } full energy at {N} seconds.
Ends at {FIM} seconds on one clean final hit, then silence.
Leaves room for a voiceover: no drops, no big fills, no lead melody. Instrumental only, no vocals.
```

As três frases finais (sem intro · hit final · espaço para a voz) **não mudam**: são o que faz a
trilha servir de fundo de fala.

### Os três exemplos reais (verbatim)

**126 BPM — urgência de prazo** (Clube da Virada, aprovada):
> 31 seconds. Energetic, urgent instrumental bed for a Brazilian social-media ad about a cash prize draw with a closing deadline. 126 BPM, bright pop-electronic: driving four-on-the-floor kick, tight claps, ticking 16th-note hi-hats, punchy bass, plucked synth and staccato strings, confident and optimistic, countdown feel. Starts immediately with the beat, no intro. Lifts to full energy at 17 seconds. Ends at 30 seconds on one clean final hit, then silence. Leaves room for a voiceover: no drops, no big fills, no lead melody. Instrumental only, no vocals.

**112 BPM — tecnologia / carreira** (Allevo Tech):
> 45 seconds. Modern tech instrumental bed for a Brazilian social-media ad about a hands-on data analyst course for people changing careers. 112 BPM, clean electronic pop: tight kick, crisp claps, muted synth plucks, soft arpeggiated synth, warm sub bass, subtle digital textures. Curious and a little restless at the start, then steadily builds into a confident, optimistic groove with a clear sense of progress and forward motion. Starts immediately with the beat, no intro. Full energy at 15 seconds. Ends at 40 seconds on one clean final hit, then silence. Leaves room for a voiceover: no drops, no big fills, no lead melody. Instrumental only, no vocals.

**100 BPM — cuidado, acolhimento** (Quero Card):
> 45 seconds. Warm, caring, optimistic instrumental bed for a Brazilian social-media ad about an affordable health benefits card for the whole family. 100 BPM, light acoustic pop: soft kick, finger snaps, muted acoustic guitar and ukulele plucks, gentle piano chords, warm round bass. Feels human, reassuring, everyday family life, a sense of relief. Starts immediately with the groove, no intro. Builds gently, full at 15 seconds. Ends at 40 seconds on one clean final hit, then silence. Leaves room for a voiceover: no drops, no big fills, no lead melody. Instrumental only, no vocals.

### Como escolher humor e BPM

| sentimento da marca | BPM de partida | paleta |
|---|---|---|
| urgência / prazo / sorteio | ~126 | pop-eletrônico, kick em 4, hi-hat em semicolcheia |
| tecnologia / progresso | ~112 | eletrônica limpa, plucks sintéticos, arpejo |
| cuidado / família / alívio | ~100 | pop acústico, violão, ukulele, piano, estalos |

Uma marca nova: peça à pessoa o **sentimento** (uma palavra) e o **assunto** do anúncio, escolha a
linha mais próxima, mostre o prompt final e o custo (1.641,41 cr por variação; 1 variação basta se
ela não quer escolher entre duas — a segunda pode falhar no servidor, como aconteceu com a Allevo).

## O que aprendemos medindo (vale para qualquer geração)

Meça **tudo** antes de usar, sempre com os comandos do repositório:

```bash
./ev audio inspect brands/<marca>/sound/sfx/*.mp3      # duração, pico, onde há som de verdade
./ev audio beat brands/<marca>/sound/music/<trilha>.mp3  # BPM, fase da batida, ataques do fim (o hit final)
./ev audio vocals brands/<marca>/sound/music/<trilha>.mp3  # voz cantada escondida? (Whisper)
```

- **Geração muda existe.** Efeito mudo (pico de −40 dB ou menos; os descartados mediram −54 a −72 dB) não se guarda.
- **A duração pedida não é a entregue:** pediram 31s e veio 40s; pediram "hit final em 30s" e a
  Allevo veio sem hit claro (nível estável até 42,5s, decai depois). O ponto de alinhamento é o
  **último ataque forte medido** (`beat`), nunca o pedido.
- **Alinhe o hit final com a última palavra:** `offset = hit − t_última_palavra` (vídeo mais curto
  que o hit) ou `from = t − hit` (mais longo). O tempo da palavra sai de `./ev audio words` (já no
  corte acelerado), nunca da transcrição bruta.
- **"Instrumental only" não garante:** o conector marcou `Instrumental: False` e o Whisper não achou
  voz nenhuma — mas confira sempre (`vocals`).
- **Tic-tac pedido "2 por segundo" vem 1/s ou 1 tick só:** por isso a cama é montada por
  `./ev tick` a partir de um tick, no BPM da trilha.
- **O nível não se chuta:** trilha em `presence`, efeito em `lu` (docs/05-som.md §4a). Comece com
  `presence 0` e ajuste pelo que a pessoa ouvir.
- **Registre cada som em `brands/<marca>/sound/SONS.md`** com medição, prompt verbatim e custo
  (sem o id do fluxo do ElevenLabs — é identificador do seu workspace).
