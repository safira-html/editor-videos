# 03 — Legenda

O padrão vem de um cofre de notas privado do autor ("o cofre" nas tabelas abaixo; a regra de legenda
foi fechada em 2026-09-14 e não está neste repositório — o que vale está aqui), adaptado para vídeo com
gente real. Os valores moram em `brands/clube-da-virada/brand.json → captions`.

## O set do Clube da Virada

| | Valor | De onde |
|---|---|---|
| fonte | **Nunito ExtraBold** (variável; `brands/clube-da-virada/fonts/Nunito.ttf`) | cofre |
| corpo | 32px num quadro de 480×854 → **72px** em 1080×1920 | cofre, escalado ×2,25 |
| posição | centro em X · **60% da altura** | cofre. Cai no peito do apresentador sentado e fora da zona de UI de baixo do Reels |
| cor | **branco** `#FFFFFF`, traço `#030303` | as cores do cofre são de personagem; aqui não há personagem |
| traço | pedido 6 (em 480) → **8px** medidos | 🚨 a trava da contraforma limita (abaixo) |
| palavras por bloco | até **4**, sempre **1 linha** (máx. 87,5% da largura) | cofre |
| tempo mínimo | **0,55s** na tela | cofre |
| tipografia | **inicial minúscula** (exceto nome próprio) e **nunca ponto final** (`?` `!` e vírgula ficam) | cofre, decisão da Safira |

## 🚨 A trava da contraforma

O traço do Pillow dilata o glifo para todos os lados e o buraco do `o` fecha. O script desenha um
`o`, mede os pixels transparentes e usa **o maior traço que deixa ≥25% do buraco**. Não baixe o
valor na config: ela guarda a intenção, o render aplica o possível. (Medição original do cofre:
corpo 32, traço 6 deixava 5% do buraco.)

## Por que Pillow e não ASS/libass

Um editor anterior do autor queimava legenda com ASS/libass. Aqui a fonte é **variável** e o peso ExtraBold é uma
instância nomeada — o Pillow escolhe (`set_variation_by_name`) e mede a largura exata para garantir
1 linha. Cada bloco vira um PNG transparente; a sequência entra por `concat` com duração e
`overlay`.

## A quebra dos blocos — programação dinâmica, não gulosa

A primeira versão (gulosa, 4 palavras e pronto) produziu "faltam três dias **pra** / fechar o prazo
**pra**" e "toca no botão **Responda** / a Pesquisa". A atual quebra cada frase no ponto de **menor
custo**:

| penalidade | quando |
|---|---|
| +6 | bloco termina em palavra fraca (`pra`, `de`, `o`, `a`, `um`, `no`, `por`, `e`, `que`, `não`, `mais`…) |
| +20 | separa uma **unidade travada** (`keep_together`) |
| +4 | vírgula no meio do bloco (vírgula é quebra **preferida**, não obrigatória — senão "respondeu," fica sozinho) |
| +3 | bloco de 1 palavra |
| + | desequilíbrio de tamanho |

Frase = até `.` `?` `!` ou pausa > 0,65s. Um bloco nunca atravessa duas frases.

**`keep_together` do Clube** (no brand.json): `Responda a Pesquisa`, `25 mil reais`, `25 mil`,
`23h59`, `dia 30`, `número da sorte`, `números da sorte`, `Clube da Virada`, `30 de setembro`,
`meia-noite`. Expressão nova da campanha que quebrou no `--dry` → acrescente lá.

## Nome próprio

Maiúscula **fora de início de frase** na transcrição = nome próprio (regra do cofre), somada à lista
fixa `proper_nouns` (`Clube`, `Virada`). Assim `Responda a Pesquisa` (nome do botão) fica com
maiúscula e `Dia 30,` vira `dia 30,`.

🚩 **Não copie a lista fixa do cofre inteira:** ela inclui `são` (de São Paulo) e faria "são dez
perguntas" sair "São dez perguntas". Por isso aqui a lista é só da marca.

## Correções de texto

- `captions.text_fixes` no plan.json: `[{"from": "11h59", "to": "23h59", "why": "…"}]` — aplicado
  depois da tipografia. Use para erro do Whisper **e** para fato falado errado (avisando).
- Whisper às vezes quebra hifenizada em dois tokens (`meia` + `-noite,`) — o script junta sozinho.
- Sem blink: se o vão entre dois blocos é < 0,25s, o anterior fica até o próximo entrar.

## O `.srt`

Sai ao lado do `.mp4`, com o mesmo texto e tempo dos blocos queimados — para gerenciador de anúncio
que pede legenda em arquivo.
