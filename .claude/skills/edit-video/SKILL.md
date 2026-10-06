---
name: edit-video
description: Edita um vídeo curto de anúncio com apresentador (cortes, 1,25x, cor, legenda, logo, letras miúdas, som). Use quando a pessoa disser "edita o vídeo", "edita o C25xx", "corta esse vídeo", "faz variações do vídeo", "gera versões com ganchos diferentes" ou mandar um bruto para editar.
---

# Editar um vídeo

Este skill só roteia; o método está nos docs. Leia **CLAUDE.md** (travas) e siga
**docs/01-fluxo-de-edicao.md** do começo ao fim.

1. Marca: `./ev brand --list`. **Não existe?** use o skill `new-brand` (docs/09) antes de editar.
2. `./ev setup --check` se for a primeira vez nesta máquina (falhou → `./ev setup`).
3. `./ev transcribe <bruto> projects/<marca>/<ID>` → leia `transcript.txt` → `plan.json`
   (a partir de `projects/_template/plan.json`; docs/02-cortes.md; **último take completo**).
4. `./ev edit <plan.json> --dry` (legenda) → plano de som (docs/05-som.md) → `./ev edit <plan.json>`.
5. `./ev qa output/<marca>/<arquivo>.mp4 --sheet` — reprovado não sobe. Mande o vídeo com medições.
6. Ajustes viram `_v2`, `_v3`; estilo de marca vai no `brand.json`; registre em docs/aprendizados.md.

Pediu **variações** (ganchos/corpos/CTAs), sem legenda, sem som, outro tamanho ou mais/menos trilha?
Leia **docs/08-variacoes-e-saidas.md**; em variações, mostre a tabela de opções e **confirme antes de renderizar**.

Som novo custa crédito (ElevenLabs): só com permissão, `estimate_only` antes (trava 2).
