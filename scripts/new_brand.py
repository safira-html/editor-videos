"""Cria uma marca nova em brands/<slug>/ a partir de brands/_template e valida as escolhas.

Rode pelo atalho (precisa de Pillow, que vem no venv do setup):
    ./ev brand --list
    ./ev brand --slug minha-marca --name "Minha Marca" --logo ~/logo.png --font ~/Fonte.ttf \\
               --weight Bold --fill '#00FFBB' --framing seated --frame ~/Downloads/C1.MP4 --at 8

    ./ev brand --answers respostas.json          # mesmos campos, em JSON (flags da linha de comando vencem)

Campos (flag = chave do JSON com _ no lugar de -):
    --slug            pasta em brands/ (minusculas, numeros e hifen)            [obrigatorio]
    --name            nome de exibicao                                           [default: slug]
    --logo            PNG com transparencia                                      [opcional, mas recomendado]
    --font            .ttf/.otf da legenda                                       [obrigatorio]
    --weight          instancia nomeada da fonte variavel (ex. SemiBold)         [default: Bold]
    --fill            cor do preenchimento da legenda, #RRGGBB                   [default: #FFFFFF]
    --stroke          cor do traco da legenda, #RRGGBB                           [default: #030303]
    --fine-print-file .txt com as letras miudas (copiado VERBATIM)               [default: sem letras miudas]
    --look            none | natural | warm_neutral | punch                      [default: none]
    --framing         seated (60%) | selfie (69%) | closeup (75%)                [default: seated]
    --pos-y           % da altura para a legenda (vence o --framing)
    --speed           velocidade final                                           [default: 1.25]
    --logo-width      largura do logo em px de 1080                              [default: sugerido pelo aspecto]
    --music-presence  presenca da trilha sobre a voz (docs/05-som.md 4a)         [default: 0]
    --frame / --at    video de exemplo e segundo do quadro -> brands/<slug>/preview.png
    --force           permite mexer numa marca que ja existe (nunca apaga sons)
    --preview-only    nao cria nada: so refaz o preview.png de uma marca existente (le o brand.json como esta,
                      inclusive o que voce editou a mao). Precisa de --slug e --frame
"""
import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRANDS = os.path.join(ROOT, "brands")
TEMPLATE = os.path.join(BRANDS, "_template")
FRAMING_POS_Y = {"seated": 60, "selfie": 69, "closeup": 75}
FRAMING_TEXT = {"seated": "plano medio, apresentador sentado", "selfie": "selfie, rosto no centro",
                "closeup": "close-up, rosto grande"}
KNOWN_LOOKS = ["none", "natural", "warm_neutral", "punch"]
SAMPLE_CAPTION = "assim fica a legenda"
FIELDS = ["slug", "name", "logo", "font", "weight", "fill", "stroke", "fine_print_file", "look", "framing",
          "pos_y", "speed", "logo_width", "music_presence", "frame", "at", "allow_opaque_logo"]
ANSWER_PATHS = {"logo", "font", "fine_print_file", "frame"}


class BrandError(Exception):
    """Erro de validacao com mensagem para a pessoa."""


def need_pillow():
    try:
        import PIL  # noqa: F401
    except ImportError:
        raise BrandError("Pillow is not available in this Python. Run it through ./ev brand "
                         "(setup creates the venv: ./ev setup).")


# ---------------------------------------------------------------- validacao

def check_hex(value, flag):
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", value or ""):
        raise BrandError(f"{flag} must be a hex color like #00FFBB (got {value!r})")
    return value.upper()


def luminance(hex_color):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def check_font(path, weight, weight_given):
    """Fonte abre no Pillow? Se e variavel, o peso precisa ser uma instancia nomeada."""
    from PIL import ImageFont
    if not os.path.isfile(path):
        raise BrandError(f"font file not found: {path}")
    try:
        f = ImageFont.truetype(path, 40)
    except OSError as err:
        raise BrandError(f"Pillow could not load the font {path}: {err}")
    try:
        names = [n.decode() if isinstance(n, bytes) else n for n in f.get_variation_names()]
    except OSError:
        names = []  # fonte estatica: o peso vem do arquivo
    notes = []
    if names:
        if weight not in names:
            if weight_given:
                raise BrandError(f"--weight {weight!r} is not a named instance of this variable font. "
                                 f"Available: {', '.join(names)}")
            fallback = next((n for n in ("Bold", "SemiBold", "ExtraBold", "Medium", "Regular") if n in names), names[-1])
            notes.append(f"weight {weight!r} not in the font; using {fallback!r}")
            weight = fallback
        notes.append(f"variable font, instances: {', '.join(names)}")
    else:
        notes.append("static font: the weight comes from the file itself (--weight is only recorded)")
    return weight, names, notes


def check_logo(path, width_flag, allow_opaque):
    from PIL import Image
    if not os.path.isfile(path):
        raise BrandError(f"logo file not found: {path}")
    try:
        im = Image.open(path)
        im.load()
    except Exception as err:
        raise BrandError(f"could not open the logo {path}: {err}")
    rgba = im.convert("RGBA")
    alpha = rgba.split()[3]
    lo, hi = alpha.getextrema()
    has_alpha = lo < 255
    if not has_alpha and not allow_opaque:
        raise BrandError("the logo has no transparency (every pixel is opaque), so it would show a solid box over "
                         "the video. Export a PNG with a transparent background. "
                         "(Ignore with --allow-opaque-logo if a solid box is really what you want.)")
    ratio = rgba.width / rgba.height
    # amostra os pixels visiveis para dizer se o logo e claro ou escuro (so informativo)
    small = rgba.resize((max(1, rgba.width // 8), max(1, rgba.height // 8)))
    pix = small.load()
    px = [pix[x, y] for y in range(small.height) for x in range(small.width) if pix[x, y][3] > 128]
    mean_l = sum(luminance("#%02X%02X%02X" % p[:3]) for p in px) / len(px) if px else 0.0
    # altura visual ~90px (a do logo do Clube: 200x90), largura entre 160 e 340
    suggested = max(160, min(340, int(round(90 * ratio / 10.0) * 10)))
    width = width_flag or suggested
    height = round(rgba.height * width / rgba.width)
    notes = [f"{rgba.width}x{rgba.height}px, aspect ratio {ratio:.2f}:1 "
             f"({'wordmark/horizontal' if ratio >= 3 else 'compact' if ratio < 1.5 else 'medium'})",
             f"transparency: {'yes' if has_alpha else 'NO'}",
             f"visible pixels are {'light' if mean_l > 0.5 else 'dark'} (mean luminance {mean_l:.2f})",
             f"width {width}px -> about {height}px tall in the 1080x1920 frame"
             + ("" if width_flag else " (suggested from the aspect ratio)")]
    if mean_l < 0.25:
        notes.append("hint: a dark logo disappears over dark backgrounds; check the preview or use the white version")
    return width, notes


def slugify_check(slug):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug or ""):
        raise BrandError("--slug must be lowercase letters, digits and hyphens (e.g. minha-marca), "
                         f"and cannot start with '_' (got {slug!r})")
    return slug


# ---------------------------------------------------------------- listagem

def brand_label(slug, brand):
    if brand.get("name"):
        return brand["name"]
    readme = os.path.join(BRANDS, slug, "README.md")
    if os.path.exists(readme):
        first = open(readme, encoding="utf-8").readline()
        m = re.match(r"#\s*(.+?)\s+[—-]\s+", first)
        if m:
            return m.group(1)
    return slug


def list_brands():
    rows = []
    for slug in sorted(os.listdir(BRANDS)):
        path = os.path.join(BRANDS, slug, "brand.json")
        if slug.startswith("_") or not os.path.isfile(path):
            continue
        b = json.load(open(path, encoding="utf-8"))
        cap = b.get("captions", {})
        sounds = 0
        for sub in ("music", "sfx"):
            d = os.path.join(BRANDS, slug, "sound", sub)
            if os.path.isdir(d):
                sounds += sum(1 for f in os.listdir(d) if f.lower().endswith((".mp3", ".wav")))
        rows.append((slug, brand_label(slug, b), os.path.basename(cap.get("font_file", "-")), cap.get("weight", "-"),
                     cap.get("color", "-"), b.get("look", "none"), f"{b.get('speed', 1.25)}x",
                     "yes" if b.get("logo") else "no", "yes" if b.get("fine_print") else "no", str(sounds)))
    if not rows:
        print("No brands yet. Create one with: ./ev brand --slug <slug> --font <file> ...")
        return
    head = ("slug", "name", "font", "weight", "fill", "look", "speed", "logo", "fine print", "sounds")
    widths = [max(len(str(r[i])) for r in rows + [head]) for i in range(len(head))]
    for r in [head] + rows:
        print("  ".join(str(c).ljust(w) for c, w in zip(r, widths)))


# ---------------------------------------------------------------- criacao

def name_defaults(name):
    """Palavras com maiuscula viram nomes proprios; o nome inteiro nunca quebra entre blocos."""
    words = [w for w in re.findall(r"[\w'-]+", name, flags=re.UNICODE) if w[:1].isupper()]
    keep = [name] if len(name.split()) > 1 else []
    return words, keep


def build_brand_json(a, weight, logo_width, fine_print_weight):
    brand = json.load(open(os.path.join(TEMPLATE, "brand.json"), encoding="utf-8"))
    for key in [k for k in brand if k.startswith("_fine_print") or k.startswith("_logo")]:
        del brand[key]
    today = datetime.date.today().isoformat()
    nouns, keep = name_defaults(a["name"])
    brand = {"_sobre": f"Estilo fixo da marca {a['name']} para anuncio em video com apresentador. Criado em {today} "
                       "por scripts/new_brand.py (docs/09-onboarding-de-marca.md). Cada plan.json de video herda "
                       "daqui e so sobrescreve o que for dele.",
             "name": a["name"], **{k: v for k, v in brand.items() if k != "_sobre"}}
    brand["speed"] = a["speed"]
    brand["look"] = a["look"]
    cap = brand["captions"]
    cap.update({"font_file": f"fonts/{os.path.basename(a['font'])}", "weight": weight, "color": a["fill"],
                "stroke_color": a["stroke"], "pos_y": a["pos_y"], "proper_nouns": nouns, "keep_together": keep})
    if a.get("fine_print_file"):
        brand["fine_print"] = {"file": "fine-print.txt", "size": 21, "weight": fine_print_weight, "max_width": 0.9,
                               "margin_bottom": 56, "color": "#FFFFFF", "alpha": 225, "shade_alpha": 150}
    if a.get("logo"):
        brand["logo"] = {"file": f"logo/{os.path.basename(a['logo'])}", "width": logo_width, "top": 80,
                         "shadow": True, "shadow_alpha": 0.45}
    brand["sound_defaults"] = {"target_lufs": -14, "music_db": -27, "tick_db": -22, "dropout_db": -30,
                               "music_presence": a["music_presence"],
                               "_leveling": "trilha em 'presence' e efeitos em 'lu' (nivel percebido). "
                                            "Ver docs/05-som.md 4a."}
    why = {"framing": f"{a['framing']} ({FRAMING_TEXT[a['framing']]}): legenda a {a['pos_y']}% da altura, "
                      "logo a 80px do topo",
           "captions": f"preenchimento {a['fill']}, traco {a['stroke']}; fonte {os.path.basename(a['font'])} {weight}",
           "look": a["look"] + (" (comecar sem correcao de cor e mostrar as opcoes lado a lado)"
                                if a["look"] == "none" else ""),
           "speed": f"{a['speed']}x"}
    if a.get("logo"):
        why["logo"] = f"{os.path.basename(a['logo'])}, {logo_width}px de largura (aspecto e largura medidos no onboarding)"
    why["fine_print"] = ("texto legal verbatim em fine-print.txt" if a.get("fine_print_file")
                         else "sem letras miudas")
    brand["_por_que"] = why
    return brand


def brand_readme(a, brand):
    cap = brand["captions"]
    rows = [("formato / ritmo", f"1080x1920, -14 LUFS, pausas > 0,45s encurtadas, **{a['speed']}x**"),
            ("cor", f"look `{a['look']}`"),
            ("legenda", f"`{cap['font_file']}` {cap['weight']}, preenchimento **{a['fill']}**, traco `{a['stroke']}`; "
                        f"{cap['pos_y']}% da altura, ate 4 palavras, minusculas"),
            ("logo", (f"`{brand['logo']['file']}`, {brand['logo']['width']}px, centralizado, 80px do topo"
                      if brand.get("logo") else "sem logo")),
            ("rodape", "`fine-print.txt` verbatim" if brand.get("fine_print") else "sem letras miudas"),
            ("trilha / efeitos", "ainda nao gerados — ver `sound/SONS.md` e `sound/STARTER-KIT.md` do template")]
    body = "\n".join(f"| **{k}** | {v} |" for k, v in rows)
    return (f"# {a['name']} — o estilo em uma tela\n\n"
            f"Criado em {datetime.date.today().isoformat()} com `./ev brand` (enquadramento: "
            f"{FRAMING_TEXT[a['framing']]}). Valores em `brand.json`; as decisoes e o porque ficam em `_por_que`.\n\n"
            f"| | |\n|---|---|\n{body}\n\n"
            "## Muda por campanha — confira antes de cada video novo\n\n"
            "- (preencha: o que muda de uma campanha para outra, ex. datas das letras miudas)\n")


def sons_md(a):
    return (f"# Biblioteca de som — {a['name']}\n\n"
            "**Antes de gerar som novo, procure aqui.** Ainda vazia: gere o kit basico seguindo "
            "`brands/_template/sound/STARTER-KIT.md` (geracao paga: so com permissao, `estimate_only` primeiro).\n\n"
            "## Trilha\n\n| arquivo | dura | BPM | medicao | papel |\n|---|---|---|---|---|\n\n"
            "## Efeitos\n\n| arquivo | dura | pico | som util | papel |\n|---|---|---|---|---|\n\n"
            "## Procedencia\n\n| arquivos | modelo | variacoes x custo | prompt (verbatim) |\n|---|---|---|---|\n")


def create_brand(a, dest):
    exists = os.path.isdir(dest)
    if exists and not a["force"]:
        raise BrandError(f"brands/{a['slug']} already exists. Choose another --slug or pass --force "
                         "(it overwrites brand.json/logo/font but never deletes sounds).")
    shutil.copytree(TEMPLATE, dest, dirs_exist_ok=True)
    for sub in ("fonts", "logo"):
        os.makedirs(os.path.join(dest, sub), exist_ok=True)
    # o STARTER-KIT fica so no template; a marca tem o seu SONS.md
    kit = os.path.join(dest, "sound", "STARTER-KIT.md")
    if os.path.exists(kit):
        os.remove(kit)
    shutil.copyfile(a["font"], os.path.join(dest, "fonts", os.path.basename(a["font"])))
    if a.get("logo"):
        shutil.copyfile(a["logo"], os.path.join(dest, "logo", os.path.basename(a["logo"])))
    if a.get("fine_print_file"):
        shutil.copyfile(a["fine_print_file"], os.path.join(dest, "fine-print.txt"))  # bytes iguais: verbatim
    for sub in ("fonts", "logo"):
        d = os.path.join(dest, sub)
        if len(os.listdir(d)) > 1 and os.path.exists(os.path.join(d, ".gitkeep")):
            os.remove(os.path.join(d, ".gitkeep"))
    return exists


# ---------------------------------------------------------------- preview

def probe_display_size(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:stream_side_data=rotation", "-of", "json", video],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise BrandError(f"ffprobe could not read {video}: {out.stderr.strip()[-200:]}")
    info = json.loads(out.stdout)["streams"][0]
    w, h = info["width"], info["height"]
    rot = next((abs(int(sd["rotation"])) for sd in info.get("side_data_list", []) if "rotation" in sd), 0)
    return (h, w) if rot in (90, 270) else (w, h)


def render_preview(dest, brand, video, at, notes):
    """Quadro do video + legenda de exemplo + logo + letras miudas, pelas mesmas funcoes do edit.py."""
    from PIL import Image
    if not shutil.which("ffmpeg"):
        raise BrandError("ffmpeg not found (needed for --frame). Run ./ev setup --check")
    video = os.path.expanduser(video)
    if not os.path.isfile(video):
        raise BrandError(f"--frame video not found: {video}")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import edit  # o mesmo codigo que renderiza o video de verdade

    w, h = brand.get("output_size", [1080, 1920])
    dw, dh = probe_display_size(video)
    if abs(dw / dh - w / h) > 0.02:
        notes.append(f"warning: the sample video is {dw}x{dh}, not {w}:{h}. edit.py scales to {w}x{h} without "
                     "cropping, so the preview (and the real render) will look stretched.")
    edit.BRAND_DIR = dest
    edit.FONT_PATH = os.path.join(dest, brand["captions"]["font_file"])
    look = edit.LOOKS[brand.get("look", "none")]
    with tempfile.TemporaryDirectory() as tmp:
        frame = os.path.join(tmp, "frame.png")
        proc = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(at), "-i", video, "-frames:v", "1",
                               "-vf", f"scale={w}:{h}:flags=lanczos,setsar=1,{look}", frame],
                              capture_output=True, text=True)
        if proc.returncode != 0 or not os.path.exists(frame):
            raise BrandError(f"could not extract a frame at {at}s: {proc.stderr.strip()[-200:]}")
        base = Image.open(frame).convert("RGBA")

        overlay = os.path.join(tmp, "overlay.png")
        if brand.get("fine_print"):
            edit.render_fine_print(brand["fine_print"], overlay, w, h)
        else:
            Image.new("RGBA", (w, h), (0, 0, 0, 0)).save(overlay)
        if brand.get("logo"):
            edit.render_logo(brand["logo"], overlay, w)
        base.alpha_composite(Image.open(overlay).convert("RGBA"))

        words = [{"t": t, "s": 0.2 * i, "e": 0.2 * i + 0.18} for i, t in enumerate(SAMPLE_CAPTION.split())]
        blocks, _, stroke, size = edit.render_captions(words, brand, os.path.join(tmp, "captions"), w, h, 2.0)
        base.alpha_composite(Image.open(os.path.join(tmp, "captions", "block_000.png")).convert("RGBA"))
        out = os.path.join(dest, "preview.png")
        base.convert("RGB").save(out)
    notes.append(f"caption rendered at {size}px with a {stroke}px stroke (stroke is capped by the counter-form check)")
    return out


# ---------------------------------------------------------------- main

def parse_args(argv):
    p = argparse.ArgumentParser(description="Scaffold a new brand under brands/<slug> (see docs/09-onboarding-de-marca.md).",
                                formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("--list", action="store_true", help="list existing brands and exit")
    p.add_argument("--answers", help="JSON file with the same fields as the flags")
    p.add_argument("--slug")
    p.add_argument("--name")
    p.add_argument("--logo")
    p.add_argument("--font")
    p.add_argument("--weight")
    p.add_argument("--fill")
    p.add_argument("--stroke")
    p.add_argument("--fine-print-file", dest="fine_print_file")
    p.add_argument("--look", choices=KNOWN_LOOKS)
    p.add_argument("--framing", choices=sorted(FRAMING_POS_Y))
    p.add_argument("--pos-y", dest="pos_y", type=float)
    p.add_argument("--speed", type=float)
    p.add_argument("--logo-width", dest="logo_width", type=int)
    p.add_argument("--music-presence", dest="music_presence", type=float)
    p.add_argument("--frame", help="sample video to render brands/<slug>/preview.png from")
    p.add_argument("--at", type=float, help="second of the sample frame (default 5)")
    p.add_argument("--allow-opaque-logo", dest="allow_opaque_logo", action="store_true", default=None)
    p.add_argument("--force", action="store_true")
    p.add_argument("--preview-only", dest="preview_only", action="store_true",
                   help="only re-render preview.png of an existing brand from its current brand.json")
    return p.parse_args(argv)


def merge_answers(args):
    a = {k: getattr(args, k, None) for k in FIELDS}
    if args.answers:
        path = os.path.expanduser(args.answers)
        try:
            data = json.load(open(path, encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as err:
            raise BrandError(f"could not read --answers {path}: {err}")
        base = os.path.dirname(os.path.abspath(path))
        for k, v in data.items():
            key = k.replace("-", "_")
            if key.startswith("_"):
                continue
            if key not in FIELDS:
                raise BrandError(f"unknown field {k!r} in {path}. Valid: {', '.join(FIELDS)}")
            if a.get(key) is None:  # flag na linha de comando vence
                if key in ANSWER_PATHS and isinstance(v, str) and not os.path.isabs(os.path.expanduser(v)) \
                        and not os.path.exists(os.path.expanduser(v)):
                    v = os.path.join(base, v)  # relativo ao arquivo de respostas
                a[key] = v
    for key in ANSWER_PATHS:
        if a.get(key):
            a[key] = os.path.abspath(os.path.expanduser(a[key]))
    return a


def preview_only(args):
    """Refaz so o preview.png de uma marca que ja existe, com o brand.json atual."""
    slug = slugify_check(args.slug)
    dest = os.path.join(BRANDS, slug)
    path = os.path.join(dest, "brand.json")
    if not os.path.isfile(path):
        raise BrandError(f"brands/{slug}/brand.json does not exist (create the brand first)")
    if not args.frame:
        raise BrandError("--preview-only needs --frame <video> (and optionally --at <seconds>)")
    brand = json.load(open(path, encoding="utf-8"))
    notes = []
    preview = render_preview(dest, brand, os.path.abspath(os.path.expanduser(args.frame)),
                             5.0 if args.at is None else args.at, notes)
    for n in notes:
        print(f"  preview: {n}")
    print(f"Preview: {preview}")
    return 0


def main(argv=None):
    args = parse_args(argv)
    if args.list:
        list_brands()
        return 0
    need_pillow()
    if args.preview_only:
        return preview_only(args)
    a = merge_answers(args)
    a["slug"] = slugify_check(a.get("slug"))
    a["name"] = a.get("name") or a["slug"]
    if not a.get("font"):
        raise BrandError("--font is required (a .ttf/.otf file for the captions)")
    a["fill"] = check_hex(a.get("fill") or "#FFFFFF", "--fill")
    a["stroke"] = check_hex(a.get("stroke") or "#030303", "--stroke")
    a["look"] = a.get("look") or "none"
    a["framing"] = a.get("framing") or "seated"
    if a["framing"] not in FRAMING_POS_Y:
        raise BrandError(f"--framing must be one of {', '.join(FRAMING_POS_Y)}")
    a["pos_y"] = a["pos_y"] if a.get("pos_y") is not None else FRAMING_POS_Y[a["framing"]]
    a["pos_y"] = int(a["pos_y"]) if float(a["pos_y"]).is_integer() else a["pos_y"]
    a["speed"] = a["speed"] if a.get("speed") is not None else 1.25
    a["music_presence"] = a["music_presence"] if a.get("music_presence") is not None else 0
    a["force"] = bool(args.force)
    if a.get("at") is None:
        a["at"] = 5.0
    # sanidade do look contra o que o edit.py realmente sabe fazer
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        import edit
        if a["look"] not in edit.LOOKS:
            raise BrandError(f"--look {a['look']!r} is not in edit.py LOOKS ({', '.join(edit.LOOKS)})")
    except ImportError:
        pass

    notes = []
    weight_given = a.get("weight") is not None
    weight, instances, font_notes = check_font(a["font"], a.get("weight") or "Bold", weight_given)
    fine_weight = "SemiBold" if (not instances or "SemiBold" in instances) else weight
    if instances and fine_weight != "SemiBold":
        font_notes.append(f"fine print uses {fine_weight!r} (the font has no 'SemiBold' instance)")
    logo_width = None
    logo_notes = []
    if a.get("logo"):
        logo_width, logo_notes = check_logo(a["logo"], a.get("logo_width"), bool(a.get("allow_opaque_logo")))
    else:
        logo_notes.append("no --logo: the brand will have no logo (add one later and a 'logo' block in brand.json)")
    if a.get("fine_print_file"):
        if not os.path.isfile(a["fine_print_file"]):
            raise BrandError(f"fine print file not found: {a['fine_print_file']}")
        if not open(a["fine_print_file"], encoding="utf-8").read().strip():
            raise BrandError("the fine print file is empty")
    ratio = contrast(a["fill"], a["stroke"])
    contrast_note = f"caption fill {a['fill']} on stroke {a['stroke']}: contrast {ratio:.1f}:1"
    if ratio < 4.5:
        contrast_note += "  <- LOW (below 4.5:1); pick a lighter fill or a darker stroke"

    dest = os.path.join(BRANDS, a["slug"])
    brand = build_brand_json(a, weight, logo_width, fine_weight)
    existed = create_brand(a, dest)
    json.dump(brand, open(os.path.join(dest, "brand.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(dest, "brand.json"), "a").write("\n")
    for fname, content in (("README.md", brand_readme(a, brand)), (os.path.join("sound", "SONS.md"), sons_md(a))):
        target = os.path.join(dest, fname)
        if not os.path.exists(target) or not existed:
            open(target, "w", encoding="utf-8").write(content)

    print(f"{'Updated' if existed else 'Created'} brands/{a['slug']}/")
    print("\nChecks:")
    for n in font_notes:
        print(f"  font:    {n}")
    for n in logo_notes:
        print(f"  logo:    {n}")
    print(f"  colors:  {contrast_note}")
    print(f"  framing: {a['framing']} -> captions at {a['pos_y']}% of the height, logo 80px from the top")
    print(f"  fine print: {'copied verbatim to fine-print.txt' if a.get('fine_print_file') else 'none'}")

    if a.get("frame"):
        try:
            preview = render_preview(dest, brand, a["frame"], a["at"], notes)
        except BrandError as err:
            print(f"\nBrand created, but the preview failed: {err}", file=sys.stderr)
            return 1
        for n in notes:
            print(f"  preview: {n}")
        print(f"\nPreview: {preview}")
    else:
        print("\nNo preview rendered. Add --frame <video> --at <seconds> to see captions, logo and fine print "
              "over a real frame (always do this before fixing pos_y).")
    print("\nNext: look at the preview, adjust brand.json, then follow docs/09-onboarding-de-marca.md "
          "(look, sound identity, brand README).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrandError as err:
        print(f"error: {err}", file=sys.stderr)
        sys.exit(2)
