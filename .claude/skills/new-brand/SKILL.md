---
name: new-brand
description: Cria uma marca nova (onboarding de marca) para os vídeos de anúncio. Use quando a pessoa disser "nova marca", "onboarding de marca", "cadastra a marca X", "configura a marca", ou pedir uma edição de uma marca que não existe em brands/.
---

# Onboarding de marca

Este skill só roteia; o roteiro completo está em **docs/09-onboarding-de-marca.md**. Entrevista curta,
**uma pergunta por vez**, cada uma com padrão sensato:

nome/slug → logo (PNG transparente; versão que contrasta com o fundo) → fonte (arquivo ou Google
Fonts, com permissão para baixar) e peso → cores da legenda (traço `#030303`) → letras miúdas
(**verbatim**; datas da campanha) → enquadramento (**extraia e olhe um quadro** antes de fixar `pos_y`)
→ look (`none`; ofereça `natural`) → velocidade (1,25x) → identidade sonora (geração paga só com permissão).

Depois:

```bash
./ev brand --list
./ev brand --slug <slug> --name "<Nome>" --logo <png> --font <ttf> --weight <Peso> --fill '#RRGGBB' \
    --fine-print-file <txt> --framing seated --frame <bruto.MP4> --at 8
./ev brand --slug <slug> --preview-only --frame <bruto.MP4> --at 8   # refaz só o preview após editar o brand.json
```

Mostre `brands/<slug>/preview.png`, itere, registre as decisões em `brand.json` (`_por_que`) e em
`brands/<slug>/README.md`, e só então siga para o skill `edit-video`. Som da marca nova:
`brands/_template/sound/STARTER-KIT.md` (custo + `estimate_only` + permissão).
