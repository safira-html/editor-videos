# 06 — Marcas: o que é fixo e como criar uma nova

## A divisão

| mora na **marca** (`brands/<marca>/brand.json`) | mora no **vídeo** (`projects/<marca>/<ID>/plan.json`) |
|---|---|
| fonte, corpo, posição, cor e regras da legenda | quais takes ficam (`keep`) e por quê |
| look de cor, velocidade (1,25x), tamanho de saída | correções de texto (`captions.text_fixes`) |
| logo (arquivo, largura, posição, sombra) | o plano de som (trilha, offset, efeitos, dropouts) |
| letras miúdas (`fine-print.txt` + estilo) | nome da saída (`_vN`) |
| níveis de som padrão, biblioteca de sons | o que foi deixado de fora (`_ausencias`) |

O `edit.py` lê o `brand.json` e mescla o `plan.json` por cima (`deep_merge`): o vídeo **pode**
sobrescrever qualquer campo, mas se o motivo vale para todos, o lugar é a marca.

## Criar uma marca nova

**O caminho curto:** `./ev brand --slug <marca> --font <ttf> ...` (`scripts/new_brand.py`) copia o
template, escreve o `brand.json`, valida e gera um preview sobre um quadro real; o roteiro da
entrevista que o assistente segue está em [09-onboarding-de-marca.md](09-onboarding-de-marca.md).
O passo a passo manual abaixo é o que o script faz:

1. `cp -R brands/_template brands/<nova-marca>` e preencha o `brand.json`.
2. **Fonte:** coloque o `.ttf` em `brands/<nova-marca>/fonts/` e aponte `captions.font_file`. Fonte
   variável: `captions.weight` é o nome da instância (`"ExtraBold"`, `"Bold"`…). Fonte estática: aponte
   para o arquivo do peso certo (ex. `Montserrat-Black.ttf`) — o script usa o arquivo como está.
3. **Logo:** PNG com transparência em `logo/`. Escolha a versão que contrasta com o fundo típico
   do cenário (no Clube: o branco, porque o fundo é parede verde escura).
4. **Letras miúdas:** `fine-print.txt` verbatim do jurídico/cliente. Sem letras miúdas → remova a
   chave `fine_print`.
5. **Look:** comece por `"none"` e mostre as opções lado a lado ([04-cor.md](04-cor.md)).
6. **Som:** comece pela pasta `sound/` vazia. Siga [05-som.md](05-som.md) — trilha nova é geração
   paga, com permissão.
7. Rode um vídeo, itere com a pessoa, e **registre as decisões no brand.json** com `_por_que`.
8. Escreva `brands/<nova-marca>/README.md` (o estilo em uma tela) como o do Clube.

## Coisas que a marca do Clube ensinou e que valem para qualquer marca

- identidade visual não muda por campanha (regra de identidade da marca do Clube) — pedido de mudar é quase sempre
  mal-entendido, confirme;
- a lista de nomes próprios é **da marca**, não herdada de outra (ver o caso "São" em
  [03-legenda.md](03-legenda.md));
- a posição da legenda (60%) e do logo (80px do topo) foi decidida para **apresentador sentado em
  plano médio**. Formato diferente (selfie, rosto no centro) pede outra posição — 69% para selfie e
  75% para close-up são os pontos de partida do onboarding — **sempre confira num quadro real**.
