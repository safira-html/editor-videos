# Biblioteca de som — Quero Card

**Antes de gerar som novo, procure aqui.** Medido com `audio_tools.py inspect` / `beat` / `vocals` em 2026-09-25.

## Trilha

| arquivo | dura | BPM | medição | papel |
|---|---|---|---|---|
| `music/cuidado-100bpm-a.mp3` | 45,0s | **100,00** (batidas em 0,005s + k×0,6000s) | pico −1,2; último ataque forte **39,14s**, decai de 41s a 44,5s; sem voz (Whisper) | **a trilha da campanha**: pop acústico acolhedor. Alinhe 39,14s na última palavra |
| `music/cuidado-100bpm-b.mp3` | 45,0s | 100,00 (0,300s + k×0,6000s) | pico −0,9; último ataque forte 40,20s; sem voz | 2ª variação, guardada |

## Efeitos

| arquivo | dura | pico | som útil | papel |
|---|---|---|---|---|
| `sfx/video-call-a.mp3` | 2,0s | −4,5 | 1,06s | **B** · telemedicina / TeleVet ("conversar com o médico por vídeo") |
| `sfx/video-call-b.mp3` | 4,0s | −5,6 | 2,10s | 2ª variação (dois toques) |
| `sfx/savings-a.mp3` | 1,0s | −6,6 | 0,82s | **C** · desconto / preço reduzido |
| `sfx/savings-b.mp3` | 2,0s | −7,5 | 1,16s | 2ª variação |
| `sfx/drawer-paper-a.mp3` | 1,0s | −14,4 | 0,70s | **C** · "na gaveta" / pedido de exame |
| `sfx/drawer-paper-b.mp3` | 2,0s | −13,6 | 0,66s | 2ª variação |
| `sfx/dog-whimper-a.mp3` | 2,0s | −20,3 | 1,16s | **C** · "seu cachorro passou mal" |
| `sfx/dog-whimper-b.mp3` | 1,0s | −23,5 | 0,30s | 2ª variação, curta |
| `sfx/whoosh-b.mp3` | | | | da biblioteca da Allevo Tech (mesmo lote) |
| `sfx/impact-b.mp3` · `90-01-riser.mp3` · `tap-b.mp3` · `tick-a.mp3` · `90-02-ding.mp3` · `downer-b.mp3` | | | | **copiados da biblioteca do Clube da Virada** — sem custo. `tick-a` vira o relógio de madrugada com `tick_bed.py` a 60 BPM |

🚫 **Descartados (mudos):** obturador de câmera (2 variações, pico −71/−72 dB) e ambiência de casa à noite (2 variações, pico −40/−54 dB, 0s úteis). Não foram guardados.

## Procedência — ElevenLabs, 2026-09-25

| arquivos | flow | modelo | variações × custo | prompt (verbatim) |
|---|---|---|---|---|
| `cuidado-100bpm-a/b` | (id omitido) | `eleven_music_v2` | 2 × 1.641,41 cr | "45 seconds. Warm, caring, optimistic instrumental bed for a Brazilian social-media ad about an affordable health benefits card for the whole family. 100 BPM, light acoustic pop: soft kick, finger snaps, muted acoustic guitar and ukulele plucks, gentle piano chords, warm round bass. Feels human, reassuring, everyday family life, a sense of relief. Starts immediately with the groove, no intro. Builds gently, full at 15 seconds. Ends at 40 seconds on one clean final hit, then silence. Leaves room for a voiceover: no drops, no big fills, no lead melody. Instrumental only, no vocals." |
| `video-call-a/b` | (id omitido) | `eleven_text_to_sound_v2` | 2 × 50 cr | "Friendly video call connecting sound on a smartphone app, a soft warm two-tone ascending chime that says the call is connected, clean modern UI, reassuring, 1 second, dry, no music." |
| `savings-a/b` | idem | idem | 2 × 50 cr | "Short pleasant savings sound, a few light coins dropping into a hand followed by a soft bright sparkle, feels like paying less, clean modern advertising, not a cash register, 1 second, dry, no music." |
| `drawer-paper-a/b` | idem | idem | 2 × 50 cr | "A wooden drawer sliding open and a folded paper sheet being picked up and rustled, close mic, soft and domestic, clean, 1.5 seconds, dry, no music." |
| `dog-whimper-a/b` | idem | idem | 2 × 50 cr | "A medium dog softly whimpering and whining a couple of times, unwell and seeking comfort, indoors, close mic, gentle not distressing, 1.5 seconds, dry, no music." |
| (descartado) shutter | idem | idem | 2 × 50 cr | "Single smartphone camera shutter click, crisp modern phone photo capture sound, very short and clean, close mic, 0.5 seconds, dry, no music." |
| (descartado) night ambience | idem | idem | 2 × 50 cr | "Quiet house at night ambience, very soft distant crickets outside a window, faint room tone, a wall clock ticking slowly, calm but a little tense, no voices, no cars, 6 seconds, no music." |

**Total do lote 2026-09-25 (as duas marcas):** 3 músicas completas × 1.641,41 + 20 efeitos × 50 = **5.924,2 cr** confirmados; a 4ª música falhou (o status mostra preço de 1.641,41 nela — confira em elevenlabs.io se foi cobrada).
