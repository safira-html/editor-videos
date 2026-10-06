# 02 — Cortes: o que sai e onde cortar

**A transcrição diz O QUE foi falado; o silêncio medido diz ONDE cortar.** Nunca corte no tempo do
Whisper sem encostar no silêncio — ele erra a borda da palavra em até ~0,2s e o corte decapita a
sílaba.

## O que sai (decisão editorial, lendo `transcript.txt`)

| Sai | Exemplo real |
|---|---|
| claquete / conversa de set | C2556 0–13,9s ("isso é bem emergência, né? … beleza"); C2557 "Oi câmera, esse aqui é o segundo AD… 1, 2, 3, ação!" |
| sobra depois da última fala do roteiro | C2556 depois de "estamos torcendo por você!" ("bora, vocês garantiram o lugar?") |
| falso início | C2558 51,96s "Responda uma rápida…" (retomado em 54,60s) |
| take repetido — **fica o último completo** | C2558: 1º take do fecho termina em "e… Bora!"; ele pede "quer fazer isso de novo?" → fica o 2º (96,4s). C2559: "acho que essa parte dá pra fazer de novo" → fica o 2º "Dia 30…" (41,9s) |
| comentário no meio | C2559 55–65,6s ("ah, não, falta mais coisa… vou jogar um…") |
| **pausa longa** | automático: toda pausa > `max_pause` (0,45s) vira ~0,25s (0,15s depois da fala + 0,10s antes da próxima) |

**Registre o porquê** no campo `_keep` do plan.json. É o que permite a outra pessoa (ou outra
sessão) entender a edição sem assistir ao bruto.

## Como o script corta

1. `ffmpeg silencedetect` a −35 dB, mínimo 0,18s, sobre `audio16k.wav`;
2. cada borda de `keep` encosta no silêncio mais próximo (até 0,35s de distância), com 0,10s de
   respiro antes da fala e 0,15s depois;
3. dentro de cada take, pausas > 0,45s são encurtadas;
4. cada trecho ganha **fade de 12 ms** no áudio (sem estalo na emenda);
5. concat → `setpts=PTS/1.25` + `atempo=1.25` (a voz acelera sem mudar o tom).

No C2556: 63s de bruto → 10 trechos → 38,3s → **30,6s** a 1,25x.

## Jump cut

Em anúncio falado, o pulo de imagem na emenda é aceito — é a linguagem do formato. Não tente
esconder com zoom ou transição: nada disso foi pedido e o aprovado não tem.

## Palavras da legenda depois do corte

Uma palavra entra na legenda se o meio dela cai num trecho mantido **com folga de 0,15s** (a borda
do Whisper erra). Palavra de um take cortado fica fora automaticamente.
