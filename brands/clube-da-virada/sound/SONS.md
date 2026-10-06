# Biblioteca de som — Clube da Virada

**Antes de gerar som novo, procure aqui.** Tudo foi medido com
`python3 scripts/venv_run.py scripts/audio_tools.py inspect <arquivo>` em 2026-09-24.
"Som útil" = tempo acima de −45 dBFS no arquivo **cru** (o som quieto, como o riser, rende mais
depois do nivelamento do mix — ele sobe o pico a −1 dBFS antes de aplicar o `db` do plano).

## ✅ Em uso nos anúncios aprovados (C2556 v6, C2557, C2558, C2559 v2)

| arquivo | dura | pico | som útil | papel | nível usado |
|---|---|---|---|---|---|
| `music/urgencia-126bpm-a.mp3` | 40,0s | −1,1 | 36,6s | **a trilha da campanha**: 126,00 BPM, batidas em 0,470s + k×0,4762s, **hit final 29,99s**, decai até ~37s | −27 |
| `sfx/impact-b.mp3` | 2,0s | −2,1 | 0,8s | impact + sub: momento A (−13) e gancho (−18) | −13 / −17 / −18 |
| `sfx/tick-a.mp3` | 1,0s | −0,5 | 0,06s | **um tick** (ataque em 0,52s) — matéria-prima do `tick_bed.py` | cama a −22 |
| `sfx/downer-b.mp3` | 2,0s | −2,7 | 1,2s | "está fora": thud + queda de pitch | −16 |
| `sfx/tap-b.mp3` | 2,0s | −0,0 | 0,12s | toque de tela — **dois toques** (0,24s e 1,26s); use `offset 0.22`, `length 0.15` | −16 |
| `sfx/90-01-riser.mp3` | 2,0s | −21,5 | 0,5s* | riser curto antes do momento A (da peça 90) | −17 (A) / −20 (B) |
| `sfx/90-02-ding.mp3` | 2,0s | −1,0 | 1,4s | "número da sorte" (da peça 90) | −20 / −23 |

## ⚪ Guardados, não usados no aprovado

| arquivo | por quê está aqui |
|---|---|
| `music/urgencia-126bpm-b.mp3` | 2ª variação da trilha: mesmo BPM, **corta seco** perto de 31s (ataques 30,46 / 30,72s) em vez de decair. Alternativa para variar sem gerar |
| `music/pulso.mp3` · `lista.mp3` · `energia.mp3` · `fecho.mp3` | trilhas institucionais da peça 90 (cofre). Usadas na v2 do C2556 e **reprovadas por falta de energia** para anúncio de prazo. Servem para peça calma/confessional |
| `sfx/90-03-resolve.mp3` | fecho institucional da peça 90. No aprovado o hit da própria trilha fecha |
| `sfx/impact-a.mp3` | 2ª variação do impact: mais fraco (pico −15,4, 0,5s úteis) |
| `sfx/downer-a.mp3` | 2ª variação do downer: mais curto (0,6s) |
| `sfx/tick-b.mp3` | 2ª variação do tic-tac: 12s a **1 tick/s** (pedido era 2/s) — lento demais para urgência |

🚫 **Descartado:** `tap-a` (pico −66 dB — mudo). Não foi guardado.

## Procedência — ElevenLabs, 2026-09-24

| arquivos | modelo | variações × custo | prompt (verbatim) |
|---|---|---|---|
| `urgencia-126bpm-a/b` | `eleven_music_v2` | 2 × 1.641,41 cr | "31 seconds. Energetic, urgent instrumental bed for a Brazilian social-media ad about a cash prize draw with a closing deadline. 126 BPM, bright pop-electronic: driving four-on-the-floor kick, tight claps, ticking 16th-note hi-hats, punchy bass, plucked synth and staccato strings, confident and optimistic, countdown feel. Starts immediately with the beat, no intro. Lifts to full energy at 17 seconds. Ends at 30 seconds on one clean final hit, then silence. Leaves room for a voiceover: no drops, no big fills, no lead melody. Instrumental only, no vocals." |
| `tick-a/b` | `eleven_text_to_sound_v2` | 2 × 50 cr | "Mechanical clock ticking, steady tick-tock, two ticks per second, close mic, crisp and clean, 4 seconds, dry, no music." |
| `impact-a/b` | `eleven_text_to_sound_v2` | 2 × 50 cr | "Soft cinematic impact with a deep sub bass thump, tight punchy transient, short tail under one second, modern clean advertising sound, 2 seconds, dry, no music." |
| `tap-b` (+ `tap-a` mudo) | `eleven_text_to_sound_v2` | 2 × 50 cr | "Single smartphone screen tap, crisp UI button click, very short and clean, close mic, 1 second, dry, no music." |
| `downer-a/b` | `eleven_text_to_sound_v2` | 2 × 50 cr | "Short low thud followed by a quick downward pitch drop, like a timer running out, clean and modern, serious not comedic, 1.5 seconds, dry, no music." |

**Total: 3.682,8 créditos** (estimativa com `estimate_only` = cobrado). A voz não foi checada por
ouvido — a checagem de voz cantada na trilha foi por Whisper (nenhuma).

Da peça 90 do cofre (sem custo aqui): `pulso`, `lista`, `energia`, `fecho`, `90-01-riser`,
`90-02-ding`, `90-03-resolve` — origem: biblioteca institucional privada do autor (peça 90), não incluída aqui.
