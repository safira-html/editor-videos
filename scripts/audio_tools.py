"""Medições de som — tudo que se mede ANTES de decidir, e DEPOIS de misturar.

Rode sempre pelo launcher (precisa de numpy; `vocals` precisa de faster-whisper):
    python3 scripts/venv_run.py scripts/audio_tools.py <subcomando> ...

Subcomandos:
  inspect <arquivos...>        duração, pico, média e onde há som de verdade (som gerado vem com silêncio
                               dentro, e às vezes vem MUDO — tap-a saiu com pico de −66 dB)
  beat <musica>                BPM, fase da batida (para travar o tic-tac) e os ataques do fim (o hit final)
  vocals <musica>              procura voz cantada (a geração de música pode vir com "Instrumental: False")
  words <plan.json> [chaves]   tempo de cada palavra JÁ no corte acelerado (onde pôr cada efeito)
  mix <pasta_do_projeto>       depois do render: quantos dB a trilha fica abaixo da voz e o nível
                               em cada dropout/efeito do plano
"""
import json
import os
import re
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000


def load(path, sr=SR):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(float)


def db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9) - 90.3


def lufs(path):
    out = subprocess.run(["ffmpeg", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1])


def cmd_inspect(files):
    for f in files:
        x = load(f)
        dur = len(x) / SR
        pk = 20 * np.log10(np.max(np.abs(x)) / 32768 + 1e-12)
        hop = int(SR * 0.02)
        n = len(x) // hop
        env = 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)) / 32768 + 1e-12)
        on = env > -45
        spans, start = [], None
        for i, v in enumerate(on):
            if v and start is None:
                start = i
            if not v and start is not None:
                spans.append((start * 0.02, i * 0.02))
                start = None
        if start is not None:
            spans.append((start * 0.02, n * 0.02))
        useful = sum(b - a for a, b in spans)
        flag = "  🚫 MUDO" if pk < -40 else ""
        print(f"{os.path.basename(f):<28} {dur:6.2f}s  pico {pk:6.1f} dB  som útil {useful:5.2f}s{flag}")
        print("   trechos com som:", " ".join(f"{a:.2f}-{b:.2f}" for a, b in spans[:12]), "…" if len(spans) > 12 else "")


def cmd_beat(path):
    x = load(path, 11025)
    hop = 64
    n = len(x) // hop
    e = np.log1p((x[:n * hop].reshape(n, hop) ** 2).sum(1))
    on = np.maximum(0, np.diff(e))
    fps = 11025 / hop
    best = None
    for bpm in np.arange(80, 170.01, 0.05):
        period = 60 / bpm
        for ph in np.arange(0, period, 0.005):
            idx = (np.arange(ph, min(30, len(on) / fps - 0.1), period) * fps).astype(int)
            s = on[idx].mean()
            if best is None or s > best[0]:
                best = (s, bpm, ph)
    _, bpm, ph = best
    print(f"{os.path.basename(path)}: {bpm:.2f} BPM · batidas em {ph:.3f}s + k×{60 / bpm:.4f}s")
    y = load(path)
    hop = 480
    n = len(y) // hop
    env = np.log1p((y[:n * hop].reshape(n, hop) ** 2).mean(1))
    d = np.diff(env)
    dur = len(y) / SR
    tail = np.argsort(d[int((dur - 12) * 100):])[-6:] + int((dur - 12) * 100)
    print("   ataques mais fortes nos últimos 12s:", " ".join(f"{i / 100:.2f}s" for i in sorted(tail)))
    print("   nível a cada 0,5s nos últimos 12s:",
          " ".join(f"{t:.1f}:{db(y[int(t * SR):int((t + 0.5) * SR)]):.0f}" for t in np.arange(dur - 12, dur, 0.5)))
    print("   → o 'hit final' é o último ataque forte antes do nível despencar; alinhe-o à última palavra")


def cmd_vocals(path):
    from faster_whisper import WhisperModel
    model = WhisperModel(os.environ.get("EDITOR_WHISPER_MODEL", "mobiuslabsgmbh/faster-whisper-large-v3-turbo"),
                         device="cpu", compute_type="int8")
    segs = list(model.transcribe(path, vad_filter=True)[0])
    if not segs:
        print(f"{os.path.basename(path)}: ✅ nenhuma voz detectada")
    for s in segs:
        print(f"{os.path.basename(path)}: ⚠️ [{s.start:.1f}-{s.end:.1f}] {s.text!r}")


def cmd_words(plan_path, keys):
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import edit as E
    plan = E.load_plan(os.path.abspath(plan_path))
    d = os.path.dirname(os.path.abspath(plan_path))
    sil = E.detect_silences(os.path.join(d, "audio16k.wav"), plan.get("silence_db", -35), 0.18)
    segs = E.build_segments(plan, sil)
    sp = plan["speed"]
    dur = sum(b - a for a, b in segs) / sp
    words = json.load(open(os.path.join(d, "words.json"), encoding="utf-8"))
    print(f"duração final {dur:.2f}s")
    for w in words:
        mid = (w["s"] + w["e"]) / 2
        if not any(a - 0.15 <= mid <= b + 0.15 for a, b in segs):
            continue
        if keys and not any(k.lower() in w["t"].lower() for k in keys):
            continue
        print(f"  {E.remap(w['s'], segs) / sp:6.2f}-{E.remap(w['e'], segs) / sp:6.2f}  {w['t']}")


# voz − fundo por oitava (125 Hz … 8 kHz) no Clube aprovado (C2556 v6, medido em 2026-09-25)
CLUBE_REF = [2.5, 22.1, 30.5, 21.9, 18.6, 7.8, 7.8]


def cmd_mix(project):
    mix = load(os.path.join(project, "mix_pre.wav"))
    voice_path = os.path.join(project, "stage_voice.wav")
    v = load(voice_path)
    g = 10 ** ((-18.8 - lufs(voice_path)) / 20)  # a voz entra no mix nivelada a −18,8 LUFS
    n = min(len(mix), len(v))
    bed = mix[:n] - v[:n] * g
    vv = v[:n] * g
    print(f"trilha+efeitos ficam {db(vv) - db(bed):.1f} dB abaixo da voz (RMS do vídeo inteiro)")

    plan0 = json.load(open(os.path.join(project, "plan.json"), encoding="utf-8"))
    mus = plan0.get("sound", {}).get("music", [])
    lo, hi = (int(mus[0].get("from", 0) * SR), int(min(mus[0].get("to", 1e9), n / SR) * SR)) if mus else (0, n)
    # por oitava, só onde a trilha toca: quanto a voz está acima do fundo (menor = fundo mais presente)
    bands = [125, 250, 500, 1000, 2000, 4000, 8000]
    ref = dict(zip(bands, CLUBE_REF))
    f_v, f_b = np.abs(np.fft.rfft(vv[lo:hi])) ** 2, np.abs(np.fft.rfft(bed[lo:hi])) ** 2
    fr = np.fft.rfftfreq(hi - lo, 1 / SR)
    row = []
    for c in bands:
        m = (fr >= c / 1.414) & (fr < c * 1.414)
        row.append(10 * np.log10(f_v[m].sum() + 1e-9) - 10 * np.log10(f_b[m].sum() + 1e-9))
    print(f"voz − fundo por oitava, só onde a trilha toca ({lo / SR:.1f}–{hi / SR:.1f}s); entre parênteses o Clube aprovado (C2556 v6):")
    print("   " + "  ".join(f"{c if c < 1000 else str(c // 1000) + 'k'}: {r:5.1f} ({ref[c]:4.1f})" for c, r in zip(bands, row)))
    print("   → número MENOR que o do Clube = fundo mais presente que o aprovado; mais de ~3 dB abaixo em 1–8k pede `presence` negativo")
    plan = json.load(open(os.path.join(project, "plan.json"), encoding="utf-8"))
    snd = plan.get("sound", {})
    for d in snd.get("dropouts", []):
        a, b = d["from"], d["to"]
        print(f"  dropout {a:6.2f}-{b:6.2f}: fundo em {db(bed[int(a * SR):int(b * SR)]):6.1f} dB")
    for e in snd.get("sfx", []):
        if e.get("path"):
            continue
        a = e["at"]
        b = a + e.get("length", 0.5)
        print(f"  {a:6.2f} {e.get('file', ''):<20} {db(bed[int(a * SR):int(b * SR)]):6.1f} dB")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    sub, args = sys.argv[1], sys.argv[2:]
    {"inspect": lambda: cmd_inspect(args), "beat": lambda: cmd_beat(args[0]),
     "vocals": lambda: [cmd_vocals(a) for a in args], "words": lambda: cmd_words(args[0], args[1:]),
     "mix": lambda: cmd_mix(args[0])}[sub]()


if __name__ == "__main__":
    main()
