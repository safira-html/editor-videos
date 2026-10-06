"""Roda um script com o Python que tem faster-whisper + numpy + Pillow (config.json -> whisper_python).

Uso:
    python3 scripts/venv_run.py scripts/transcribe.py <video> <pasta_do_projeto>
    python3 scripts/venv_run.py scripts/audio_tools.py <subcomando> ...

Existe para que nenhum caminho de maquina fique espalhado pelos scripts: ele mora so no config.json.
Se o config.json nao existe, copia o config.example.json e pede para rodar o setup.
"""
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "config.json")
EXAMPLE = os.path.join(ROOT, "config.example.json")


def resolve_path(value):
    """Resolve `~` e caminho relativo (relativo a raiz do projeto)."""
    value = os.path.expanduser(value)
    return value if os.path.isabs(value) else os.path.normpath(os.path.join(ROOT, value))


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python3 scripts/venv_run.py <script.py> [args...]")
    if not os.path.exists(CONFIG):
        if not os.path.exists(EXAMPLE):
            sys.exit(f"Missing {CONFIG} and {EXAMPLE}. Is this the editor-videos repo root?")
        shutil.copyfile(EXAMPLE, CONFIG)
        sys.exit("config.json did not exist, so I copied config.example.json to config.json.\n"
                 "Now run the setup (it creates the Python environment and checks ffmpeg):\n"
                 "    ./ev setup")
    try:
        cfg = json.load(open(CONFIG, encoding="utf-8"))
    except json.JSONDecodeError as err:
        sys.exit(f"config.json is not valid JSON ({err}). Fix it or delete it and run ./ev setup.")
    if "whisper_python" not in cfg:
        sys.exit("config.json has no 'whisper_python' key. Compare it with config.example.json.")
    python = resolve_path(cfg["whisper_python"])
    if not os.path.exists(python):
        sys.exit(f"Whisper Python not found at {python}.\n"
                 "Run ./ev setup to create it, or point 'whisper_python' in config.json "
                 "to a Python that has faster-whisper, numpy and Pillow.")
    env = dict(os.environ)
    if cfg.get("hf_offline", True):
        env["HF_HUB_OFFLINE"] = "1"
    env["EDITOR_WHISPER_MODEL"] = cfg.get("whisper_model", "mobiuslabsgmbh/faster-whisper-large-v3-turbo")
    os.execve(python, [python, *sys.argv[1:]], env)


if __name__ == "__main__":
    main()
