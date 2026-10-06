# 01 — O fluxo de uma edição, do bruto ao vídeo aprovado

Exatamente o caminho que produziu os primeiros vídeos aprovados (C2556–C2559, 2026-09-24). Cada passo
diz o comando, o que olhar e o erro que ele evita. Todos os comandos usam o atalho `./ev`
(`./ev --help`); em máquina nova rode `./ev setup` antes.

## 0. Receber o pedido

- **Qual vídeo e qual marca?** O bruto costuma estar em `~/Downloads/<ID>.MP4` (câmera Sony, 4K
  H.264 8 bits Rec.709, gravado deitado com rotação −90° — o ffmpeg já endireita para 9:16).
- **A marca já existe em `brands/`?** (`./ev brand --list`.) Se não, pare e faça o onboarding:
  [09-onboarding-de-marca.md](09-onboarding-de-marca.md) (a visão geral do que é da marca e do vídeo
  está em [06-marcas.md](06-marcas.md)).
- **Pediu uma saída sob medida?** Variações (gancho × corpo × CTA), sem legenda, sem som, outro
  tamanho, mais/menos trilha → [08-variacoes-e-saidas.md](08-variacoes-e-saidas.md); no caso das
  variações o plano usa o bloco `variants` em vez de `keep` e o render é `./ev variants`.
- **O texto de `fine-print.txt` da marca ainda vale para esta campanha?** Se o vídeo é de outra fase,
  pergunte antes de renderizar.

## 1. Transcrever

```bash
mkdir -p projects/clube-da-virada/C2560
```

```bash
./ev transcribe ~/Downloads/C2560.MP4 projects/clube-da-virada/C2560
```

Grava `audio16k.wav`, `words.json` (tempo por palavra) e `transcript.txt`. Leva ~1 min por minuto de
bruto na CPU. **VAD desligado de propósito:** queremos ver claquete, conversa de set e takes
repetidos para decidir o corte.

## 2. Decidir o que fica — lendo a transcrição

Leia `transcript.txt` inteiro e marque os **takes que ficam**. As regras estão em
[02-cortes.md](02-cortes.md). Na prática:

- claquete e conversa de set ("1, 2, 3, ação", "peraí de novo") saem;
- falso início ("Responda uma rápida…") sai;
- **take repetido: fica o último que ele completou** — normalmente o que ele pediu para refazer;
- pausa longa não precisa marcar: o script encurta toda pausa > 0,45s.

Para ver o tempo exato de cada palavra nas bordas:

```bash
python3 -c "import json;[print(f\"{w['s']:7.2f}-{w['e']:7.2f} {w['t']}\") for w in json.load(open('projects/clube-da-virada/C2560/words.json')) if 40<w['s']<56]"
```

🚩 **Confira fatos falados contra a campanha:** horário, data, valor. No C2559 ele disse "11h59" e o
prazo é 23h59 — a pessoa pegou; a legenda foi corrigida com `text_fixes` (ver trava 5 do CLAUDE.md).

## 3. Escrever o plan.json

Copie `projects/_template/plan.json` (ele já traz o bloco `sound` com a trilha da marca; o script
recusa rodar com o `keep` de exemplo `[[0, 0]]`). O corte, no mínimo:

```json
{
 "brand": "clube-da-virada",
 "source": "~/Downloads/C2560.MP4",
 "output_name": "C2560_editado_v1.mp4",
 "keep": [[40.30, 51.45], [54.50, 74.60]],
 "_keep": "por que cada trecho saiu — é o registro da decisão editorial"
}
```

Sem o bloco `sound` o vídeo sai só com a voz (o script avisa). As bordas de `keep` podem ser os tempos do Whisper: o script **encosta cada borda no silêncio
medido** (`snap_to_silence`), porque o Whisper erra a borda da palavra em até ~0,2s. Referência de
campos: [07-plan-json.md](07-plan-json.md).

## 4. Conferir a legenda antes de renderizar

```bash
./ev edit projects/clube-da-virada/C2560/plan.json --dry
```

Mostra cada bloco no **tempo final** (já cortado e a 1,25x). Procure:

- expressão da marca quebrada ("Clube / da Virada", "números / da sorte") → acrescente em
  `captions.keep_together` **do brand.json** (vale para os próximos);
- bloco terminando em "pra", "de", "o" → a quebra já penaliza; se aparecer, é falta de espaço;
- palavra que o Whisper errou → `captions.text_fixes` no plan.json do vídeo.

Regras completas: [03-legenda.md](03-legenda.md).

## 5. Planejar o som

Leia [05-som.md](05-som.md) — é a etapa que mais pesa na qualidade. Resumo do que se faz:

1. tempos das palavras-chave no corte final:
   ```bash
   ./ev audio words projects/clube-da-virada/C2560/plan.json 25 botão sorte
   ```
2. hierarquia: **A** (o prêmio), **B** (gancho, prazo, CTA), **C** (número da sorte, tic-tac);
3. trilha da biblioteca, com o **hit final alinhado à última palavra** (`offset` ou `from`);
4. tic-tac nas falas de prazo, travado no BPM (`scripts/tick_bed.py`);
5. escreva `sound` no plan.json — **cada linha com `why`**, e as ausências em `_ausencias`.

Som novo? Só com permissão (trava 2).

## 6. Renderizar

```bash
./ev edit projects/clube-da-virada/C2560/plan.json
```

~1 min para 30s de vídeo. Ordem interna (herdada do cofre): cortar → **acelerar** → cor →
letras miúdas + logo → legenda (já no tempo acelerado) → voz → mix de som → `.mp4` + `.srt` em
`output/<marca>/`. Intermediários ficam no projeto (`stage_video.mov`, `stage_voice.wav`,
`mix_pre.wav`, `edit-report.json`).

## 7. QA da máquina

```bash
./ev qa output/clube-da-virada/C2560_editado_v1.mp4 --sheet
```

```bash
./ev audio mix projects/clube-da-virada/C2560
```

O primeiro reprova formato, loudness (−14 ±0,5 LUFS), pico e dessincronia. O segundo diz quantos dB
a trilha fica abaixo da voz (nos aprovados: **~14 dB no vídeo inteiro, ~18 dB no CTA**) e confirma
que cada dropout realmente silenciou (fundo ≤ −29 dB). Abra a folha de contato
(`*_contato.jpg`) e olhe: legenda legível, logo acima da cabeça, rodapé inteiro.

## 8. Mandar e iterar

Para refazer **só o som** (corte e legenda já aprovados): `./ev edit <plan.json> --remix` — reusa
`stage_video.mov` e `stage_voice.wav` do último render e leva ~2 s.

Mande o `.mp4` com: duração bruto → final, o que foi cortado e
por quê, o que conferir (palavras da legenda, fatos falados), e o que custou (se gerou som).

Cada ajuste vira `_v2`, `_v3`… Se o ajuste é de **estilo** (vale para todos), mude o `brand.json`.
Se é do vídeo, mude o plan.json. **E registre em [aprendizados.md](aprendizados.md).**

**Quando a pessoa aprovar:** acrescente a linha em `output/<marca>/APROVADOS.md` e, se entrou som
novo, mova-o para "Em uso" em `brands/<marca>/sound/SONS.md` com prompt, custo e medição.

## Tempo de referência

C2557–C2559 (três vídeos, do pedido à entrega): transcrição ~5 min em segundo plano, decisão e
planos ~15 min, render ~1 min cada.
