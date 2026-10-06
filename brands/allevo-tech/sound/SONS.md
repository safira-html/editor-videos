# Biblioteca de som — Allevo Tech

**Antes de gerar som novo, procure aqui.** Medido com `audio_tools.py inspect` / `beat` / `vocals` em 2026-09-25.

## Trilha

| arquivo | dura | BPM | medição | papel |
|---|---|---|---|---|
| `music/carreira-112bpm-a.mp3` | 45,0s | **112,00** (batidas em 0,530s + k×0,5357s) | pico −1,3; nível estável (~−14) até 42,5s, cai até 44,5s; último ataque forte **38,96s**; sem voz (Whisper) | **a trilha da campanha**: eletrônica limpa, curiosa no início, confiante depois. Alinhe 38,96s na última palavra (`offset = 38,96 − t`) |

## Efeitos

| arquivo | dura | pico | som útil | papel |
|---|---|---|---|---|
| `sfx/whoosh-b.mp3` | 1,0s | −0,6 | 0,58s (0–0,58) | **A** · virada problema → solução ("Na formação…"), junto do impact |
| `sfx/whoosh-a.mp3` | 2,0s | −3,1 | 0,82s (0,24–1,06) | 2ª variação (começa em 0,24s: use `offset 0.24`) |
| `sfx/glitch-a.mp3` | 0,48s | −8,1 | 0,40s | **C** · sobrecarga ("lista de ferramentas", "cinco ferramentas") |
| `sfx/glitch-b.mp3` | 2,0s | −4,3 | 1,66s | 2ª variação, mais longa |
| `sfx/achievement-b.mp3` | 1,0s | −0,4 | 0,74s | **C** · conquista ("certificados", "projetos", "portfólio") — **uma vez por vídeo** |
| `sfx/achievement-a.mp3` | 1,0s | −12,8 | 0,20s | 2ª variação, fraca |
| `sfx/typing-b.mp3` | 2,0s | −0,5 | 0,76s | **C** · teclado ("preenchendo planilha") |
| `sfx/typing-a.mp3` | 6,0s | −0,3 | 2,76s | 2ª variação, rajada longa |
| `sfx/impact-b.mp3` · `90-01-riser.mp3` · `tap-b.mp3` · `tick-a.mp3` · `90-02-ding.mp3` · `downer-b.mp3` | | | | **copiados da biblioteca do Clube da Virada** (ver `brands/clube-da-virada/sound/SONS.md`) — sem custo |

## Procedência — ElevenLabs, 2026-09-25

| arquivos | flow | modelo | variações × custo | prompt (verbatim) |
|---|---|---|---|---|
| `carreira-112bpm-a` | (id omitido) | `eleven_music_v2` | 2 pedidas × 1.641,41 cr — **a 2ª falhou no servidor** ("unexpected error generating music") | "45 seconds. Modern tech instrumental bed for a Brazilian social-media ad about a hands-on data analyst course for people changing careers. 112 BPM, clean electronic pop: tight kick, crisp claps, muted synth plucks, soft arpeggiated synth, warm sub bass, subtle digital textures. Curious and a little restless at the start, then steadily builds into a confident, optimistic groove with a clear sense of progress and forward motion. Starts immediately with the beat, no intro. Full energy at 15 seconds. Ends at 40 seconds on one clean final hit, then silence. Leaves room for a voiceover: no drops, no big fills, no lead melody. Instrumental only, no vocals." |
| `whoosh-a/b` | (id omitido) | `eleven_text_to_sound_v2` | 2 × 50 cr | "Short clean modern whoosh transition, airy swipe that rises then resolves, smooth and bright, tech advertising feel, no impact at the end, 1 second, dry, no music." |
| `glitch-a/b` | idem | idem | 2 × 50 cr | "Short digital glitch stutter, quick computer data error blip with a few crunchy bit-crushed fragments, confused and overloaded feeling, clean and modern, not harsh, 0.8 seconds, dry, no music." |
| `achievement-a/b` | idem | idem | 2 × 50 cr | "Bright positive achievement chime, a short two-note rising digital notification like unlocking a badge or earning a certificate in an app, clean, satisfying, modern UI, 1 second, dry, no music." |
| `typing-a/b` | idem | idem | 2 × 50 cr | "Fast office keyboard typing on a laptop, a short burst of keystrokes followed by one enter key press, close mic, clean, everyday spreadsheet work, 1.5 seconds, dry, no music." |

A trilha não soou "um hit final limpo" como pedido: ela segue em nível até 42,5s e decai — o ataque de 38,96s é o ponto de alinhamento.
