# 07 — Referência do plan.json (e do brand.json)

O `edit.py` carrega `brands/<brand>/brand.json` e mescla o `plan.json` por cima. Qualquer campo
abaixo pode estar em um ou no outro; a coluna "mora em" diz onde ele **deveria** estar. Campos que
começam com `_` são comentário (o script ignora) — use-os para registrar o porquê.

## Corte e saída

| campo | mora em | exemplo | o que faz |
|---|---|---|---|
| `brand` | vídeo | `"clube-da-virada"` | qual `brands/<marca>/` usar |
| `source` | vídeo | `"~/Downloads/C2558.MP4"` | o bruto |
| `output_subdir` | vídeo | `"2026-10-06"` | agrupa uma leva: o vídeo sai em `output/<marca>/<subpasta>/` (opcional; sem ele sai direto em `output/<marca>/`) |
| `output_name` | vídeo | `"C2558_editado_v1.mp4"` | sai em `output/<marca>/`; suba o `_vN` a cada ajuste |
| `keep` | vídeo | `[[40.30, 51.45], [96.30, 104.45]]` | takes que ficam, em ordem (bordas encostam no silêncio) |
| `keep_window` | vídeo | `[13.95, 55.75]` | alternativa a `keep` quando é um trecho só |
| `remove` | vídeo | `[[20.1, 21.3]]` | trecho a tirar de dentro de um take |
| `max_pause` | marca | `0.45` | pausa maior que isso é encurtada |
| `pad_before_speech` / `pad_after_speech` | marca | `0.10` / `0.15` | respiro que sobra antes/depois da fala em cada corte |
| `silence_db` | marca | `-35` | limiar do `silencedetect` |
| `speed` | marca | `1.25` | velocidade final (vídeo e voz, tom preservado) |
| `output_size` | marca | `[1080, 1920]` | |
| `look` | marca | `"natural"` | chave de `LOOKS` em `edit.py` |
| `loudness_lufs` | marca | `-14` | usado só quando não há `sound` |

## `captions`

| campo | exemplo | |
|---|---|---|
| `enabled` | `false` | **no vídeo**: `false` não queima legenda (o `.srt` sai vazio). Padrão `true` |
| `font_file` | `"fonts/Nunito.ttf"` | relativo à pasta da marca |
| `weight` | `"ExtraBold"` | instância da fonte variável |
| `size` / `stroke` | `32` / `6` | em quadro de **480 px de largura** (escala sozinho); o traço é limitado pela contraforma |
| `pos_x` / `pos_y` | `50` / `60` | % do quadro |
| `color` / `stroke_color` | `"#FFFFFF"` / `"#030303"` | |
| `max_words` · `max_width` · `max_gap` · `min_on_screen` | `4` · `0.875` · `0.65` · `0.55` | |
| `proper_nouns` | `["Clube", "Virada"]` | somados aos achados na transcrição |
| `force_lowercase` | `[]` | tira uma palavra da lista de nomes próprios |
| `keep_together` | `["25 mil reais", "Clube da Virada"]` | expressões que um bloco nunca separa |
| `text_fixes` | `[{"from": "11h59", "to": "23h59", "why": "…"}]` | **no vídeo**: troca de texto depois da tipografia, bloco a bloco. Com `"regex": true` o `from` é expressão regular — use `\\b` para não trocar dentro de outra palavra (`"\\bDade\\b"` não pega "idade") |

## `fine_print` e `logo` (marca)

| campo | exemplo | |
|---|---|---|
| `fine_print.file` | `"fine-print.txt"` | texto verbatim; `\n` força quebra |
| `fine_print.size` · `weight` · `max_width` · `margin_bottom` · `alpha` · `shade_alpha` | `21` · `"SemiBold"` · `0.9` · `56` · `225` · `150` | em px de 1080; degradê escuro atrás |
| `logo.file` · `width` · `top` | `"logo/logo-branco.png"` · `200` · `80` | centralizado em X |
| `logo.shadow` · `shadow_alpha` | `true` · `0.45` | sombra suave para ler sobre fundo cheio |

## `sound` (vídeo)

```json
"sound": {
 "target_lufs": -14,
 "music": [{"file": "urgencia-126bpm-a.mp3", "from": 0, "to": 30.18, "offset": 0.19, "db": -27,
            "fade_out": 0.3, "why": "hit final alinhado em 'tela'"}],
 "dropouts": [{"from": 16.65, "to": 17.92, "db": -30, "why": "'tá maluco?' no vazio"}],
 "sfx": [{"file": "impact-b.mp3", "at": 1.88, "length": 0.9, "tail": 0.3, "db": -13, "why": "A · '25 mil'"},
         {"file": "tap-b.mp3", "offset": 0.22, "at": 20.28, "length": 0.15, "tail": 0.1, "db": -16, "why": "CTA"},
         {"path": "tick_bed.wav", "at": 0, "length": 30.1, "tail": 0.05, "db": -22, "why": "prazo"}],
 "_ausencias": "o que foi deixado de fora, de propósito"
}
```

| campo | |
|---|---|
| `music[].file` | em `brands/<marca>/sound/music/` |
| `music[].from` / `to` | quando entra/sai no vídeo (s) |
| `music[].offset` | de onde a faixa começa a tocar (s) — é como se alinha o hit final |
| `music[].db` | relativo a −12 LUFS; se omitido, `sound_defaults.music_db` da marca (−27) — método antigo (Clube) |
| `music[].presence` | **método percebido**: presença sobre a voz em 1–8 kHz; 0 = igual ao Clube aprovado; se omitido e a marca tiver `sound_defaults.music_presence`, usa esse ([05-som.md §4a](05-som.md)) |
| `sfx[].lu` | **método percebido**: loudness momentânea máx do trecho em LU relativos à voz (ex. −13 para nível C) |
| `dropouts[]` | a trilha cai a `db` (padrão −30) entre `from` e `to` (rampa 60 ms) |
| `sfx[].file` / `path` | `file` na biblioteca da marca (`sound/sfx/`); `path` relativo à pasta do projeto |
| `sfx[].offset` | pula o começo do arquivo (ex.: pegar só o 1º toque) |
| `sfx[].at` · `length` · `tail` · `db` | quando entra · quanto toca · fade depois · relativo a pico −1 dBFS — `db` **obrigatório** (exceto `tick_bed.wav`, que herda −22) |

Mais de uma entrada em `music` faz crossfade de 0,4s entre elas (foi assim na v2, com motivos da
biblioteca; o aprovado usa uma peça só).

## `variants` (vídeo)

Gancho × corpo × CTA a partir de uma gravação, com som ancorado em blocos (`block`/`anchor`/`rel`/`when`, `align_end`): schema e comandos em [08-variacoes-e-saidas.md](08-variacoes-e-saidas.md).
