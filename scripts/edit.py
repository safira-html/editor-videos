"""Edição simples de vídeo curto: corta trechos marcados, encurta pausas longas e queima legenda.

Uso:
    python3 scripts/edit.py projects/<marca>/<ID>/plan.json [--dry]   (--dry só mostra os blocos de legenda)
    python3 scripts/edit.py projects/<marca>/<ID>/plan.json --remix   (só refaz o som: reusa stage_video.mov e
                                                                     stage_voice.wav do último render)

O estilo da marca (fonte, legenda, look, velocidade, logo, letras miúdas, sons) mora em
brands/<marca>/brand.json; o plan.json do vídeo só guarda o que é dele e pode sobrescrever a marca.

O plan.json diz o que cortar (decisão editorial, lida da transcrição) e onde sair.
O script mede o silêncio no áudio para achar os pontos exatos de corte — a transcrição
diz O QUE foi falado, o silêncio medido diz ONDE cortar.
"""
import json
import os
import re
import subprocess
import sys
import unicodedata

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND_DIR = None   # brands/<marca> — definido em load_plan()
FONT_PATH = None   # fonte da legenda da marca

# padrão de legenda do Clube da Virada (legenda-padrao.json), autorado em 480x854
REF_W = 480
SENTENCE_END = ".?!…"
MIN_HOLE = 0.25  # trava da contraforma: o "o" precisa manter 25% do buraco


def deep_merge(base, over):
    """O plano do vídeo sobrescreve a marca; dicionários se mesclam, o resto é trocado."""
    out = dict(base)
    for k, v in over.items():
        out[k] = deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_plan(plan_path):
    """plan.json do vídeo + brands/<marca>/brand.json (o estilo fixo da marca)."""
    global BRAND_DIR, FONT_PATH
    plan = json.load(open(plan_path, encoding="utf-8"))
    BRAND_DIR = os.path.join(ROOT, "brands", plan["brand"])
    brand = json.load(open(os.path.join(BRAND_DIR, "brand.json"), encoding="utf-8"))
    plan = deep_merge(brand, plan)
    FONT_PATH = os.path.join(BRAND_DIR, plan["captions"]["font_file"])
    return plan


def detect_silences(audio, noise_db, min_dur):
    out = subprocess.run(
        ["ffmpeg", "-i", audio, "-af", f"silencedetect=noise={noise_db}dB:d={min_dur}", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return list(zip(starts, ends))


def keep_ranges(plan):
    """Takes mantidos, em ordem. `keep` (lista de takes) ou `keep_window` (um trecho só)."""
    return [tuple(r) for r in plan.get("keep") or [plan["keep_window"]]]


def snap_to_silence(t, silences, side, pad, reach=0.35):
    """Borda de take marcada pela transcrição → borda medida no silêncio mais próximo.

    O Whisper erra a borda da palavra em até ~0,2s; cortar no tempo dele decapita a sílaba.
    side="start": encosta no fim do silêncio anterior; side="end": no começo do silêncio seguinte.
    """
    best = None
    for s, e in silences:
        edge = e if side == "start" else s
        if abs(edge - t) <= reach and (best is None or abs(edge - t) < abs(best - t)):
            best = edge
    if best is None:
        return t
    return best - pad if side == "start" else best + pad


def range_segments(plan, silences):
    """Segments of each kept take, one list per entry of `keep` (blocks of a variant need the boundaries)."""
    out = []
    for a, b in keep_ranges(plan):
        a = snap_to_silence(a, silences, "start", plan.get("pad_before_speech", 0.10))
        b = snap_to_silence(b, silences, "end", plan.get("pad_after_speech", 0.15))
        out.append(build_segments(dict(plan, keep=None, keep_window=[a, b]), silences))
    return out


def block_timeline(plan, silences, speed):
    """Variants: {block name: (start, end)} in the final (cut + sped up) timeline.

    `_blocks` is written by scripts/variants.py: [{"name": "hook", "option": "h1", "ranges": 1}, ...],
    in order, each block owning that many consecutive entries of `keep`.
    """
    per_take, times, i, t0 = range_segments(plan, silences), {}, 0, 0.0
    for blk in plan["_blocks"]:
        dur = sum(b - a for take in per_take[i:i + blk["ranges"]] for a, b in take) / speed
        times[blk["name"]] = (round(t0, 3), round(t0 + dur, 3))
        i, t0 = i + blk["ranges"], t0 + dur
    return times


def take_index_of(mid, plan):
    """Which entry of `keep` a word belongs to (by the middle of the word, with the usual 0.15s margin)."""
    for i, (a, b) in enumerate(keep_ranges(plan)):
        if a - 0.15 <= mid <= b + 0.15:
            return i
    return -1


def build_segments(plan, silences):
    """Trechos mantidos = takes do plano − cortes manuais − pausas longas encurtadas."""
    ranges = keep_ranges(plan)
    for a, b in ranges:
        if b - a < 0.3:
            raise SystemExit(f"take [{a}, {b}] vazio ou curto demais — confira 'keep' no plan.json "
                             "(o template vem com [[0, 0]] para ser preenchido)")
    if len(ranges) > 1 or plan.get("keep"):
        return [s for per_take in range_segments(plan, silences) for s in per_take]
    win_start, win_end = ranges[0]
    cut = [tuple(r) for r in plan.get("remove", [])]
    pause_max = plan.get("max_pause", 0.45)
    pad_before = plan.get("pad_before_speech", 0.10)
    pad_after = plan.get("pad_after_speech", 0.15)
    for s, e in silences:
        if e - s > pause_max and s > win_start and e < win_end:
            a, b = s + pad_after, e - pad_before
            if b > a:
                cut.append((a, b))
    cut.sort()
    segs, cur = [], win_start
    for a, b in cut:
        a, b = max(a, win_start), min(b, win_end)
        if b <= cur:
            continue
        if a > cur:
            segs.append((round(cur, 3), round(a, 3)))
        cur = max(cur, b)
    if cur < win_end:
        segs.append((round(cur, 3), round(win_end, 3)))
    return [s for s in segs if s[1] - s[0] > 0.08]


def remap(t, segs):
    """Tempo do original → tempo do editado. Palavra que caiu num corte gruda na borda."""
    acc = 0.0
    for a, b in segs:
        if t < a:
            return acc
        if t <= b:
            return acc + (t - a)
        acc += b - a
    return acc


def strip_accents(x):
    x = unicodedata.normalize("NFD", x.lower())
    return "".join(c for c in x if unicodedata.category(c) != "Mn")


def core(w):
    return re.sub(r"^[^\wÀ-ÿ]+|[^\wÀ-ÿ]+$", "", w)


def find_proper_nouns(words, fixed):
    """Maiúscula FORA de início de frase = nome próprio (regra do cofre)."""
    found, at_start = set(fixed), True
    for w in words:
        c = core(w["t"])
        at_start = at_start or bool(w.get("brk"))  # variants: a block boundary starts a new sentence
        if c and c[0].isupper() and not at_start:
            found.add(strip_accents(c))
        at_start = w["t"].rstrip()[-1:] in SENTENCE_END
    return found


def typeset(text, proper):
    out = []
    for p in text.split():
        c = core(p)
        if c and strip_accents(c) in proper:
            out.append(p)
        elif p and p[0].isupper() and not re.match(r"^\d", p):
            out.append(p[0].lower() + p[1:])
        else:
            out.append(p)
    text = " ".join(out)
    text = re.sub(r"(\.\.\.|…|\.)+$", "", text)  # nunca ponto final
    return text.strip()


def font(size, weight):
    """Fonte variável: escolhe a instância pelo nome (ex. "ExtraBold"). Fonte estática: usa como está."""
    f = ImageFont.truetype(FONT_PATH, size)
    try:
        f.set_variation_by_name(weight)
    except (OSError, ValueError):
        pass  # fonte não variável (OSError) ou sem instância com esse nome (ValueError) — fica o peso padrão do arquivo
    return f


def hole_area(size, stroke, weight):
    f = font(size, weight)
    pad = stroke + 6
    img = Image.new("RGBA", (size * 3 + pad * 2, size * 2 + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((img.width // 2, img.height // 2), "o", font=f, anchor="mm",
                             fill="#FFFFFF", stroke_width=stroke, stroke_fill="#000000")
    px = img.load()
    cx, cy, r = img.width // 2, img.height // 2, max(3, size // 3)
    return sum(1 for y in range(cy - r, cy + r) for x in range(cx - r, cx + r) if px[x, y][3] < 40)


def safe_stroke(size, weight, wanted):
    base = hole_area(size, 0, weight)
    safe = 0
    for s in range(1, max(3, size // 3)):
        if base and hole_area(size, s, weight) >= base * MIN_HOLE:
            safe = s
        else:
            break
    return max(1, min(wanted, safe))


def text_width(text, f, stroke):
    box = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), text, font=f, stroke_width=stroke)
    return box[2] - box[0]


# bloco não termina em palavra que pede a seguinte
WEAK_ENDINGS = {"a", "o", "as", "os", "um", "uma", "de", "da", "do", "das", "dos", "no", "na", "nos",
                "nas", "em", "pra", "pro", "para", "por", "pelo", "pela", "e", "ou", "que", "se", "com",
                "sem", "mais", "às", "ao", "é", "só", "até", "vai", "não", "cada", "seu", "sua"}


def split_phrases(words, max_gap):
    """Frase = até ponto/?/! ou pausa longa. Um bloco nunca atravessa duas frases."""
    phrases, cur = [], []
    for w in words:
        if cur and (w["s"] - cur[-1]["e"] > max_gap or w.get("brk")):
            phrases.append(cur)
            cur = []
        cur.append(w)
        if w["t"].rstrip()[-1:] in SENTENCE_END:
            phrases.append(cur)
            cur = []
    if cur:
        phrases.append(cur)
    return phrases


def chunk_phrase(phrase, cfg, fits, locked):
    """Quebra ótima de uma frase em blocos de 1 linha (programação dinâmica).

    Penaliza: bloco terminando em palavra fraca, quebrar uma unidade travada
    ("25 mil reais", nome de botão), bloco de 1 palavra, blocos desbalanceados.
    """
    n = len(phrase)
    best = [0.0] + [float("inf")] * n
    back = [0] * (n + 1)
    for j in range(1, n + 1):
        for i in range(max(0, j - cfg["max_words"]), j):
            chunk = phrase[i:j]
            if not fits(" ".join(w["t"] for w in chunk)):
                continue
            cost = 1.0
            last = strip_accents(core(chunk[-1]["t"]))
            if j < n and last in WEAK_ENDINGS:
                cost += 6
            if j < n and (j - 1, j) in locked:
                cost += 20
            if any(w["t"].rstrip().endswith(",") for w in chunk[:-1]):
                cost += 4  # vírgula é quebra preferida, não obrigatória
            if len(chunk) == 1 and n > 1:
                cost += 3
            cost += 0.3 * (cfg["max_words"] - len(chunk)) ** 2 / cfg["max_words"]
            if best[i] + cost < best[j]:
                best[j], back[j] = best[i] + cost, i
    out, j = [], n
    while j > 0:
        out.append(phrase[back[j]:j])
        j = back[j]
    return out[::-1]


def locked_pairs(phrase, units):
    """Pares de índices (k, k+1) que não podem ser separados."""
    toks = [strip_accents(core(w["t"])) for w in phrase]
    pairs = set()
    for unit in units:
        u = [strip_accents(core(x)) for x in unit.split()]
        for k in range(len(toks) - len(u) + 1):
            if toks[k:k + len(u)] == u:
                pairs.update((k + m, k + m + 1) for m in range(len(u) - 1))
    return pairs


def group_blocks(words, cfg, f, stroke, width):
    def fits(text):
        return text_width(text, f, stroke) <= width * cfg["max_width"]

    blocks = []
    for phrase in split_phrases(words, cfg["max_gap"]):
        for chunk in chunk_phrase(phrase, cfg, fits, locked_pairs(phrase, cfg.get("keep_together", []))):
            blocks.append({"raw": " ".join(w["t"] for w in chunk), "start": chunk[0]["s"], "end": chunk[-1]["e"]})
    # tempo mínimo na tela: bloco curto entra antes, avançando no silêncio anterior
    for i, b in enumerate(blocks):
        if b["end"] - b["start"] >= cfg["min_on_screen"]:
            continue
        ceiling = blocks[i + 1]["start"] - 0.04 if i + 1 < len(blocks) else b["end"] + cfg["min_on_screen"]
        b["end"] = max(b["end"], min(b["start"] + cfg["min_on_screen"], ceiling))
        if b["end"] - b["start"] < cfg["min_on_screen"]:
            floor = blocks[i - 1]["end"] + 0.04 if i else 0.0
            b["start"] = min(b["start"], max(floor, b["end"] - cfg["min_on_screen"]))
    # sem piscar: o bloco fica até o próximo entrar quando o vão é curto
    for i in range(len(blocks) - 1):
        if blocks[i + 1]["start"] - blocks[i]["end"] < 0.25:
            blocks[i]["end"] = blocks[i + 1]["start"]
    return blocks


def render_captions(words, plan, out_dir, width, height, duration):
    cfg = plan["captions"]
    k = width / REF_W
    size = round(cfg["size"] * k)
    weight = cfg.get("weight", "ExtraBold")
    f = font(size, weight)
    stroke = safe_stroke(size, weight, round(cfg["stroke"] * k))
    proper = find_proper_nouns(words, {strip_accents(x) for x in cfg.get("proper_nouns", [])})
    for t in cfg.get("force_lowercase", []):
        proper.discard(strip_accents(t))
    blocks = group_blocks(words, cfg, f, stroke, width)
    for b in blocks:
        b["text"] = typeset(b["raw"], proper)
    for fix in cfg.get("text_fixes", []):
        for b in blocks:
            # "regex": true → troca com limite de palavra (ex. "\be analista" não pega "de analista")
            if fix.get("regex"):
                b["text"] = re.sub(fix["from"], fix["to"], b["text"])
            else:
                b["text"] = b["text"].replace(fix["from"], fix["to"])

    os.makedirs(out_dir, exist_ok=True)
    blank = os.path.join(out_dir, "blank.png")
    Image.new("RGBA", (width, height), (0, 0, 0, 0)).save(blank)
    x, y = width * cfg["pos_x"] / 100, height * cfg["pos_y"] / 100
    lines, t = [], 0.0
    for i, b in enumerate(blocks):
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        s, ff = size, f
        while text_width(b["text"], ff, stroke) > width * cfg["max_width"] and s > 30:
            s -= 2
            ff = font(s, weight)
        ImageDraw.Draw(img).text((x, y), b["text"], font=ff, anchor="mm", fill=cfg["color"],
                                 stroke_width=stroke, stroke_fill=cfg["stroke_color"])
        p = os.path.join(out_dir, f"block_{i:03d}.png")
        img.save(p)
        if b["start"] > t:
            lines += [f"file '{blank}'", f"duration {b['start'] - t:.3f}"]
        lines += [f"file '{p}'", f"duration {b['end'] - b['start']:.3f}"]
        t = b["end"]
    lines += [f"file '{blank}'", f"duration {max(0.1, duration - t):.3f}", f"file '{blank}'"]
    concat = os.path.join(out_dir, "captions.txt")
    open(concat, "w").write("\n".join(lines) + "\n")
    return blocks, concat, stroke, size


# looks de cor (ffmpeg, aplicados em 1080x1920, Rec.709 8 bits → correção suave)
LOOKS = {
    "none": "null",
    # A · natural — aprovado pela Safira em 2026-09-24 (C2556 v2)
    "natural": "eq=contrast=1.06:brightness=-0.01:saturation=1.05,colorbalance=rm=0.02:bm=-0.02,"
               "huesaturation=colors=g+y:saturation=-0.25:strength=1",
    "warm_neutral": "curves=all='0/0.02 0.25/0.22 0.5/0.5 0.75/0.79 1/0.98',"
                    "colorbalance=rs=0.02:bs=-0.03:rm=0.04:gm=0.01:bm=-0.04:rh=0.02:bh=-0.02,"
                    "huesaturation=colors=g:saturation=-0.35:strength=1,eq=saturation=1.02",
    "punch": "curves=all='0/0 0.25/0.2 0.5/0.5 0.75/0.82 1/1',eq=saturation=1.12,vibrance=intensity=0.12,"
             "colorbalance=rm=0.02:bm=-0.02,huesaturation=colors=g:saturation=-0.2:strength=1,unsharp=5:5:0.4",
}


def wrap_lines(text, f, max_w):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split():
            cand = f"{cur} {word}".strip()
            if text_width(cand, f, 0) <= max_w or not cur:
                cur = cand
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


def render_fine_print(cfg, path, width, height):
    """Letras miúdas centralizadas no rodapé, com degradê escuro atrás para leitura."""
    text = open(os.path.join(BRAND_DIR, cfg["file"]), encoding="utf-8").read().strip()
    size = cfg.get("size", 22)
    f = font(size, cfg.get("weight", "SemiBold"))
    lines = wrap_lines(text, f, width * cfg.get("max_width", 0.9))
    line_h = round(size * 1.3)
    block_h = line_h * len(lines)
    bottom = height - cfg.get("margin_bottom", 48)
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    grad_h = block_h + 160
    grad = Image.new("L", (1, grad_h))
    for yy in range(grad_h):
        grad.putpixel((0, yy), int(cfg.get("shade_alpha", 150) * (yy / grad_h) ** 1.6))
    black = Image.new("RGBA", (width, grad_h), (0, 0, 0, 255))
    black.putalpha(grad.resize((width, grad_h)))
    img.alpha_composite(black, (0, height - grad_h))
    d = ImageDraw.Draw(img)
    y = bottom - block_h
    fill = tuple(int(cfg.get("color", "#FFFFFF")[i:i + 2], 16) for i in (1, 3, 5)) + (cfg.get("alpha", 230),)
    for line in lines:
        d.text((width / 2, y), line, font=f, anchor="ma", fill=fill, stroke_width=1, stroke_fill=(0, 0, 0, 160))
        y += line_h
    img.save(path)
    return lines


def render_logo(cfg, overlay_path, width):
    """Logo centralizado no topo, sobre a camada estática (rodapé). Sombra suave para leitura."""
    from PIL import ImageFilter
    base = Image.open(overlay_path).convert("RGBA")
    logo = Image.open(os.path.join(BRAND_DIR, cfg["file"])).convert("RGBA")
    w = cfg.get("width", 400)
    logo = logo.resize((w, round(logo.height * w / logo.width)), Image.LANCZOS)
    x, y = (width - w) // 2, cfg.get("top", 70)
    if cfg.get("shadow", True):
        pad = 30
        sh = Image.new("RGBA", (logo.width + pad * 2, logo.height + pad * 2), (0, 0, 0, 0))
        alpha = logo.split()[3].point(lambda a: int(a * cfg.get("shadow_alpha", 0.45)))
        sh.paste((0, 0, 0, 255), (pad, pad + 4), alpha)
        sh = sh.filter(ImageFilter.GaussianBlur(12))
        base.alpha_composite(sh, (x - pad, y - pad))
    base.alpha_composite(logo, (x, y))
    base.save(overlay_path)
    return (x, y, logo.width, logo.height)


def loudness(path):
    out = subprocess.run(["ffmpeg", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1])


def peak(path):
    out = subprocess.run(["ffmpeg", "-i", path, "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.search(r"max_volume: (-?[\d.]+) dB", out).group(1))


# referências da Rotina 8 do cofre (mix_episode.py): o dB do plano é relativo a elas
VOICE_REF_LUFS = -18.8
MUSIC_REF_LUFS = -12.0
SFX_REF_PEAK = -1.0
MUSIC_XFADE = 0.40

# Nível percebido (2026-09-25). Pico e loudness do arquivo inteiro enganam: o impact é quase todo
# subgrave, o latido é denso, e uma trilha com muito sub some no celular. Ver docs/05-som.md §4.
# · efeito com "lu": loudness momentânea máx (400 ms) do trecho que toca = voz + lu.
# · trilha com "presence": quanto ela ESCAPA DA MÁSCARA DA VOZ deste vídeo nas oitavas de 1 a 8 kHz
#   (hi-hat, palma, synth — o que o celular reproduz e a voz cobre menos), somadas em potência.
#   0 = igual ao Clube aprovado (C2556 v6 −9,8 · C2559 v2 −9,7 dB); +2 = 2 dB mais presente.
#   Se o grave (oitava de 125 Hz) passar do Clube, um shelf abaixo de 150 Hz corta o excesso.
PRESENCE_BANDS = [1000, 2000, 4000, 8000]
PRESENCE_REF = -9.7   # dB, trilha − voz somadas em 1–8 kHz, nos aprovados do Clube
LOW_BAND, LOW_REF = 125, -8.9  # dB, trilha − voz na oitava de 125 Hz, nos aprovados do Clube
LEVELS = []  # o que cada som mediu e quanto ganho levou — vai para o edit-report.json


def band_level(path, center, offset=0.0, length=None):
    """Nível médio (dB) na oitava centrada em `center` — dois passa-banda de 1 oitava em série."""
    span = ["-ss", str(offset), "-t", f"{length:.3f}"] if length else []
    bp = f"bandpass=f={center}:width_type=o:w=1"
    out = subprocess.run(["ffmpeg", *span, "-i", path, "-af", f"{bp},{bp},volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.search(r"mean_volume: (-?[\d.]+) dB", out).group(1))


def music_presence_gain(src, offset, length, voice_wav, gain_v, presence):
    """Ganho (dB) para a trilha ter a presença pedida sobre ESTA voz, e o corte de grave (dB) que evita embolar."""
    import math
    diffs = [band_level(src, c, offset, length) - (band_level(voice_wav, c) + gain_v) for c in PRESENCE_BANDS]
    measured = 10 * math.log10(sum(10 ** (d / 10) for d in diffs))
    g = PRESENCE_REF + presence - measured
    low = band_level(src, LOW_BAND, offset, length) + g - (band_level(voice_wav, LOW_BAND) + gain_v)
    return g, max(0.0, low - LOW_REF), measured


def momentary_max(path, offset, length):
    """Loudness momentânea máxima (LUFS, janela de 400 ms) do trecho que o efeito toca."""
    out = subprocess.run(["ffmpeg", "-v", "verbose", "-ss", str(offset), "-t", f"{length:.3f}", "-i", path,
                          "-af", "apad=pad_dur=0.5,ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return max(float(x) for x in re.findall(r"M:\s*(-?[\d.]+)", out))


def music_dropouts(drops, ramp=0.06):
    """Dropout: a trilha cai por um instante antes de um momento-chave (silêncio como ferramenta).

    Cada item: {"from": s, "to": s, "db": -30}. Rampa de 60ms nas bordas para não estalar.
    """
    parts = []
    for d in drops:
        g = 10 ** (d.get("db", -30) / 20)
        a, b = d["from"], d["to"]
        env = f"clip((t-{a})/{ramp},0,1)*clip(({b}-t)/{ramp},0,1)"
        parts.append(f",volume='1-{1 - g:.4f}*{env}':eval=frame")
    return "".join(parts)


def resolve_anchors(sound, plan, block_times, last_word_start):
    """Variants: turns block-relative sound into absolute times of THIS combination.

    sfx / dropout: {"block": "body", "anchor": "start"|"end", "rel": -0.12} replaces `at` / `from`
    (a dropout also takes "len" → `to`). {"when": {"hook": "h2"}} keeps the item only for that option.
    music: {"align_end": true} puts the track's final hit (brand sound_defaults.music_hits[file]) on the
    start of the last spoken word (offset when the video is shorter than the hit, `from` when longer).
    Items without these keys pass through untouched, so ordinary plans are unaffected.
    """
    combo = plan.get("_combo", {})

    def wanted(item):
        return all(combo.get(k) == v for k, v in item.get("when", {}).items())

    def anchored(item, key):
        item = dict(item)
        item.pop("when", None)
        if "block" in item:
            start, end = block_times[item.pop("block")]
            item[key] = round((start if item.pop("anchor", "start") == "start" else end) + item.pop("rel", 0.0), 3)
        return item

    out = dict(sound)
    out["sfx"] = [anchored(e, "at") for e in sound.get("sfx", []) if wanted(e)]
    drops = []
    for d in sound.get("dropouts", []):
        if wanted(d):
            d = anchored(d, "from")
            if "len" in d:
                d["to"] = round(d["from"] + d.pop("len"), 3)
            drops.append(d)
    out["dropouts"] = drops
    hits = plan.get("sound_defaults", {}).get("music_hits", {})
    music = []
    for m in sound.get("music", []):
        m = dict(m)
        if m.pop("align_end", False):
            if m["file"] not in hits:
                raise SystemExit(f"align_end: add the final-hit time of {m['file']} to sound_defaults.music_hits "
                                 "in brand.json (python3 scripts/audio_tools.py beat <file> prints it)")
            off = hits[m["file"]] - last_word_start
            m["offset"], m["from"] = (round(off, 2), 0.0) if off >= 0 else (0.0, round(-off, 2))
        music.append(m)
    out["music"] = music
    return out


def apply_sound_defaults(sound, defaults, duration):
    """Preenche o que o plano do vídeo não disse com os padrões da marca (brand.json → sound_defaults)."""
    sound = dict(sound)
    sound.setdefault("target_lufs", defaults.get("target_lufs", -14))
    music = []
    for m in sound.get("music", []):
        m = dict(m)
        if "presence" not in m and "db" not in m:
            if "music_presence" in defaults:
                m["presence"] = defaults["music_presence"]
            else:
                m["db"] = defaults.get("music_db", -27)
        m.setdefault("from", 0.0)
        m.setdefault("to", duration)
        music.append(m)
    sound["music"] = music
    sound["dropouts"] = [dict({"db": defaults.get("dropout_db", -30)}, **d) for d in sound.get("dropouts", [])]
    sfx = []
    for e in sound.get("sfx", []):
        e = dict(e)
        if "db" not in e and "lu" not in e:
            if e.get("path", "").endswith("tick_bed.wav"):
                e["db"] = defaults.get("tick_db", -22)
            else:
                raise SystemExit(f"efeito sem 'lu'/'db' no plano: {e} — o nível é decisão de hierarquia (docs/05-som.md §4)")
        sfx.append(e)
    sound["sfx"] = sfx
    return sound


def mix_sound(voice_wav, sound, duration, out_wav, work):
    """Voz + trilha (motivos com crossfade) + efeitos → wav final em -14 LUFS."""
    sdir = os.path.join(BRAND_DIR, "sound")
    inputs, filters, labels = ["-i", voice_wav], [], []
    gain_v = VOICE_REF_LUFS - loudness(voice_wav)
    filters.append(f"[0:a]volume={gain_v:.2f}dB[voice]")
    labels.append("[voice]")
    n = 1
    for i, m in enumerate(sound.get("music", [])):
        src = os.path.join(sdir, "music", m["file"])
        start, end = m["from"], min(m["to"], duration)
        length = end - start + (MUSIC_XFADE if i + 1 < len(sound["music"]) else 0)
        shelf = 0.0
        if "presence" in m:
            g, shelf, measured = music_presence_gain(src, m.get("offset", 0), length, voice_wav, gain_v, m["presence"])
        else:
            measured = loudness(src)
            g = MUSIC_REF_LUFS - measured + m["db"]
        LEVELS.append({"som": m["file"], "modo": "presence" if "presence" in m else "db",
                       "alvo": m.get("presence", m.get("db")), "medido": round(measured, 1), "ganho": round(g, 1),
                       "corte_grave": round(shelf, 1)})
        eq = f"lowshelf=f=150:g={-shelf:.2f}," if shelf > 0.05 else ""
        fade_in = 0.05 if i == 0 else MUSIC_XFADE
        fade_out = MUSIC_XFADE if i + 1 < len(sound["music"]) else m.get("fade_out", 0.6)
        inputs += ["-ss", str(m.get("offset", 0)), "-t", f"{length:.3f}", "-i", src]
        filters.append(f"[{n}:a]aresample=48000,{eq}volume={g:.2f}dB,afade=t=in:d={fade_in},"
                       f"afade=t=out:st={max(0, length - fade_out):.3f}:d={fade_out},"
                       f"adelay={int(start * 1000)}:all=1{music_dropouts(sound.get('dropouts', []))}[m{i}]")
        labels.append(f"[m{i}]")
        n += 1
    for i, e in enumerate(sound.get("sfx", [])):
        src = os.path.join(work, e["path"]) if e.get("path") else os.path.join(sdir, "sfx", e["file"])
        if "lu" in e:
            measured = momentary_max(src, e.get("offset", 0), e.get("length", 1.0))
            g = VOICE_REF_LUFS + e["lu"] - measured
        else:
            measured = peak(src)
            g = SFX_REF_PEAK - measured + e["db"]
        LEVELS.append({"som": e.get("file") or e.get("path"), "at": e["at"], "modo": "lu" if "lu" in e else "db",
                       "alvo": e.get("lu", e.get("db")), "medido": round(measured, 1), "ganho": round(g, 1)})
        inputs += ["-ss", str(e.get("offset", 0)), "-i", src]
        filters.append(f"[{n}:a]aresample=48000,volume={g:.2f}dB,afade=t=in:d=0.015,"
                       f"afade=t=out:st={e.get('length', 1.0):.3f}:d={e.get('tail', 0.8)}:curve=qua,"
                       f"adelay={int(e['at'] * 1000)}:all=1[e{i}]")
        labels.append(f"[e{i}]")
        n += 1
    pre = os.path.join(work, "mix_pre.wav")
    filters.append(f"{''.join(labels)}amix=inputs={len(labels)}:duration=first:normalize=0[mix]")
    subprocess.run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", "[mix]",
                    "-ar", "48000", "-ac", "2", pre], check=True, stderr=subprocess.DEVNULL)
    g = sound.get("target_lufs", -14) - loudness(pre)
    subprocess.run(["ffmpeg", "-y", "-i", pre, "-af", f"volume={g:.2f}dB,alimiter=limit=0.84:level=false",
                    out_wav], check=True, stderr=subprocess.DEVNULL)
    return out_wav


def write_srt(blocks, path):
    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    with open(path, "w", encoding="utf-8") as fh:
        for i, b in enumerate(blocks, 1):
            fh.write(f"{i}\n{ts(b['start'])} --> {ts(b['end'])}\n{b['text']}\n\n")


def main():
    plan_path = os.path.abspath(sys.argv[1])
    work = os.path.dirname(plan_path)
    plan = load_plan(plan_path)
    src = os.path.expanduser(plan["source"])
    audio = os.path.join(work, "audio16k.wav")
    words = json.load(open(os.path.join(work, "words.json"), encoding="utf-8"))

    silences = detect_silences(audio, plan.get("silence_db", -35), 0.18)
    segs = build_segments(plan, silences)
    if not segs:
        raise SystemExit("nenhum trecho mantido — confira 'keep' no plan.json (o template vem com [[0, 0]])")
    if not plan.get("sound") and "--dry" not in sys.argv:
        print("⚠️  plano sem 'sound': o vídeo sai só com a voz (sem trilha nem efeitos)")
    speed = plan.get("speed", 1.25)  # padrão: sempre 1,25x (decisão da Safira, 2026-09-24)
    duration = sum(b - a for a, b in segs) / speed
    block_times = block_timeline(plan, silences, speed) if plan.get("_blocks") else {}

    # o Whisper às vezes quebra palavra hifenizada em dois tokens ("meia" + "-noite,")
    merged = []
    for w in words:
        if merged and w["t"].startswith("-"):
            merged[-1] = dict(merged[-1], t=merged[-1]["t"] + w["t"], e=w["e"])
        else:
            merged.append(w)
    words = merged

    kept = []
    for w in words:
        mid = (w["s"] + w["e"]) / 2
        if any(a - 0.15 <= mid <= b + 0.15 for a, b in segs):  # folga p/ erro de borda do Whisper
            kept.append({"t": w["t"], "s": remap(w["s"], segs) / speed, "e": remap(w["e"], segs) / speed})
            if plan.get("_blocks"):  # variants: a caption never straddles two blocks
                kept[-1]["take"] = take_index_of(mid, plan)
    block_of = {}
    for blk in plan.get("_blocks", []):
        for i in range(len(block_of), len(block_of) + blk["ranges"]):
            block_of[i] = blk["name"]
    for prev, cur in zip(kept, kept[1:]):
        if block_of.get(cur.get("take")) != block_of.get(prev.get("take")):
            cur["brk"] = True

    width, height = plan.get("output_size", [1080, 1920])
    cap_dir = os.path.join(work, "captions")
    captions_on = plan.get("captions", {}).get("enabled", True) is not False
    blocks, concat, stroke, size = render_captions(kept if captions_on else [], plan, cap_dir, width, height, duration)

    if "--dry" in sys.argv:
        for b in blocks:
            print(f"  {b['start']:6.2f}-{b['end']:6.2f}  {b['text']}")
        return

    out_dir = os.path.join(ROOT, "output", plan["brand"])
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, plan["output_name"])
    fine_png = os.path.join(work, "fine_print.png")
    fine_lines = []
    if plan.get("fine_print"):
        fine_lines = render_fine_print(plan["fine_print"], fine_png, width, height)
    else:
        Image.new("RGBA", (width, height), (0, 0, 0, 0)).save(fine_png)
    logo_box = render_logo(plan["logo"], fine_png, width) if plan.get("logo") else None
    look = LOOKS[plan.get("look", "none")]

    fade = 0.012
    parts, labels = [], ""
    for i, (a, b) in enumerate(segs):
        d = b - a
        parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}]")
        parts.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d={fade},"
                     f"afade=t=out:st={d - fade:.3f}:d={fade}[a{i}]")
        labels += f"[v{i}][a{i}]"
    parts.append(f"{labels}concat=n={len(segs)}:v=1:a=1[vc][ac]")
    # ordem do cofre: acelera primeiro, legenda depois (legenda já está no tempo acelerado)
    parts.append(f"[vc]setpts=PTS/{speed},fps=30000/1001,scale={width}:{height}:flags=lanczos,setsar=1,{look}[vs]")
    parts.append("[1:v]format=rgba[cap]")
    parts.append("[2:v]format=rgba[fine]")
    parts.append("[vs][fine]overlay=0:0:format=auto[vf]")
    parts.append("[vf][cap]overlay=0:0:eof_action=pass:format=auto,format=yuv420p[v]")
    parts.append(f"[ac]atempo={speed},aresample=48000[a]")
    stage = os.path.join(work, "stage_video.mp4")
    voice = os.path.join(work, "stage_voice.wav")
    cmd = ["ffmpeg", "-y", "-i", src, "-f", "concat", "-safe", "0", "-i", concat,
           "-loop", "1", "-i", fine_png,
           "-filter_complex", ";".join(parts), "-map", "[v]", "-map", "[a]", "-t", f"{duration:.3f}",
           "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high",
           "-c:a", "pcm_s16le", "-video_track_timescale", "90000", stage.replace(".mp4", ".mov")]
    stage = stage.replace(".mp4", ".mov")
    if "--remix" in sys.argv and os.path.exists(stage) and os.path.exists(voice):
        print("--remix: reusando stage_video.mov e stage_voice.wav (corte e legenda do último render)")
    else:
        subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-y", "-i", stage, "-vn", "-c:a", "pcm_s16le", voice], check=True,
                       stderr=subprocess.DEVNULL)

    final_audio = os.path.join(work, "final_audio.wav")
    if plan.get("sound"):
        sound = resolve_anchors(plan["sound"], plan, block_times, kept[-1]["s"] if kept else 0.0)
        sound = apply_sound_defaults(sound, plan.get("sound_defaults", {}), duration)
        mix_sound(voice, sound, duration, final_audio, work)
    else:
        g = plan.get("loudness_lufs", -14) - loudness(voice)
        subprocess.run(["ffmpeg", "-y", "-i", voice, "-af", f"volume={g:.2f}dB,alimiter=limit=0.84:level=false",
                        final_audio], check=True, stderr=subprocess.DEVNULL)
    subprocess.run(["ffmpeg", "-y", "-i", stage, "-i", final_audio, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                    out], check=True, stderr=subprocess.DEVNULL)

    srt = out.rsplit(".", 1)[0] + ".srt"
    write_srt(blocks, srt)
    report = {"block_times": block_times, "segments": segs, "edited_duration": round(duration, 3),
              "original_takes": keep_ranges(plan), "caption_blocks": blocks,
              "caption_size_px": size, "stroke_px": stroke, "sound_levels": LEVELS}
    json.dump(report, open(os.path.join(work, "edit-report.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"segmentos mantidos: {len(segs)} · duração editada {duration:.2f}s")
    for a, b in segs:
        print(f"  {a:6.2f} → {b:6.2f}  ({b - a:.2f}s)")
    print(f"legenda: {len(blocks)} blocos · corpo {size}px · traço {stroke}px")
    for b in blocks:
        print(f"  {b['start']:6.2f}-{b['end']:6.2f}  {b['text']}")
    if fine_lines:
        print(f"letras miúdas: {len(fine_lines)} linhas")
    if logo_box:
        print(f"logo: x={logo_box[0]} y={logo_box[1]} {logo_box[2]}x{logo_box[3]}px")
    for lv in LEVELS:
        print(f"  som {lv['som']:<24} {lv['modo']} {lv['alvo']:>6} · medido {lv['medido']:6.1f} · ganho {lv['ganho']:+6.1f} dB")
    print(f"velocidade {speed}x · look {plan.get('look', 'none')} · duração final {duration:.2f}s")
    print(f"saída: {out}\nsrt:   {srt}")


if __name__ == "__main__":
    main()
