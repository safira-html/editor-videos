"""Monta uma cama de tic-tac travada no BPM da trilha.

Uso:
    python3 scripts/tick_bed.py <tick.mp3> <saida.wav> <bpm> <fase_s> <duracao_s> <janelas.json>

janelas.json: [{"from": 0.0, "to": 2.07}, {"from": 20.24, "to": 22.9, "double_from": 21.9}]
  - um tick por batida dentro de cada janela;
  - "double_from": a partir dali o tic-tac dobra (colcheias) — urgência que aperta antes do corte.
O tick alterna com um "tac" meio tom abaixo, para não soar como metrônomo.
"""
import array
import json
import subprocess
import sys
import wave

SR = 48000


def decode(path, rate=1.0):
    af = f"asetrate={int(SR * rate)},aresample={SR}" if rate != 1.0 else f"aresample={SR}"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-af", af, "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return array.array("h", raw)


def trim_to_onset(samples, threshold=2000):
    for i, v in enumerate(samples):
        if abs(v) > threshold:
            return samples[max(0, i - 48):]
    return samples


def main():
    tick_path, out, bpm, phase, duration, windows_path = sys.argv[1:7]
    bpm, phase, duration = float(bpm), float(phase), float(duration)
    windows = json.load(open(windows_path))
    tick = trim_to_onset(decode(tick_path))[: int(SR * 0.25)]
    tock = trim_to_onset(decode(tick_path, rate=0.944))[: int(SR * 0.25)]  # ~1 semitom abaixo
    bed = array.array("i", [0]) * int(SR * duration)
    period = 60.0 / bpm
    for w in windows:
        t, k = phase, 0
        while t < w["to"]:
            step = period / 2 if w.get("double_from") is not None and t >= w["double_from"] else period
            if t >= w["from"] - 1e-6:
                src = tick if k % 2 == 0 else tock
                start = int(t * SR)
                for i, v in enumerate(src):
                    if start + i < len(bed):
                        bed[start + i] += v
                k += 1
            t += step
    pcm = array.array("h", (max(-32767, min(32767, v)) for v in bed))
    with wave.open(out, "wb") as fh:
        fh.setnchannels(1)
        fh.setsampwidth(2)
        fh.setframerate(SR)
        fh.writeframes(pcm.tobytes())
    print(f"cama de tic-tac: {out} · {bpm} BPM · {len(windows)} janelas")


if __name__ == "__main__":
    main()
