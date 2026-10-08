# Aprendizados

> **Histórico do projeto.** Este arquivo é o diário de como o método chegou à qualidade atual: cada
> correção feita pela autora (nas tabelas, "ela" é a autora do repositório) e cada descoberta técnica,
> com data e **onde foi consertada**. Use-o assim: antes de mudar uma regra, procure aqui *por que*
> ela existe; ao receber uma correção sua, **acrescente uma linha na mesma sessão** (trava 7 do
> [CLAUDE.md](../CLAUDE.md)). As entradas não são reescritas — algumas citam material privado do
> autor (cofre de notas, deck de campanha de cliente, vídeos brutos) que **não está** no repositório;
> o que valia deles já virou regra nos docs.

Cada correção e cada descoberta que mudou o resultado, com data e **onde foi consertada**.
Correção que fica só na conversa volta na próxima sessão — por isso este arquivo existe.

## Correções e decisões da Safira

| # | data | vídeo | o que ela disse | o que mudou | onde mora |
|---|---|---|---|---|---|
| 1 | 2026-09-24 | — | *"primeiro quero testar o output de edição… depois que aprovado, documentamos"* | entregar vídeo cedo; documentar só após aprovação | CLAUDE.md · fluxo §8 |
| 2 | 2026-09-24 | — | *"não mexa nos arquivos de outras pastas, apenas consuma"* | tudo copiado para cá | CLAUDE.md trava 1 · FONTES.md |
| 3 | 2026-09-24 | C2556 v2 | escolheu **A · natural** entre 3 looks | look padrão da marca | brand.json `look` · 04-cor.md |
| 4 | 2026-09-24 | C2556 v2 | *"vamos deixar por padrão aumentar sempre a velocidade pra 1.25x"* | 1,25x em todo vídeo | brand.json `speed` |
| 5 | 2026-09-24 | C2556 v2 | letras miúdas centralizadas no rodapé em todo anúncio do Clube | rodapé legal com degradê | brand.json `fine_print` · fine-print.txt |
| 6 | 2026-09-24 | C2556 v2 | o texto veio com "…0001-50Válido" colado | quebra de linha antes de "Válido apenas…" (sem mudar palavra) | fine-print.txt |
| 7 | 2026-09-24 | C2556 v2 | *"a trilha poderia ser mais agitada… bpm e timing dela tá mt fraquinho"* | trilha institucional da biblioteca → trilha nova de 126 BPM | 05-som.md §3 |
| 8 | 2026-09-24 | C2556 v2 | *"sonzinho de tic tac quando fala q falta pouco tempo ou bota urgencia de prazo"* | tic-tac nas falas de prazo, travado no BPM | tick_bed.py · 05-som.md §2 |
| 9 | 2026-09-24 | C2556 | mandou o guia de sonoplastia e pediu *"repense… antes de gerar"* | hierarquia A/B/C, riser→dropout→impact, "está fora" em silêncio, toque de tela no CTA | 05-som.md §1–2 |
| 10 | 2026-09-24 | C2556 v3 | *"deixa a trilha mais baixa, tá mt alta"* | −17 → −24 | brand.json `sound_defaults` |
| 11 | 2026-09-24 | C2556 v4 | logo do Clube no topo, acima da cabeça | logo branco centralizado | brand.json `logo` |
| 12 | 2026-09-24 | C2556 v5 | *"deixa na metade do tamanho"* | logo 400 → **200 px** | brand.json `logo.width` |
| 13 | 2026-09-24 | C2556 v6 | *"a trilha um pouquinho mais baixa ainda — sfx tá bom"* | −24 → **−27**; efeitos intactos | brand.json `sound_defaults.music_db` |
| 14 | 2026-09-24 | — | pensar em outra marca com outra tipografia na organização | `brands/` × `projects/` | 06-marcas.md |
| 15 | 2026-09-24 | C2559 v1 | *"aqui é 23h59"* (o apresentador falou 11h59) | `text_fixes`; revisados os 4 vídeos — só havia esse | plan.json do C2559 · CLAUDE.md trava 5 |

| 16 | 2026-09-25 | 10 vídeos | *"são 3 marcas… identifique qual é qual pela copy"* | marcas `allevo-tech` e `quero-card` criadas; mesmo cenário do Clube → look/posições herdados | brands/allevo-tech · brands/quero-card |
| 17 | 2026-09-25 | — | Allevo: logo `mono-darkbg`, sem letras miúdas, legenda com traço mantido e preenchimento **#00FFBB**, **Geist SemiBold** | brand.json da Allevo | brands/allevo-tech/brand.json |
| 18 | 2026-09-25 | — | Quero Card: logo `Logo - Quero Card0 1`, sem letras miúdas, preenchimento **rgba(166, 242, 0, 1)** (#A6F200), **Poppins SemiBold** | brand.json do Quero Card; fonte baixada do Google Fonts com permissão | brands/quero-card/brand.json |
| 19 | 2026-09-25 | 10 vídeos | *"gere os áudios de acordo com as narrativas: sfx em momentos que precisam, trilha que faça sentido com o assunto"* | uma trilha por marca (Allevo 112 BPM tech · Quero 100 BPM acústica) + efeitos narrativos; madrugada (C2551, C2554) sem trilha até a virada | brands/*/sound/SONS.md · plan.json |
| 20 | 2026-09-25 | — | *"demorando, né? bora"* | paralelizar: transcrição 3 por vez, cortes por agentes, render 3 por vez | este arquivo |
| 21 | 2026-09-25 | Allevo v1 | *"não dá p ouvir a trilha de allevo tech no fundo, precisa melhorar o método de interpretar os decibéis de cada som para equilibrar"* | trilha em `presence` (paridade com o Clube em 1–8 kHz sobre a voz, com corte de grave) e efeitos em `lu` (percebido); v2 das 10 só remixando o som (`--remix`, 2,4s cada) | edit.py · 05-som.md §4a · brand.json `sound_defaults` |
| 22 | 2026-10-06 | 05ECAE3A v1 | *"ele fala 'ADS01' como identificação de qual anúncio é e você coloca 'Edson'… nem era para aparecer"* | a claquete falada saiu da legenda (v2 corta o início no silêncio antes de "você"); o agente de corte tinha avisado que "Edson" era leitura incerta (p 0,7; 5 de 12 releituras) e eu transformei isso em `text_fix` fixo — regra nova: leitura incerta antes do roteiro = claquete até prova em contrário, **pergunte** | docs/02-cortes.md · plan.json |
| 23 | 2026-10-06 | 05ECAE3A, E17837EB | *"tire a trilha do 05ECAE3A / remova a trilha do E17837EB, deixando só sfx"* ("não precisa mudar nos que já têm; só não faça nos próximos") | v2 dos dois sem trilha, só efeitos; vale só para esses dois — os próximos voltam ao som completo | plan.json `sound.music: []` |
| 24 | 2026-10-08 | 5919FD0B | (QA da máquina reprovou o pico: −0,6 dBTP, limite −1,0) | `edit.py` agora mede o **pico verdadeiro** do áudio final e aperta o limitador (0,84 → 0,78 → … → 0,60) até ficar ≤ −1,3 dBTP; vale para os dois caminhos (com e sem som) | scripts/edit.py `master_audio` |
| 25 | 2026-10-08 | 5919FD0B, 991D76A8 | *"enquadra melhor dando um zoom e deixando o rosto mais posicionado para cima, e deixa mais devagar (avaliando se 1x ou 1,1x)"* | `framing` (zoom fixo ancorado embaixo): zoom 1,2 e 1,3; `pos_y` caiu de 81→76 e 87→82; velocidade pelo ritmo de fala: 5919FD0B 1,1x, 991D76A8 1,0x | plan.json · docs/07 |

## Descobertas técnicas

| # | o que | consequência |
|---|---|---|
| T1 | o bruto Sony é 3840×2160 com rotação −90° | o ffmpeg endireita sozinho → sai 9:16 sem crop |
| T2 | H.264 8 bits Rec.709, não log | grading suave; nada de LUT de conversão |
| T3 | o Whisper erra borda de palavra em até ~0,2s | cortes encostam no `silencedetect` (`snap_to_silence`); palavra entra na legenda com folga de 0,15s |
| T4 | VAD ligado esconde claquete e takes repetidos | transcrição com `vad_filter=False` |
| T5 | quebra gulosa de legenda termina bloco em "pra"/"de" e separa nome de botão | quebra por programação dinâmica com penalidades + `keep_together` |
| T6 | vírgula como quebra obrigatória deixa "respondeu," / "ganhou" sozinhos | vírgula virou quebra preferida (+4 se fica no meio) |
| T7 | a lista fixa de nomes próprios do cofre tem "são" (São Paulo) | "são dez perguntas" sairia "São dez perguntas" → a lista aqui é só da marca |
| T8 | o Whisper quebra "meia-noite" em "meia" + "-noite," | tokens com hífen inicial são colados ao anterior |
| T9 | fonte variável (Nunito) com peso nomeado | legenda desenhada com Pillow (mede largura exata), não ASS/libass |
| T10 | pedir 31s de música devolveu **40s** | medir sempre; alinhar pelo hit final medido (29,99s), não pelo pedido |
| T11 | tic-tac pedido "2 por segundo" veio 1/s ou 1 tick só | a cama é montada por script a partir de 1 tick, no BPM da trilha |
| T12 | uma variação de toque de tela veio **muda** (pico −66 dB) | `audio_tools.py inspect` antes de usar qualquer som gerado |
| T13 | a música veio marcada "Instrumental: False" | `audio_tools.py vocals` (Whisper) — nenhuma voz achada |
| T14 | o conector ElevenLabs não mostra saldo | dizer isso ao pedir permissão; saldo em elevenlabs.io |
| T15 | gasto real = estimativa: 2×1.641 + 8×50 = **3.683 cr** (2026-09-24) | `estimate_only` é confiável para música e efeito |
| T16 | o topo do cabelo do apresentador nunca passa de ~320 px (de 1920) | logo em y 80–170 não encosta na cabeça (medido com tira do topo, 1 frame/s) |
| T17 | o python3 do sistema não tem numpy | medições rodam pelo `venv_run.py` (Python do config.json) |
| T18 | vídeo mais longo que a trilha (C2559, 31,06s) | a trilha **entra depois** (`from 0.56`) para o hit cair na última palavra |

| T19 | processos abrindo arquivo dentro de uma pasta sincronizada na nuvem travam com 0% de CPU quando há muitas gravações simultâneas | render em cópia local (scratchpad) e devolver só `.mp4`/`.srt`/contato/`edit-report.json` |
| T20 | `text_fixes` literal troca dentro de outra palavra ("dade" → "iidade") | `"regex": true` com `\\b` |
| T21 | 4 de 20 efeitos vieram mudos (obturador ×2, ambiência noturna ×2) e 1 de 4 músicas falhou no servidor | `inspect` sempre; ambiência noturna substituída por relógio lento (`tick_bed.py` a 60 BPM) |
| T22 | trilha pedida "ends at 40s on one clean final hit" veio sem hit claro (Allevo: nível até 42,5s; Quero: ataque 39,14s) | alinhar o último ataque forte medido à última palavra |
| T23 | Whisper junta "R$ 24,90" em 4 tokens e "80%" em 2 | `keep_together` + regex de preço em `text_fixes` |
| T24 | loudness total (mesmo acima de 200 Hz) quase não separa a Allevo do Clube (26,6 × 25,5 dB abaixo da voz); a diferença está **por oitava**: 1 kHz −28,5 × −24,5, 4 kHz −16,9 × −12,1, 8 kHz −24,3 × −16,1 | presença = soma em potência de (trilha − voz) nas oitavas 1–8 kHz |
| T25 | pico igual ≠ volume igual: com pico a −1 dBFS a loudness momentânea dos efeitos vai de −4,5 (cachorro) a −30 (impact, que é subgrave) | efeito nivelado por loudness momentânea máx (`lu`) |
| T26 | 2026-10-06: o ambiente Python do Whisper desapareceu (o venv de um projeto vizinho, de que o `config.json` dependia, sumiu) e nada rodava | `scripts/setup.py` (`./ev setup`) cria um venv próprio em `~/.cache/editor-videos/venv`; o `venv_run.py` aceita `~` e caminho relativo e, sem `config.json`, copia o `config.example.json` e manda rodar o setup; `./ev setup --check` verifica tudo sem instalar |
| T27 | Whisper no arquivo inteiro **alucinou nos falsos inícios** (juntou o 1º take ao 2º e sumiu com palavras do 2º; esticou "pessoa" e "mercado" por segundos) — duas gravações de celular de 1,5–2,5 min | reconstruir `words.json` retranscrevendo cada take como clip curto (`faster-whisper`, beam 5, VAD off); guardar o original em `words.orig.json` |
| T28 | ruído de sala de celular/escritório fica acima de −35 dB: `silencedetect` achou 4–6 pausas no arquivo todo | `silence_db: −28` no plan.json do vídeo (docs/02-cortes.md) |
| T29 | o `presence` (soma de 1–8 kHz) calibra pela voz: voz de celular tem pouco agudo (4–8 kHz), então a trilha da Allevo Tech ficou 3–5 dB mais presente que a do Clube nos médios (250 Hz–2 kHz) | `./ev audio mix` agora imprime voz − fundo por oitava, só onde a trilha toca, com o Clube ao lado; se mascarar a voz, `music_presence: −3` no brand.json |
| T30 | a posição da legenda depende do enquadramento: selfie de busto (queixo ~50–55%) pede `pos_y` 62; close-up (queixo 69–76%) pede 80 | medir queixo/cabelo em ~24 quadros antes de fixar `captions.pos_y` (o plano guarda a medição em `_framing`) |
| T31 | o limitador de pico de amostra (`alimiter limit=0.84`) deixa overshoot entre amostras: vídeo só com voz saiu com −0,6 dBTP e o AAC ainda acrescenta um pouco | `master_audio`: mede `ebur128=peak=true` e reaperta o limitador; margem de 0,3 dB sobre o limite do QA |
| T32 | `edit.py` com vários takes em `keep` e `remove`: o corte vale para todas as janelas (não só a do take) e a linha do tempo estoura | não usar `remove` com vários takes; para tirar um trecho, quebre o `keep` em dois takes |
| T33 | ritmo de fala medido (palavras/min do vídeo editado, pausas já encurtadas): Clube aprovado a 1,25x = 184–221; apresentadores novos a 1,0x = 166–184 | para decidir a velocidade de um apresentador novo, calcule pal/min a 1,0x e escolha a velocidade que fecha ≈184 (o C2556, aprovado mais calmo); 991D76A8 (184 a 1,0x) fica em 1,0x, 5919FD0B (166) em 1,1x |
| T34 | enquadramento "rosto mais para cima" tem teto geométrico: a janela do zoom não desce abaixo do quadro | com o rosto baixo (cabelo ≥35%), zoom 1,3 sobe o cabelo de ~38% para ~20% e o queixo de ~76% para ~68%; simule o recorte nos piores quadros antes de renderizar |

## Pendências conhecidas

- vazamento de LED verde no lado esquerdo do rosto — nenhum look resolve; exigiria máscara;
- o áudio do C2559 continua dizendo "onze e cinquenta e nove" — só regravação conserta;
- **Quero Card — a fala contraria o deck da campanha** (documento de campanha do cliente, privado, que proíbe "até X% de desconto"): C2552 "até 70%", C2555 "até 80%"; planos Pro (R$ 24,90), ProMax (R$ 49,90) e Start Plus não estão no deck. Só regravação/corte resolve;
- Allevo C2546: ele diz "formação analista de dados" (sem "em") no take usado; C2547 "de analista";
- o texto de `fine-print.txt` tem as datas da campanha de 2026 (participação até 27/09, sorteio
  30/09) — revisar a cada campanha.
