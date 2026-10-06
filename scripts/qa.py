"""QA da máquina sobre o vídeo final — roda ANTES de mandar para a pessoa. Reprovado não sobe.

Uso:
    python3 scripts/qa.py output/<marca>/<arquivo>.mp4 [--sheet] [--size 1920x1080]

Confere: 1080×1920, 29,97 fps, H.264 + AAC, loudness −14 ±0,5 LUFS, pico verdadeiro ≤ −1 dBTP,
e se vídeo e áudio terminam juntos (±0,15s). --sheet grava uma folha de contato (1 frame a cada 4s)
ao lado do vídeo, para olhar legenda, logo e rodapé sem abrir o player.
"""
import json
import os
import re
import subprocess
import sys


def main():
    path = sys.argv[1]
    want_w, want_h = (1080, 1920)
    if "--size" in sys.argv:  # custom output_size in the plan (e.g. 1920x1080)
        want_w, want_h = (int(x) for x in sys.argv[sys.argv.index("--size") + 1].lower().split("x"))
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                      "stream=codec_type,codec_name,width,height,r_frame_rate,duration",
                                      "-of", "json", path], capture_output=True, text=True, check=True).stdout)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next(s for s in info["streams"] if s["codec_type"] == "audio")
    out = subprocess.run(["ffmpeg", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    summary = out[out.rfind("Summary"):]
    lufs = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summary).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summary).group(1))
    checks = [
        (f"resolução {want_w}×{want_h}", (v["width"], v["height"]) == (want_w, want_h), f"{v['width']}×{v['height']}"),
        ("29,97 fps", v["r_frame_rate"] == "30000/1001", v["r_frame_rate"]),
        ("H.264 + AAC", v["codec_name"] == "h264" and a["codec_name"] == "aac", f"{v['codec_name']} + {a['codec_name']}"),
        ("loudness −14 ±0,5 LUFS", abs(lufs + 14) <= 0.5, f"{lufs} LUFS"),
        ("pico ≤ −1 dBTP", tp <= -1.0, f"{tp} dBTP"),
        ("vídeo e áudio juntos (±0,15s)", abs(float(v["duration"]) - float(a["duration"])) <= 0.15,
         f"vídeo {float(v['duration']):.2f}s · áudio {float(a['duration']):.2f}s"),
    ]
    ok = True
    for name, passed, got in checks:
        ok &= passed
        print(f"{'✅' if passed else '❌'} {name:<32} {got}")
    if "--sheet" in sys.argv:
        sheet = path.rsplit(".", 1)[0] + "_contato.jpg"
        cols = max(1, int(float(v["duration"]) // 4) + 1)  # 1 quadro a cada 4s, o vídeo inteiro
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", f"fps=1/4,scale=270:-1,tile={cols}x1",
                        "-frames:v", "1", sheet], check=True)
        print(f"folha de contato: {sheet}")
    print("APROVADO pela máquina" if ok else "REPROVADO — conserte antes de mandar")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
