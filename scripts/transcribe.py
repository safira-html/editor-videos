"""Transcreve um vídeo com tempo por palavra (faster-whisper large-v3-turbo, pt).

Uso (o launcher escolhe o Python certo a partir do config.json):
    python3 scripts/venv_run.py scripts/transcribe.py <video> <pasta_do_projeto>

Escreve na pasta do projeto: audio16k.wav (usado para medir silêncio), words.json e transcript.txt.
VAD desligado de propósito: queremos ver as pausas e as falas fora do roteiro para decidir o corte.
"""
import json
import os
import subprocess
import sys

from faster_whisper import WhisperModel

video, out_dir = sys.argv[1], sys.argv[2]
os.makedirs(out_dir, exist_ok=True)
audio = os.path.join(out_dir, "audio16k.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000", audio], check=True)
model = WhisperModel(os.environ.get("EDITOR_WHISPER_MODEL", "mobiuslabsgmbh/faster-whisper-large-v3-turbo"),
                     device="cpu", compute_type="int8")
segs, info = model.transcribe(audio, language="pt", word_timestamps=True, vad_filter=False,
                              condition_on_previous_text=False)
words, lines = [], []
for s in segs:
    for w in s.words:
        words.append({"t": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3), "p": round(w.probability, 2)})
    lines.append(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}")
json.dump(words, open(os.path.join(out_dir, "words.json"), "w"), ensure_ascii=False, indent=0)
open(os.path.join(out_dir, "transcript.txt"), "w").write("\n".join(lines) + "\n")
print(f"{video}: {len(words)} palavras")
