# 09 — Onboarding de marca: o roteiro do assistente

Use quando o pedido é de uma marca que **não existe** em `brands/` (confira com `./ev brand --list`)
ou quando a pessoa diz "nova marca". É uma entrevista curta: **uma pergunta por vez**, cada uma com
um padrão sensato e o que conferir. Nunca despeje o questionário inteiro. Se a pessoa já mandou
parte das respostas (logo, fonte, cores), pule essas perguntas e confirme em uma frase.

No fim, o estilo fica em `brands/<slug>/brand.json` e **não se rediscute por vídeo** (trava 3 do
[CLAUDE.md](../CLAUDE.md)). Por isso vale acertar agora, olhando a imagem.

> Antes de começar, uma pergunta de contexto: **existe um vídeo bruto de exemplo** desta marca?
> Sem ele não dá para fixar a posição da legenda (pergunta 6) nem ver o preview. Se não existir,
> faça as perguntas, crie a marca com o padrão `seated` e avise que a posição é provisória.

## A entrevista

### 1. Nome e slug

- Pergunte: *"Qual o nome da marca?"* O slug sai dele: minúsculas, sem acento, hífen no lugar de
  espaço (`Quero Card` → `quero-card`). Confirme em uma linha.
- Confira: `./ev brand --list` para não colidir com uma marca existente (o script recusa sem
  `--force`).
- O nome escrito certo importa: o Whisper costuma errar nome de marca ("Allevo Tech" saiu
  "Levotec"). Pergunte **como se fala** e anote para os `text_fixes` dos primeiros vídeos.

### 2. Logo

- Pergunte: *"Mande o logo em PNG com fundo transparente. Qual versão contrasta com o fundo dos
  vídeos?"* Fundo escuro (parede, estúdio escuro) → versão **branca ou monocromática clara**;
  fundo claro → a escura. O Clube usa o branco porque o fundo é uma parede verde escura.
- Confira (o script mede e imprime): transparência (PNG sem alfa mostraria uma caixa sólida — o
  script recusa), **proporção** e luminância dos pixels visíveis (logo escuro em fundo escuro
  some).
- Proponha a **largura** pela proporção: altura visual ~90px, largura entre 160 e 340px. Wordmark
  horizontal 5:1 → 340px; logo médio 2,2:1 (o do Clube) → 200px; quadrado → 160px. O script já
  sugere esse valor; confirme com a pessoa só se ela tiver preferência. O logo fica centralizado,
  80px do topo.
- Sem logo? Tudo bem: a marca nasce sem o bloco `logo` e o vídeo sai sem.

### 3. Fonte da legenda

- Pergunte: *"Qual a fonte da marca? Se tiver o arquivo `.ttf`/`.otf`, me diga o caminho; se for
  uma família do Google Fonts, só o nome."*
- **Arquivo:** use o caminho dele.
- **Família do Google Fonts** (ex. Poppins): peça **permissão** para baixar o `.ttf` de
  `github.com/google/fonts` (licença OFL — a Poppins do Quero Card veio assim). Diga o nome do
  arquivo, a origem e o tamanho antes de baixar. Fonte estática: baixe o arquivo do **peso certo**
  (`Poppins-SemiBold.ttf`). Fonte variável: um arquivo só, e o peso é uma instância nomeada.
- **Peso:** pergunte (padrão `Bold`; o Clube usa `ExtraBold`, Allevo e Quero `SemiBold`). Em fonte
  variável o script confere se o nome é uma instância real e lista as disponíveis; em fonte
  estática o peso vem do arquivo e `--weight` só é registrado.
- Legenda de anúncio pede peso **forte** (SemiBold ou mais): com traço preto, peso leve vira
  borrão.

### 4. Cores da legenda

- Pergunte: *"Qual a cor de destaque da legenda?"* Padrão: **branco `#FFFFFF`** se a marca não tiver
  cor forte; senão, a cor de destaque da marca (Allevo `#00FFBB`, Quero Card `#A6F200`).
- **Traço:** padrão `#030303` — não pergunte, só avise.
- Confira o contraste do preenchimento sobre o traço (o script imprime; abaixo de 4,5:1 ele avisa).
  Vermelho/azul escuros sobre traço preto perdem; clareie o preenchimento ou escureça o traço.
  O teste final é o preview sobre o vídeo real.

### 5. Letras miúdas

- Pergunte: *"Esta marca tem texto legal obrigatório no rodapé? Se sim, cole **exatamente** como o
  jurídico mandou."* Padrão: **sem letras miúdas**.
- 🚨 **Verbatim.** Nunca parafraseie, resuma, corrija ortografia ou "melhore". Salve o texto como
  veio num `.txt` (`--fine-print-file`); o script copia os bytes. Quebra de linha antes de um
  trecho é permitida (não muda palavra).
- Pergunte **as datas da campanha** (participação, sorteio, vigência): elas mudam de fase para fase
  e vão para `brands/<slug>/README.md` na seção "Muda por campanha", para o assistente perguntar
  de novo antes de cada vídeo de outra fase.

### 6. Enquadramento — e olhar um quadro antes de fixar a posição

- Pergunte: *"Como o apresentador aparece? (a) sentado, plano médio · (b) selfie, rosto grande no
  centro · (c) close-up."* Isso escolhe a posição da legenda (`captions.pos_y`):

  | enquadramento | `--framing` | `pos_y` | por quê |
  |---|---|---|---|
  | sentado, plano médio | `seated` | 60% | cai no peito e fora da zona de interface de baixo do Reels (Clube) |
  | selfie | `selfie` | 69% | o rosto ocupa o meio; a legenda desce |
  | close-up | `closeup` | 75% | idem, mais baixo ainda |

  O logo fica a 80px do topo nos três; confira que não encosta na cabeça.
- 🚩 **SEMPRE extraia um quadro de um vídeo de exemplo e olhe** antes de fixar `pos_y`:
  ```bash
  ffmpeg -ss 8 -i ~/Downloads/<ID>.MP4 -frames:v 1 quadro.png
  ```
  e abra a imagem (o criador de marca da etapa seguinte também gera um preview com legenda,
  logo e rodapé sobre esse quadro). Procure: a legenda cai no peito, sem cobrir a boca? O logo está acima da
  cabeça? O rodapé de letras miúdas não cobre mãos/objeto importante? O vídeo é 9:16? (o
  `edit.py` escala para 1080×1920 **sem cortar**: bruto de outra proporção sai esticado — o script
  de marca avisa.) Ajuste `--pos-y` com o que viu.

### 7. Look de cor

- Pergunte: *"Quer correção de cor? Posso mostrar as opções lado a lado."* Padrão: **`none`**
  (sem correção). Ofereça **`natural`** (contraste leve; a marca do Clube usa).
- Se ela quiser escolher: mostre `none`, `natural`, `warm_neutral`, `punch` **na mesma imagem**,
  rotulados, em mais de um momento do vídeo, sem opinar antes ([04-cor.md](04-cor.md)). O look
  muda a cor do vídeo inteiro — olhe o rosto e o fundo.

### 8. Velocidade

- Pergunte: *"Aceleramos o vídeo? Os aprovados rodam a **1,25x**."* Padrão: 1,25 (voz acelerada
  sem mudar o tom). `1.0` desliga. Fica no `brand.json` para a marca inteira.

### 9. Identidade sonora

- Pergunte: *"Que sensação o som deve passar? (urgência · tecnologia/progresso · cuidado/acolhimento ·
  outra)"* e o assunto do anúncio. Isso define o **humor e o BPM** da trilha
  (126 / 112 / 100 BPM nos exemplos) — molde e exemplos em
  [`brands/_template/sound/STARTER-KIT.md`](../brands/_template/sound/STARTER-KIT.md).
- **Geração é paga e só com permissão.** Antes: `estimate_only` (grátis), diga **o que** vai gerar
  (trilha: 1.641,41 cr por variação; cada efeito 50 cr × 2 variações), **quanto** custa e que o
  conector **não mostra saldo**. **Espere o sim.** Não pergunte "posso gerar?" no meio da entrevista:
  conclua a marca primeiro e proponha o som na etapa 4 de "Preview, iteração e registro".
- Sem verba/permissão? A marca fica sem som próprio; o vídeo sai só com a voz (ou reaproveite
  efeitos de outra marca do repositório, sem custo). `music_presence` padrão é 0.

## Criar a marca

Com as respostas em mãos, **um comando**:

```bash
./ev brand --slug minha-marca --name "Minha Marca" \
    --logo ~/Downloads/logo-branco.png \
    --font ~/Downloads/Poppins-SemiBold.ttf --weight SemiBold \
    --fill '#A6F200' --stroke '#030303' \
    --fine-print-file ~/Downloads/letras-miudas.txt \
    --look none --framing seated --speed 1.25 \
    --frame ~/Downloads/C0001.MP4 --at 8
```

Todas as flags e os padrões: `./ev brand --help`. Mesmos campos em JSON:
`./ev brand --answers respostas.json` (chaves = nome das flags com `_`; caminhos relativos valem a
partir da pasta do JSON; flags da linha de comando vencem o JSON).

O script **copia** `brands/_template` → `brands/<slug>`, copia logo e fonte, escreve o
`brand.json` e **valida**: cores hex, fonte abre no Pillow, peso é instância nomeada (fonte
variável), logo tem transparência (e imprime a proporção), arquivo de letras miúdas existe.
Recusa sobrescrever marca existente sem `--force` (e nunca apaga sons). Cria também um
`README.md` e um `sound/SONS.md` de rascunho.

## Preview, iteração e registro

1. **Mostre o `brands/<slug>/preview.png`** (quadro real + legenda de exemplo + logo + letras
   miúdas, desenhados pelas mesmas funções do `edit.py`). Pergunte o que mudaria — **uma coisa de
   cada vez**. Para ajustar um valor, edite o `brand.json` (por exemplo `captions.pos_y` ou
   `logo.width`) e refaça **só o preview**, sem recriar a marca:
   ```bash
   ./ev brand --slug minha-marca --preview-only --frame ~/Downloads/C0001.MP4 --at 8
   ```
   Para trocar logo, fonte ou cor, rode de novo o comando de criação com `--force` (ele regrava o
   `brand.json` a partir das flags — perde edições manuais — e nunca apaga sons). O preview não é
   um vídeo: mostra posição e estilo, não o timing.
2. Ajustes finos (`captions.keep_together`, `proper_nouns`, `logo.width`…) vão direto no
   `brand.json` — referência de campos em [07-plan-json.md](07-plan-json.md).
3. **Registre as decisões**: preencha `_por_que` no `brand.json` com o motivo de cada escolha
   (o script já deixa o rascunho), e complete `brands/<slug>/README.md` ("o estilo em uma tela" +
   "Muda por campanha"), como os das marcas existentes. Se a pessoa corrigiu algo durante a
   entrevista, também em [aprendizados.md](aprendizados.md) (trava 7).
4. **Som**: só agora, com permissão, gere o kit básico do
   [STARTER-KIT](../brands/_template/sound/STARTER-KIT.md), meça tudo (`./ev audio inspect`) e
   registre em `brands/<slug>/sound/SONS.md`.
5. Volte ao [fluxo de edição](01-fluxo-de-edicao.md) e edite o primeiro vídeo. **Entregue cedo**:
   o primeiro render é a prova final do estilo; o `--dry` já mostra a quebra da legenda (marca com
   nome composto costuma precisar de `keep_together`).

## Resumo da ordem

```
./ev brand --list → perguntas 1–9 (uma por vez) → ./ev brand ... --frame ... → preview.png →
ajustes (brand.json + --preview-only) → _por_que + README da marca → (com permissão) som → primeiro vídeo (docs/01)
```
