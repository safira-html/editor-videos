# Editor de vídeos curtos — leia isto antes de qualquer coisa

Este repositório edita **vídeos curtos de anúncio com apresentador**: corta erros (claquete, falso
início, take repetido, pausa longa), acelera, corrige cor, legenda, põe logo e letras miúdas, e
sonoriza (trilha + efeitos). Tudo o que se aprendeu para chegar à qualidade aprovada está **dentro
desta pasta** (`docs/`) — não dependa de memória de conversa. Comandos pelo atalho `./ev`
(`./ev --help`). Máquina nova: `./ev setup` primeiro.

## Se alguém pedir "edita o vídeo X"

```
marca existe? → transcrever → decidir cortes (lendo a transcrição) → plan.json → --dry (legenda) →
plano de som → render → QA da máquina → mandar o vídeo → ajustar pelo que a pessoa disser
```

1. **A marca existe em `brands/`?** (`./ev brand --list`; descubra pela copy.) **Se não existe →
   [docs/09-onboarding-de-marca.md](docs/09-onboarding-de-marca.md)** (entrevista curta, uma pergunta
   por vez, preview sobre um quadro real) antes de qualquer edição.
2. Siga **[docs/01-fluxo-de-edicao.md](docs/01-fluxo-de-edicao.md)** do começo ao fim. O estilo da
   marca está em `brands/<marca>/brand.json` e **não se rediscute por vídeo**.
3. Crie `projects/<marca>/<ID>/`, transcreva, e escreva o `plan.json` a partir de
   `projects/_template/plan.json`.
4. **A pessoa pediu saída sob medida?** Variações (2 ganchos × 2 corpos × 2 CTAs…), sem legenda,
   sem som, outra velocidade, mais/menos trilha → **[docs/08-variacoes-e-saidas.md](docs/08-variacoes-e-saidas.md)**
   (`./ev variants`). Variações: mostre a tabela de opções e a contagem e **peça confirmação antes de renderizar**.
5. Entregue **cedo** e com medições. A pessoa itera por frases curtas ("trilha mais baixa",
   "metade do tamanho") — aplique, gere nova versão (`_v2`, `_v3`…), nunca sobrescreva a anterior.

## As travas

1. **Não mexa em pastas fora desta** (o repositório). Material de outras pastas é só leitura; o que
   for útil é **copiado** para cá.
2. 💸 **Geração paga só com permissão.** Trilha e efeito novos saem do ElevenLabs e custam crédito.
   Antes: `estimate_only` (grátis), diga **o que** vai gerar, **quanto** custa e o saldo (o conector
   não mostra saldo — diga isso), e **espere o sim**. Primeiro procure na biblioteca da marca
   (`brands/<marca>/sound/SONS.md`); marca nova → [STARTER-KIT](brands/_template/sound/STARTER-KIT.md).
   Ver [docs/05-som.md](docs/05-som.md).
3. **O estilo da marca não muda por vídeo.** Fonte, legenda, look, velocidade (1,25x), logo, letras
   miúdas e níveis de som moram no `brand.json`. Pedido que mude isso vale para a marca inteira —
   confirme e atualize o `brand.json`, não só o vídeo.
4. **Letras miúdas são texto legal: verbatim.** Nunca parafraseie. As datas da campanha mudam —
   pergunte se o texto de `brands/<marca>/fine-print.txt` ainda vale antes de um vídeo novo de outra fase.
5. **A legenda escreve o fato certo; o áudio não se conserta.** Se o apresentador fala um dado errado
   (ex.: "11h59" quando o prazo é 23h59), corrija a legenda com `captions.text_fixes` e **avise** que
   o áudio continua errado. Não invente correção sem a pessoa confirmar o dado.
6. **QA da máquina antes de mandar:** `./ev qa <vídeo> --sheet`. Reprovado não sobe.
7. **Correção que a pessoa faz vira documento, na mesma sessão:** registre em
   [docs/aprendizados.md](docs/aprendizados.md) e conserte onde mora (brand.json, doc ou script).
8. **Nenhum caminho de máquina fora do `config.json`.** **Segredo nenhum entra em arquivo** (chave de
   API, token, senha) — nem em plano, nem em doc, nem em commit.

## Onde está cada coisa

| | |
|---|---|
| [README.md](README.md) | o que é, início rápido, mapa do repositório |
| [docs/](docs/) | o como-fazer de cada etapa + [aprendizados](docs/aprendizados.md) |
| `brands/<marca>/` | estilo fixo da marca: `brand.json`, fonte, logo, letras miúdas, `sound/SONS.md` |
| `projects/<marca>/<ID>/` | um vídeo: `plan.json`, transcrição, intermediários (fora do git) |
| `output/<marca>/` | vídeos prontos (`<ID>_editado_vN.mp4` + `.srt`; fora do git) |
| `scripts/` | `setup.py`, `transcribe.py`, `edit.py`, `variants.py`, `tick_bed.py`, `audio_tools.py`, `qa.py`, `new_brand.py`, `venv_run.py` |
| `examples/plans/` | três `plan.json` reais, sanitizados |
| `config.json` | o único arquivo que muda por máquina (criado por `./ev setup`; fora do git) |
