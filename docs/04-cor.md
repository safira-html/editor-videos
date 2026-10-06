# 04 — Cor

## O material

Câmera Sony, **H.264 8 bits, Rec.709** (`color_transfer=bt709`), não log. Então o grading é
**criativo e suave** — não há conversão de perfil, e 8 bits não aguenta curva forte (banding).

## Os três looks (em `scripts/edit.py → LOOKS`)

Foram mostrados lado a lado com o original, em dois frames (20s e 45s), e a Safira escolheu o **A**
em 2026-09-24. A imagem da comparação está em `projects/clube-da-virada/C2556/grade/compare.jpg`.

| look | filtro | o que faz |
|---|---|---|
| **`natural`** ✅ | `eq` contraste 1,06 · brilho −0,01 · sat 1,05 + `colorbalance` meio-tom +R −B + `huesaturation` verde/amarelo −25% | quase o original, com um pouco mais de corpo; a parede verde recua |
| `warm_neutral` | curva S suave + meio-tom quente + verde −35% | o único ancorado no cofre ("warm-neutral color grading" do Canon Visual); mais escuro |
| `punch` | curva mais forte + saturação 1,12 + vibrance + nitidez | pele puxa para o laranja, roxos saturam |

**Por que tirar saturação do verde em todos:** o fundo é uma parede de plantas verde e roxa que
compete com o rosto. Descolorir só o verde faz o apresentador saltar sem mexer na pele.

⚪ **O que nenhum look resolve:** há um vazamento de LED verde no lado esquerdo do rosto/pescoço
(visível no original). Corrigir exigiria máscara localizada — não foi pedido.

## Como mostrar uma escolha de cor

Escolha entre saídas boas vai **lado a lado, na mesma imagem**, com o original, rotulada, em mais de
um momento do vídeo — e sem a sua opinião na frente (princípio do cofre). Gere os stills a partir
do bruto em 540×960 e aplique cada filtro do dicionário `LOOKS`.

O look aplicado sai no `brand.json` (`"look": "natural"`). Look novo → acrescente ao dicionário, não
edite um existente que já foi aprovado.
