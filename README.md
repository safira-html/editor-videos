# editor-videos

**English summary.** A Claude Code project that edits short talking-head ad videos by script: it cuts
mistakes (slates, false starts, repeated takes, long pauses), speeds up to 1.25x, color-corrects,
burns captions, logo and fine print, and adds music and sound effects. One folder per **brand**
(fixed style) and one per **video**. You clone it, run `./ev setup`, open it in Claude Code and say
*"edita o vídeo X"*; for a brand that does not exist yet, the assistant interviews you
([docs/09](docs/09-onboarding-de-marca.md)). Everything is local and free except the optional
sound generation (ElevenLabs, paid, always asked first). The docs and the assistant's dialogue are in
Brazilian Portuguese; the code is in English. Limits: single-presenter vertical (9:16) ads, Portuguese
transcription by default. MIT license.

---

Edição simples de vídeo curto de anúncio com apresentador, dirigida pelo Claude Code. Você grava, o
assistente lê a transcrição, decide os cortes, e o script entrega o vídeo pronto com a qualidade dos
exemplos aprovados.

## Antes e depois

| bruto | editado |
|---|---|
| 1–2 min com claquete, "peraí, de novo", falso início, o mesmo trecho gravado três vezes e pausas longas | ~30s, só o último take completo de cada trecho, pausas encurtadas, **1,25x** com a voz sem mudar de tom |
| 4K deitado (rotação −90°) sem cor trabalhada | 1080×1920, look de cor suave, −14 LUFS |
| sem legenda, logo nem rodapé | legenda queimada (≤4 palavras, 1 linha, quebra inteligente), logo no topo, letras miúdas verbatim no rodapé, `.srt` ao lado |
| só a voz | trilha no BPM do assunto + efeitos nos momentos certos (riser → silêncio → impact no ponto principal) |

## Requisitos

- macOS ou Linux (Windows: use WSL). Não há suporte a Windows nativo.
- [Claude Code](https://claude.com/claude-code).
- `ffmpeg` e `ffprobe` (`brew install ffmpeg` / `sudo apt install ffmpeg`).
- Python 3.9–3.13 (de preferência 3.11 ou 3.12; no 3.14 pode faltar pacote pronto). O `./ev setup` cria
  o ambiente com `faster-whisper`, `numpy` e `pillow` — você não instala nada à mão.
- Disco: ~2 GB (ambiente Python ~250 MB + modelo do Whisper ~1,6 GB) e espaço para os brutos 4K.
- CPU basta (transcrição ~1 min por minuto de bruto, no modelo `large-v3-turbo`, `int8`). Render: ~1 min
  para 30s de vídeo.

## Início em 5 minutos

```bash
git clone https://github.com/safira-html/editor-videos.git
cd editor-videos
./ev setup                      # confere o ffmpeg, cria o ambiente Python, escreve o config.json
./ev setup --download-model     # opcional: baixa o modelo do Whisper (~1,6 GB, precisa de internet)
```

Depois, **abra a pasta no Claude Code** e peça:

> edita o vídeo C2560

Ele identifica a marca pela copy, transcreve, decide os cortes, mostra a legenda (`--dry`), sonoriza,
renderiza, passa o QA e manda o `.mp4`. Você itera em frases curtas ("trilha mais baixa", "logo na
metade do tamanho") e cada ajuste vira `_v2`, `_v3`…

**Primeira vez com uma marca nova?** O assistente faz uma entrevista curta (logo, fonte, cores,
letras miúdas, enquadramento, som), mostra um preview sobre um quadro do seu vídeo e só então edita.
Roteiro: [docs/09-onboarding-de-marca.md](docs/09-onboarding-de-marca.md). Ou você mesmo:
`./ev brand --help`.

O repositório já traz **três marcas reais** como exemplo (Clube da Virada, Allevo Tech, Quero Card) —
estilo, fonte, logo e a biblioteca de sons documentada em cada `SONS.md`, mas **sem os arquivos de
áudio**. Planos de exemplo em [`examples/`](examples/README.md).

## Como ele decide os cortes

A transcrição diz **o que** foi falado; o silêncio medido diz **onde** cortar.

1. Whisper com tempo por palavra e **VAD desligado** (para enxergar claquete e takes repetidos).
2. O assistente lê o `transcript.txt` e marca os takes que ficam: claquete e conversa de set saem,
   falso início sai, **take repetido: fica o último que a pessoa completou**, comentário no meio sai.
3. Cada borda de corte encosta no silêncio mais próximo (o Whisper erra a borda em até ~0,2 s);
   pausa > 0,45 s é encurtada; emenda com fade de 12 ms.
4. O porquê de cada trecho fica no campo `_keep` do `plan.json`.

Detalhes: [docs/02-cortes.md](docs/02-cortes.md).

## Comandos

Tudo por `./ev` (que escolhe o Python certo):

```bash
./ev setup [--check] [--download-model]            # preparar / conferir a máquina
./ev transcribe ~/Downloads/C2560.MP4 projects/minha-marca/C2560
./ev edit projects/minha-marca/C2560/plan.json --dry      # só mostra os blocos de legenda
./ev edit projects/minha-marca/C2560/plan.json            # render completo
./ev edit projects/minha-marca/C2560/plan.json --remix    # refaz só o som (reusa corte e legenda)
./ev qa output/minha-marca/C2560_editado_v1.mp4 --sheet   # QA da máquina + folha de contato
./ev audio inspect|beat|vocals|words|mix ...              # medições de som
./ev variants projects/minha-marca/C2560/plan.json --list # combinações gancho × corpo × CTA
./ev brand --list                                         # marcas existentes; ./ev brand --help cria uma
```

## Saídas sob medida

Peça na hora do pedido: **variações combinatórias** (2 ganchos × 2 corpos × 2 CTAs = 8 vídeos de uma
gravação só), outra velocidade, sem legenda, sem som, sem logo, mais ou menos trilha, várias versões.
O que existe e o que não existe: [docs/08-variacoes-e-saidas.md](docs/08-variacoes-e-saidas.md).

## Mapa do repositório

```
editor-videos/
├── ev                         ← atalho para tudo (./ev setup | transcribe | edit | variants | qa | audio | brand)
├── CLAUDE.md                  ← regras (travas) e como atender um pedido
├── config.example.json        ← modelo do config.json (que é local e não vai para o git)
├── .claude/skills/            ← edit-video e new-brand: atalhos do Claude Code para os docs
├── docs/
│   ├── 01-fluxo-de-edicao.md  ← o passo a passo, com os comandos
│   ├── 02-cortes.md           ← como decidir o que sai
│   ├── 03-legenda.md          ← padrão tipográfico e regras de quebra
│   ├── 04-cor.md              ← os looks de cor
│   ├── 05-som.md              ← trilha, efeitos, hierarquia, mixagem e geração
│   ├── 06-marcas.md           ← o que é da marca e o que é do vídeo
│   ├── 07-plan-json.md        ← referência de todos os campos
│   ├── 08-variacoes-e-saidas.md  ← variações combinatórias e outras saídas
│   ├── 09-onboarding-de-marca.md ← a entrevista de marca nova
│   └── aprendizados.md        ← histórico de correções e descobertas, com data
├── brands/
│   ├── _template/             ← ponto de partida + sound/STARTER-KIT.md
│   └── clube-da-virada · allevo-tech · quero-card/   ← brand.json · fonts/ · logo/ · sound/SONS.md
├── projects/_template/        ← plan.json modelo (cada vídeo seu vira projects/<marca>/<ID>/, fora do git)
├── examples/plans/            ← três plan.json reais, sanitizados
└── scripts/                   ← setup · transcribe · edit · variants · tick_bed · audio_tools · qa · new_brand · venv_run
```

`projects/<marca>/<ID>/` (transcrição, intermediários) e `output/` (vídeos prontos) são locais:
o `.gitignore` os deixa fora do repositório, assim como todo `.mp3`, `.wav`, `.mp4`, `.mov`.

## Custos

- **Grátis e local:** transcrição, corte, cor, legenda, logo, letras miúdas, mixagem, QA, variações.
- **Opcional e pago — geração de som (ElevenLabs):** trilha ≈ 1.641 créditos por variação, efeito
  = 50 créditos por variação (medido em 2026-09-24/25). O assistente **nunca gera sem permissão**:
  mostra o que vai gerar e quanto custa (`estimate_only`, que é grátis) e espera o sim. Exige o
  conector ElevenLabs no seu claude.ai; sem ele, o vídeo sai só com a voz (ou com efeitos que você
  já tenha na pasta da marca). Kit básico e prompts:
  [brands/_template/sound/STARTER-KIT.md](brands/_template/sound/STARTER-KIT.md).

## Limites (honestos)

- Pensado para **anúncio vertical (9:16) com um apresentador falando para a câmera**, gravado em plano
  fixo. Não é um editor geral: não faz B-roll, transição, zoom nem multicâmera.
- **A transcrição é em português** (`language="pt"` fixo em `scripts/transcribe.py`); para outro idioma
  é preciso editar essa linha — não há opção de configuração para isso ainda. As regras de legenda
  (palavras fracas, nomes próprios) também são do português.
- O áudio não se conserta: se o apresentador fala um dado errado, a legenda pode ser corrigida
  (`captions.text_fixes`), a fala não.
- O `edit.py` escala o bruto para o tamanho de saída **sem cortar**: bruto fora de 9:16 sai esticado.
- Não há suporte a Windows nativo.
- As marcas de exemplo foram ajustadas para um cenário e enquadramento específicos (apresentador
  sentado, plano médio, parede de plantas); outro cenário pede outra posição de legenda e logo — é
  o que o onboarding de marca resolve olhando um quadro real.
- O melhor resultado depende do Claude Code seguindo `docs/` e `CLAUDE.md`: a decisão de corte é
  editorial, feita lendo a transcrição.

## Licença e créditos

[MIT](LICENSE) © 2026 safira-html.

Peças de terceiros: `faster-whisper` (MIT) e o modelo `large-v3-turbo` (Whisper, MIT); `ffmpeg`;
`Pillow`; fontes **Nunito**, **Geist** e **Poppins** (SIL Open Font License) em `brands/*/fonts/`.
Os logos e textos legais das três marcas pertencem aos seus donos e estão aqui apenas como exemplo
de configuração. Método de sonorização destilado de um guia de sonoplastia para anúncios e de
experimentos próprios (ver [docs/05-som.md](docs/05-som.md)).
