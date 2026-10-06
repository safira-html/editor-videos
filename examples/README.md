# Exemplos de plan.json

Três `plan.json` reais (de vídeos aprovados), com o caminho do bruto trocado por `~/Downloads/<ID>.MP4`
e as notas de corte (`_keep`) reescritas por categoria (claquete, falso início, take repetido). Servem
de modelo de **como escrever um plano**; não rodam sem o bruto, a transcrição (`words.json`) e os sons
da marca (a pasta `sound/` das marcas traz só o `SONS.md`; o áudio é gerado por quem clona).

Para usar um como molde: copie para `projects/<marca>/<ID>/plan.json`, troque `source`, `keep`
(`_keep` explica o porquê) e os tempos do som. O modelo vazio é `projects/_template/plan.json`.
Campos: [docs/07-plan-json.md](../docs/07-plan-json.md).

| arquivo | marca | o que mostra |
|---|---|---|
| [`plans/clube-da-virada-C2559.plan.json`](plans/clube-da-virada-C2559.plan.json) | Clube da Virada | **método de som antigo (`db`)**: riser → dropout → impact no momento principal, tic-tac de prazo (`tick_bed.wav`), downer em "está fora", dings de recompensa, toque de tela no CTA; trilha que **entra depois** (`from`) porque o vídeo é mais longo que a faixa; `text_fixes` corrigindo um dado falado errado (23h59) |
| [`plans/allevo-tech-C2548.plan.json`](plans/allevo-tech-C2548.plan.json) | Allevo Tech | **método percebido (`presence` e `lu`)**: vários takes descartados até o último completo; `text_fixes` para nome de marca mal transcrito e `regex` com `\\b`; `force_lowercase`; dropouts como piada (a pergunta cai no vazio) |
| [`plans/quero-card-C2553.plan.json`](plans/quero-card-C2553.plan.json) | Quero Card | falso início resolvido pelo take seguinte; `text_fixes` com regex para preço (`R$ 24,90`); `keep_together` no plano (substitui o da marca); tic-tac como relógio do "depois eu vejo"; `_ausencias` registrando o que **não** recebeu som |

Todos têm `_keep` (por que cada trecho saiu) e `why` em cada item de som: é o registro da decisão
editorial, e é o que permite outra pessoa — ou outra sessão — entender a edição sem ver o bruto.
