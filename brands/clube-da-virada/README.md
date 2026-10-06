# Clube da Virada — o estilo em uma tela

Anúncio vertical com apresentador sentado (plano médio, parede de plantas + estante). Aprovado pela
Safira no C2556 v6 em 2026-09-24; aplicado em C2557, C2558, C2559. Valores em `brand.json`.

| | |
|---|---|
| **formato** | 1080×1920, 29,97 fps, H.264 + AAC, −14 LUFS |
| **ritmo** | pausas > 0,45s encurtadas; **1,25x sempre** |
| **cor** | look `natural` (contraste leve, verde da parede −25%) |
| **legenda** | Nunito ExtraBold, branca, traço `#030303` — no `brand.json` ficam `size 32` e `stroke 6` **na escala de 480px**; o render sai com **72px** e traço **8px** (limitado pela contraforma) em 1080. Nunca escreva 72 no brand.json. Posição: 60% da altura, ≤4 palavras, 1 linha, minúsculas, sem ponto final |
| **logo** | `logo/logo-branco.png`, 200px de largura, centralizado, 80px do topo, sombra suave |
| **rodapé** | `fine-print.txt` verbatim, Nunito SemiBold 21px, centralizado, sobre degradê escuro |
| **trilha** | `urgencia-126bpm-a.mp3` a −27 (≈18 dB abaixo da voz no CTA); hit final na última palavra |
| **efeitos** | A: riser → dropout → impact no prêmio · B: impact no gancho, downer em "está fora", toque no CTA · C: ding no "número da sorte", tic-tac nos prazos |

## Muda por campanha — confira antes de cada vídeo novo

- `fine-print.txt`: período de participação (**20/06/2026 a 27/09/2026**), data do sorteio
  (**30/09/2026**), processo SUSEP;
- `captions.keep_together`: valor do prêmio e datas ditas no roteiro ("25 mil reais", "dia 30",
  "30 de setembro", "23h59").

## Não muda (regra de identidade da marca)

Cor, tipografia, logo. Pedido que implique mudar é quase sempre mal-entendido — confirme.
