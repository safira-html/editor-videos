# 08 — Variações e saídas sob medida

Pedidos que mudam **o que sai** de uma gravação, feitos na hora de pedir a edição. Parte 1: as
**variações combinatórias** (gancho × corpo × CTA). Parte 2: as **outras saídas** (velocidade,
tamanho, sem legenda, sem som…) e como cada uma mapeia para campos que existem hoje.

## Parte 1 — Variações combinatórias

Uma gravação com 2 ganchos, 2 corpos e 2 CTAs vira **8 vídeos** (2 × 2 × 2), cada um com uma
combinação. Sinais no pedido: "faz variações", "testa dois ganchos", "gravei duas versões do começo".

### O schema (bloco `variants` no `plan.json`)

```json
"variants": {
  "order": ["hook", "body", "cta"],
  "blocks": {
    "hook": {"h1": {"keep": [[12.1, 17.4]], "label": "pergunta"}, "h2": {"keep": [[40.2, 44.9]], "label": "dado"}},
    "body": {"m1": {"keep": [[50.0, 70.2]]}, "m2": {"keep": [[80.0, 99.1]]}},
    "cta":  {"c1": {"keep": [[110.0, 118.5]]}, "c2": {"keep": [[125.0, 133.0]]}}
  },
  "exclude": [["h2", "m1", "c2"]],
  "only": null
}
```

| campo | o que faz |
|---|---|
| `order` | a ordem dos blocos no vídeo final. O nome do arquivo junta o id de cada opção nessa ordem: `h1-m1-c1` |
| `blocks.<bloco>.<id>.keep` | os takes dessa opção, em segundos do bruto (mesma regra do `keep` normal: bordas encostam no silêncio, pausas > 0,45 s encurtam) |
| `blocks.<bloco>.<id>.label` | rótulo para a tabela do `--list` (opcional) |
| `exclude` | combinações removidas. Aceita `"*"` como curinga: `["h2", "*", "c2"]` |
| `only` | lista de combinações; restringe a só elas (`null` = todas) |

Os ids das opções são **únicos no plano inteiro** (eles nomeiam os arquivos). O `keep` do topo do
`plan.json` não é usado quando há `variants`; o resto do plano (legenda, som, sobrescritas da marca)
vale para todas as combinações.

Saída: `output/<marca>/<ID>_h1-m1-c1_v1.mp4` … (+ `.srt`). A versão `_vN` vem do `output_name` do plano.
Cada combinação ganha um plano derivado em `projects/<marca>/<ID>/variants/<combo>/plan.json`.

### Som nas variações: âncoras em vez de tempo absoluto

O tempo absoluto muda com cada combinação, então o som aponta para o **começo ou o fim de um bloco**
(no vídeo final, já cortado e acelerado):

```json
"sound": {
  "music": [{"file": "urgencia-126bpm-a.mp3", "align_end": true, "fade_out": 0.3, "why": "hit final na última palavra"}],
  "dropouts": [{"block": "body", "anchor": "start", "rel": -0.1, "len": 0.25, "why": "micro-silêncio antes do corpo"}],
  "sfx": [
    {"file": "impact-b.mp3", "block": "hook", "anchor": "start", "rel": 0.0, "length": 0.6, "tail": 0.4, "lu": -10,
     "why": "gancho"},
    {"file": "impact-b.mp3", "block": "body", "anchor": "start", "rel": -0.12, "length": 0.9, "tail": 0.3, "lu": -6,
     "when": {"hook": "h2"}, "why": "só quando o gancho é o dado"},
    {"file": "tap-b.mp3", "offset": 0.22, "block": "cta", "anchor": "start", "rel": 1.1, "length": 0.15, "lu": -19.5,
     "why": "CTA"}
  ]
}
```

| campo | onde | o que faz |
|---|---|---|
| `block` + `anchor` (`"start"` / `"end"`) + `rel` (s) | `sfx`, `dropouts` | no lugar de `at` (efeito) ou `from` (dropout): tempo = começo/fim do bloco + `rel` |
| `len` | `dropouts` | duração do dropout (vira o `to`) |
| `when` | `sfx`, `dropouts` | `{"hook": "h2"}`: o item só vale quando essa opção foi a escolhida |
| `align_end: true` | `music[]` | alinha o **hit final da trilha** ao começo da última palavra falada, usando `sound_defaults.music_hits[<arquivo>]` do `brand.json` (para medir um arquivo novo: `./ev audio beat <arquivo>`) |

Itens sem essas chaves passam como sempre. **Cama de tic-tac (`tick_bed.py`, efeito com `path`) não é
suportada** nas variações: o script avisa e descarta esses efeitos (a fase do tic-tac depende do tempo
absoluto de cada combinação).

### Os comandos

```bash
./ev variants projects/<marca>/<ID>/plan.json --list            # combinações, quantidade e duração estimada; não renderiza
./ev variants projects/<marca>/<ID>/plan.json --dry             # blocos de legenda de cada combinação; não renderiza
./ev variants projects/<marca>/<ID>/plan.json --jobs 3          # renderiza todas (3 em paralelo) e roda o QA
./ev variants projects/<marca>/<ID>/plan.json --only h1-m2-c1 h2-m1-c1   # só estas
./ev variants projects/<marca>/<ID>/plan.json --no-qa           # sem o QA automático
```

### Como o assistente atende o pedido

1. **Transcreva** e leia o `transcript.txt` inteiro ([01-fluxo-de-edicao.md](01-fluxo-de-edicao.md)).
2. **Identifique cada take de cada bloco** (cada gancho, cada corpo, cada CTA). A regra do último
   take completo vale **por opção**: se um gancho foi regravado, use o último dele.
3. **Mostre a tabela das opções e a contagem de combinações, e peça confirmação antes de
   renderizar** (8 renders levam um tempo; o `--list` dá a duração estimada):

   | bloco | id | takes (bruto) | o que é |
   |---|---|---|---|
   | hook | h1 | 12,1–17,4 | pergunta |
   | hook | h2 | 40,2–44,9 | dado |
   | … | | | |

   → 2 × 2 × 2 = **8 vídeos** (menos o que for excluído). Pergunte se alguma combinação não faz
   sentido.
4. **Combinações que não fazem sentido editorial devem sair** com `exclude`: um CTA que remete ao
   número do gancho ("com esse desconto…") com o gancho que não tem número; um corpo que continua
   o assunto do gancho A depois do gancho B.
5. **Escreva o bloco `variants` e o som com âncoras**, rode `--list`, depois `--dry` (confira as
   quebras de legenda), depois renderize com `--jobs 3`.
6. **QA em todas as saídas** (o `variants` já roda o `qa.py`; confira o resultado de cada uma e abra
   a folha de contato de pelo menos duas) e **mande uma tabela**: combinação · duração · QA · o que é.
7. ⚠️ **Avise:** a emenda entre blocos é um *jump cut* do mesmo plano da mesma fonte (o apresentador
   "pula" de posição entre gancho e corpo). É a linguagem do formato, e é esperado.

Detalhes que o script já trata: uma legenda nunca atravessa dois blocos, e o começo de um bloco conta
como começo de frase (a regra de nomes próprios não confunde a maiúscula do início).

## Parte 2 — Outras saídas pedidas no input

Cada linha confere com o `edit.py`. Campos de marca valem para todos os vídeos da marca (confirme
antes de mudar o `brand.json`); no `plan.json` valem só para aquele vídeo e sobrescrevem a marca.

| a pessoa pede | como | onde |
|---|---|---|
| outra velocidade ("sem acelerar", "1,1x") | `"speed": 1.0` | `plan.json` (vídeo) ou `brand.json` (marca). `1.0` desliga |
| outro look de cor ou nenhum | `"look": "none"` / `"natural"` / `"warm_neutral"` / `"punch"` | idem |
| **sem som** (só a voz) | omita o bloco `sound` do `plan.json` (a marca não tem bloco `sound`, só `sound_defaults`). O vídeo sai só com a voz em `loudness_lufs` (−14) | `plan.json` |
| **sem legenda** | `"captions": {"enabled": false}` | `plan.json` |
| **só o `.srt`** | não existe modo "só `.srt`". O `.srt` sai sempre ao lado do `.mp4`; para ver só o texto use `./ev edit … --dry` | — |
| sem logo | `"logo": null` no `plan.json` (sobrescreve o da marca) | `plan.json` |
| sem letras miúdas | `"fine_print": null` no `plan.json` | `plan.json` |
| loudness diferente | `sound.target_lufs` (com som) ou `loudness_lufs` (sem som). ⚠️ o `qa.py` confere −14 ±0,5 fixo: a saída vai "reprovar" nesse item — diga isso | `plan.json` / `brand.json` |
| **mais / menos trilha** | `sound.music[].presence` (+2 = 2 dB mais presente; −2 menos; 0 = referência). Ver [05-som.md §4a](05-som.md). Marcas no método antigo usam `db` | `plan.json` |
| mais / menos efeitos | cada `sfx[].lu` (ou `db`); remova o item para tirar | `plan.json` |
| várias versões | `output_name` com `_v2`, `_v3`…; `--remix` refaz só o som | `plan.json` |
| tamanho de saída (ex. 1920×1080) | `"output_size": [1920, 1080]` e `./ev qa … --size 1920x1080` — **mas leia a nota** | marca ou vídeo |

**Nota sobre `output_size`:** o campo existe, mas o resultado só é bom para a **mesma proporção**
(ex. `[720, 1280]`, que é 9:16 menor). O `edit.py` escala o bruto para o tamanho **sem cortar nem
colocar tarja**: pedir 16:9 de um bruto vertical estica a imagem. A legenda escala com a largura
(o corpo é definido em um quadro de 480 px), mas `logo.width`, `logo.top` e o corpo das letras
miúdas estão em **px absolutos de um quadro de 1080 de largura**; em outro tamanho eles ficam
desproporcionais. O `qa.py` aceita `--size`, mas confere sempre 29,97 fps.

### O que não existe hoje (e o que seria preciso)

| pedido | por que não dá | o que faltaria |
|---|---|---|
| **16:9 / 1:1 de um bruto vertical** (reenquadrar) | o script não corta nem coloca fundo desfocado | um modo de reenquadramento (crop com posição, ou fundo desfocado) no `edit.py`; logo e letras miúdas em % |
| só o `.srt`, sem renderizar vídeo | o `.srt` é gerado no fim do render | um flag `--srt-only` |
| legenda em outro idioma / tradução | a transcrição é em português (`language="pt"` fixo em `scripts/transcribe.py`) e as regras de quebra são do português | opção de idioma no `transcribe.py` e lista de palavras fracas por idioma |
| zoom, B-roll, transição, cortes de câmera | fora do escopo | outro pipeline |
| mais de um apresentador ou cena com troca de fonte | o pipeline assume uma fonte contínua | vários `source` no plano |
| tic-tac nas variações | a cama é montada com tempo absoluto | gerar a cama por combinação |
