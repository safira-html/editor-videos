# 05 — Som: trilha, efeitos, mixagem e geração

Destilado de três fontes **privadas** do autor (um guia de sonoplastia para anúncios, uma direção de
som e uma rotina de mixagem de um cofre de notas), que não estão neste repositório — o que valia
delas está nas regras abaixo (hierarquia A/B/C, `riser → dropout → impact`, silêncio como
ferramenta, referências de nivelamento) — e, acima de tudo, das correções feitas no C2556 e das
medições registradas em [aprendizados.md](aprendizados.md). **Marca nova:** comece pelo
[STARTER-KIT](../brands/_template/sound/STARTER-KIT.md) (efeitos básicos, molde de prompt de trilha, custos).

## A regra em uma linha

> **Não sonorize o corte; sonorize a intenção.** (guia, `00-README.md`)

E duas pistas sempre, montadas juntas: **trilha** (responde ao sentimento) e **efeitos**
(respondem a um instante). Montar só uma delas foi o erro reprovado no cofre.

## 1. Hierarquia antes de escolher qualquer som

Classifique cada momento do roteiro:

| nível | no anúncio do Clube | tratamento aprovado |
|---|---|---|
| **A** — o momento principal | o prêmio: "alguém recebe **25 mil reais**" | **riser → micro-silêncio → impact + sub** (o maior som do vídeo, uma vez só) |
| **B** — secundários | gancho, "está fora", CTA ("toca no botão") | soft impact no gancho · downer em "está fora" · toque de tela no CTA |
| **C** — detalhe | "número da sorte", tic-tac | ding discreto · tic-tac baixo |

**Se tudo recebe impact, nada é importante.** O "25 mil" repetido no fim ("levar 25 mil pra casa")
**não** ganha outro impact — o A já aconteceu.

## 2. Os padrões que funcionaram

| padrão | onde | como está no plan.json |
|---|---|---|
| **riser → dropout → impact** | momento A | `90-01-riser.mp3` ~1,4s antes · `dropouts` de ~0,2s na trilha · `impact-b.mp3` a −13 |
| **tic-tac de prazo** | "faltam X dias pra fechar o prazo", "até domingo, às 23h59", "amanhã a gente descobre" | cama gerada por `tick_bed.py`, **no BPM da trilha**, dobra (colcheias) no último segundo, a −22 |
| **o tempo acabou** | "está fora" | tic-tac **e** trilha param juntos (`dropouts` ~1s) + `downer-b.mp3` a −16; a trilha volta na frase seguinte |
| **silêncio como piada** | C2558 "tá maluco?" | só `dropout` na trilha, nenhum efeito |
| **ação literal** | "toca no botão" | `tap-b.mp3` (1º toque: `offset 0.22`, 0,15s) a −16 |
| **recompensa** | "ganhou um número da sorte" | `90-02-ding.mp3` a −20; o 2º número ("mais um") a −23 — contagem, não repetição |
| **hit final = última palavra** | fim | alinhe o hit da trilha (29,99s em `urgencia-126bpm-a`) à última palavra com `offset` (vídeo mais curto) ou `from` (vídeo mais longo) |

**Ausência deliberada vai escrita** em `sound._ausencias` — é decisão tanto quanto o que se põe.

## 3. A trilha

**A primeira tentativa (biblioteca institucional da peça 90: `pulso`/`lista`/`energia`/`fecho`)
foi reprovada:** *"a trilha poderia ser mais agitada p combinar com o assunto… bpm e timing dela tá
mt fraquinho"*. Anúncio de sorteio com prazo pede **urgência**: a aprovada é uma peça única de
**126 BPM**, pop-eletrônica, four-on-the-floor, hi-hat em semicolcheia, sem melodia sobre a voz.

- **Uma peça contínua** para um anúncio de ~30s (não motivos trocando a cada frase).
- **A mesma trilha nos quatro anúncios da campanha** — identidade sonora.
- Alternativa gerada e guardada: `urgencia-126bpm-b.mp3` (corta seco em ~31s, em vez de decair).

### Alinhar o hit final

🚨 O tempo da última palavra sai de `audio_tools.py words` (já cortado e a 1,25x) — **nunca** da
transcrição bruta.

```bash
./ev audio beat brands/clube-da-virada/sound/music/urgencia-126bpm-a.mp3
```

→ `126.00 BPM · batidas em 0.470s + k×0.4762s`, último ataque forte **29,99s**. Para a última
palavra em `t`: `offset = 29,99 − t` (se `t < 29,99`) ou `from = t − 29,99` com `offset 0`.

| vídeo | última palavra | como ficou |
|---|---|---|
| C2556 | "você!" 29,89s | `offset 0` |
| C2557 | "mesmo." 25,45s | `offset 4.54` |
| C2558 | "tela." 29,80s | `offset 0.19` |
| C2559 | "sorteio." 30,55s | `from 0.56` |

### O tic-tac no tempo da trilha

A batida da faixa cai em `0,470 + k×0,47619` s (medido com `audio_tools.py beat`). No vídeo:
`fase = (0,470 − offset) mod 0,47619` quando a trilha toca desde o início com `offset`, ou
`fase = (from + 0,470) mod 0,47619` quando ela entra depois (`from`, `offset 0`). Ex.: C2557,
`offset 4.54` → fase ≈ 0,216 s. Depois:

```bash
./ev tick brands/clube-da-virada/sound/sfx/tick-a.mp3 projects/clube-da-virada/C2560/tick_bed.wav 126 <fase> <duração+0.5> projects/clube-da-virada/C2560/tick_windows.json
```

`tick_windows.json`: `[{"from": 20.2, "to": 22.9, "double_from": 21.9}]`. O tick alterna com um
"tac" um semitom abaixo para não soar metrônomo. No plan.json entra como efeito com
`"path": "tick_bed.wav"` (relativo à pasta do projeto).

## 4. Níveis e mixagem

### 4a. Método percebido (marcas novas, desde 2026-09-25) — `presence` e `lu`

🚨 A Allevo Tech v1 saiu com a trilha **inaudível** usando o `db −27` que funcionou no Clube. Medido:
o `db` é relativo ao **pico** (efeito) ou à **loudness do arquivo inteiro** (trilha), e nenhum dos dois
diz quanto o som *soa por cima da voz*:

- a trilha da Allevo tem a energia no subgrave (<150 Hz: −15,6 LUFS · >200 Hz: −20,1) — o celular não
  toca, e o nivelamento pelo arquivo inteiro conta esse sub;
- somando as oitavas de **1 a 8 kHz** (hi-hat, palma, synth: o que o celular reproduz e a voz cobre
  menos), ela ficou **5 dB menos presente** que a do Clube (−14,8 contra −9,7 dB); o Quero Card também (−14,7);
- no pico igual, o cachorro soou −4,7 LU da voz (mais alto que o impact do prêmio) e o teclado −24,9 (sumiu).

**Trilha: `"presence": 0`** = tão presente sobre **a voz deste vídeo** quanto a do Clube aprovado
(`PRESENCE_REF −9,7 dB`, média de C2556 v6 e C2559 v2). `+2` = 2 dB mais presente. O script mede a
trilha no trecho que toca, oitava por oitava contra a voz, e se a oitava de 125 Hz passar da do Clube
(`LOW_REF −8,9`) aplica um shelf abaixo de 150 Hz no excesso (na v2 cortou 5–7 dB — senão embola).

**Efeito: `"lu"`** = loudness momentânea máxima (400 ms) do trecho que toca, em LU relativos à voz.
Alvos, traduzidos do Clube aprovado (C2556 v6):

| nível | aprovado no Clube | alvo `lu` usado |
|---|---|---|
| A · impact do momento principal | −4,1 | −6 (Allevo) · −8 (Quero, marca de cuidado) |
| A · riser / whoosh da virada | −6,8 | −8 / −9 |
| B · downer, impact secundário, videochamada | −8,8 / −9,1 | −10 a −11 |
| C · ding, glitch, conquista, moedas, cachorro | −12,6 (2º: −15,6) | −13 a −14 |
| C · textura (teclado) | — | −16 |
| B · tap de tela (clique curto: a momentânea subestima) | −19,5 | −19,5 (C: −23) |

`edit-report.json → sound_levels` guarda, para cada som, o medido, o alvo e o ganho. O Clube continua em
`db` (aprovado assim — não reabrir sem pedido).

### 4b. Método antigo (`db`, Clube da Virada)

Os números do plano são **relativos a referências**, nunca ao arquivo cru (herdado do
`mix_episode.py` do cofre — os efeitos chegam espalhados por ~20 dB de pico):

| | referência | no plano |
|---|---|---|
| voz | nivelada a **−18,8 LUFS** | — |
| trilha | nivelada a **−12 LUFS**, depois `db` | **−27** (brand.json `sound_defaults.music_db`) |
| efeito | pico nivelado a **−1 dBFS**, depois `db` | −13 (A) · −16 a −18 (B) · −20/−23 (C) · tic-tac −22 |
| mix | `amix normalize=0` → ganho para **−14 LUFS** → `alimiter` (pico de amostra) | `target_lufs` |

O limitador não garante pico verdadeiro — quem garante é o `qa.py` (≤ −1 dBTP). Nos aprovados deu
−1,3 a −1,5 dBTP. Se reprovar, baixe o `limit` do `alimiter` em `edit.py`.

**Padrões da marca** (`brand.json → sound_defaults`): trilha sem `db` recebe −27, sem `from`/`to`
cobre o vídeo inteiro; dropout sem `db` recebe −30; o tic-tac (`tick_bed.wav`) sem `db` recebe −22.
**Efeito pontual sem `db` é recusado** — o nível dele é decisão de hierarquia, não padrão.

🚨 **A trilha desceu três vezes:** −17 (v3, *"tá mt alta"*) → −24 (v4) → **−27** (v6, *"um pouquinho
mais baixa ainda — sfx tá bom"*). Medido no v6: trilha **~18 dB abaixo da voz** no CTA. Os efeitos
não mudaram. **Comece em −27.**

**Dropout** (`sound.dropouts`): a trilha cai a −30 dB (padrão) entre `from` e `to`, com rampa de 60 ms (sem
estalo). Confira depois do render que o fundo realmente sumiu:

```bash
./ev audio mix projects/clube-da-virada/C2560
```

Cada efeito tem `length` (quanto toca) + `tail` (fade quadrático depois): efeito de ad pede cauda
curta — cauda longa embola.

## 5. Biblioteca da marca antes de gerar

`brands/clube-da-virada/sound/SONS.md` lista cada som, a medição, o prompt que o gerou e onde foi
usado. **Som aprovado que existe é melhor que som novo** — custo e continuidade (o mesmo prompt
devolve som diferente a cada geração).

## 6. Gerar no ElevenLabs — só com permissão

Conector **ElevenLabs (creative)** do claude.ai: é o servidor MCP cujas ferramentas se chamam
`creative_generate_in_flow`, `creative_get_flow_run_status`, `creative_list_voices` (o prefixo
`mcp__<id>__` muda por sessão — procure pelo nome com ToolSearch). 🚫 **Não** use
`audio_sfx_generate` / `audio_music_generate`: são de outro conector (Magnific), com outra cota.
`estimate_only: true` existe e funcionou em 2026-09-24 (devolveu 3.282,8 cr para 2 músicas e 100 cr
para 2 efeitos, sem cobrar).

| | trilha | efeito |
|---|---|---|
| `node_type` / `model_id` | `music` / `eleven_music_v2` | `sfx` / `eleven_text_to_sound_v2` |
| custo medido (2026-09-24) | **1.641 cr** por variação | **50 cr** por variação |
| `generations_count` | 2 se for escolher | 2 |

Procedimento:

1. `estimate_only: true` (grátis) com o prompt final → diga o que vai gerar, quanto custa, e que o
   saldo **não aparece no conector** (a pessoa vê em elevenlabs.io) → **espere o sim**;
2. use **um `flow_id`** para o lote todo;
3. poll com `creative_get_flow_run_status`; efeitos saem em ~20s, música em ~1–2 min;
4. baixe **um `curl -sL --http1.1` por vez** (sem `--http1.1` falha com exit 16; os links expiram em
   7200s). Não grave os links assinados em arquivo que fica;
5. **meça tudo antes de usar** (`audio_tools.py inspect` / `beat` / `vocals`) — ver abaixo;
6. guarde em `brands/<marca>/sound/` e registre em `SONS.md` com prompt, custo e medição.

**O que a geração entrega diferente do pedido (medido em 2026-09-24):**

| pedido | veio |
|---|---|
| trilha de 31s | **40s** (hit em 29,99s, decai até ~37s) |
| "Instrumental only" | config "Instrumental: False" — **sem voz** na checagem com Whisper, mas confira sempre |
| tic-tac "two ticks per second, 4 seconds" | uma variação com **1 tick só** (1s), outra com **1 tick/s** por 12s → a cama é montada por `tick_bed.py` a partir de 1 tick |
| toque de tela | uma das 2 variações **muda** (pico −66 dB) |
| 126 BPM | 126,00 medidos ✅ |

Prompt de efeito tem limite de **450 caracteres** (passar falha e cobra) e termine com
`dry, no music`. Duração vai **no texto** do prompt, não como parâmetro.
