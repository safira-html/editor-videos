"""Prepara (ou confere) a maquina para rodar o editor de videos.

Uso (so biblioteca padrao do Python, roda com o python3 do sistema):
    python3 scripts/setup.py                    cria o venv, instala as dependencias, escreve o config.json
    python3 scripts/setup.py --check            so verifica, nao instala nem cria nada
    python3 scripts/setup.py --download-model   alem do setup, baixa o modelo do Whisper (~1,6 GB)
    python3 scripts/setup.py --python /caminho/python3.12   forca um Python especifico

E idempotente: pode rodar de novo a qualquer momento (o pip so instala o que falta).
Atalho: ./ev setup [--check] [--download-model]
"""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "config.json")
EXAMPLE = os.path.join(ROOT, "config.example.json")
VENV_DIR = os.path.expanduser("~/.cache/editor-videos/venv")
VENV_PYTHON = os.path.join(VENV_DIR, "bin", "python")
PACKAGES = ["faster-whisper", "numpy", "pillow"]
IMPORTS = {"faster-whisper": "faster_whisper", "numpy": "numpy", "pillow": "PIL"}
DEFAULT_MODEL = "mobiuslabsgmbh/faster-whisper-large-v3-turbo"
# versoes de Python com wheels de faster-whisper/ctranslate2/onnxruntime
PREFERRED = [(3, 11), (3, 12), (3, 13), (3, 10), (3, 9)]

results = []  # (ok, label, detail) para o checklist final


def record(ok, label, detail=""):
    results.append((ok, label, detail))
    print(f"{'[ok]' if ok else '[!!]'} {label}" + (f" - {detail}" if detail else ""))


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def install_hint(tool):
    system = platform.system()
    if system == "Darwin":
        return "macOS: brew install ffmpeg" if tool == "ffmpeg" else "macOS: brew install python@3.12"
    if tool == "ffmpeg":
        return "Debian/Ubuntu: sudo apt install ffmpeg"
    return "Debian/Ubuntu: sudo apt install python3.12 python3.12-venv  (or python3.11 python3.11-venv)"


def check_ffmpeg():
    ok = True
    for tool in ("ffmpeg", "ffprobe"):
        path = shutil.which(tool)
        if path:
            first = run([path, "-version"]).stdout.splitlines()[:1]
            record(True, tool, first[0] if first else path)
        else:
            ok = False
            record(False, tool, f"not found. {install_hint('ffmpeg')}")
    return ok


def python_version(path):
    out = run([path, "-c", "import sys;print('%d.%d' % sys.version_info[:2])"])
    if out.returncode != 0:
        return None
    try:
        major, minor = out.stdout.strip().split(".")
        return int(major), int(minor)
    except ValueError:
        return None


def find_python(forced=None):
    """Devolve (caminho, versao) do melhor Python 3.9-3.13, ou (None, aviso)."""
    if forced:
        path = shutil.which(forced) or forced
        version = python_version(path) if os.path.exists(path) else None
        if not version:
            return None, f"--python {forced} does not run"
        return path, version
    found = {}
    names = [f"python{a}.{b}" for a, b in PREFERRED] + ["python3", "python"]
    for name in names:
        path = shutil.which(name)
        version = python_version(path) if path else None
        if version and version not in found:
            found[version] = path
    for version in PREFERRED:
        if version in found:
            return found[version], version
    too_new = [v for v in found if v >= (3, 14)]
    if too_new:
        v = max(too_new)
        return None, (f"only Python {v[0]}.{v[1]} found; faster-whisper/ctranslate2 may not have wheels for it yet. "
                      f"Install Python 3.11 or 3.12 ({install_hint('python')}), "
                      f"or force it with: python3 scripts/setup.py --python {found[v]}")
    return None, f"no Python 3.9-3.13 found. {install_hint('python')}"


def venv_imports_ok(python):
    """Quais pacotes importam no Python do venv."""
    missing = []
    for pkg in PACKAGES:
        if run([python, "-c", f"import {IMPORTS[pkg]}"]).returncode != 0:
            missing.append(pkg)
    return missing


def create_venv(python, version):
    if os.path.exists(VENV_PYTHON) and python_version(VENV_PYTHON):
        record(True, "venv", f"already exists at {VENV_DIR}")
        return True
    print(f"Creating venv with Python {version[0]}.{version[1]} at {VENV_DIR} ...")
    os.makedirs(os.path.dirname(VENV_DIR), exist_ok=True)
    out = run([python, "-m", "venv", VENV_DIR])
    if out.returncode != 0:
        record(False, "venv", f"could not create it: {out.stderr.strip()[-300:]}\n"
                              f"     On Debian/Ubuntu you may need: sudo apt install python{version[0]}.{version[1]}-venv")
        return False
    record(True, "venv", f"created at {VENV_DIR}")
    return True


def install_packages():
    missing = venv_imports_ok(VENV_PYTHON)
    if not missing:
        record(True, "python packages", "faster-whisper, numpy, pillow already installed")
        return True
    print(f"Installing {', '.join(missing)} (this can take a few minutes) ...")
    proc = subprocess.run([VENV_PYTHON, "-m", "pip", "install", "--disable-pip-version-check", *missing])
    still = venv_imports_ok(VENV_PYTHON)
    if proc.returncode != 0 or still:
        record(False, "python packages", f"failed: {', '.join(still or missing)}. "
                                          "If this Python is too new, re-run with --python <python3.11 or 3.12>")
        return False
    record(True, "python packages", "installed")
    return True


def write_config():
    if os.path.exists(CONFIG):
        try:
            cfg = json.load(open(CONFIG, encoding="utf-8"))
        except json.JSONDecodeError as err:
            record(False, "config.json", f"invalid JSON ({err}); delete it and run setup again")
            return False
        record(True, "config.json", f"exists (whisper_python = {cfg.get('whisper_python')})")
        return True
    if not os.path.exists(EXAMPLE):
        record(False, "config.json", "config.example.json is missing")
        return False
    shutil.copyfile(EXAMPLE, CONFIG)
    record(True, "config.json", "written from config.example.json")
    return True


def configured_python():
    """Python do config.json (com ~ e relativo a raiz), ou o do venv padrao."""
    if os.path.exists(CONFIG):
        try:
            value = json.load(open(CONFIG, encoding="utf-8")).get("whisper_python")
        except json.JSONDecodeError:
            value = None
        if value:
            value = os.path.expanduser(value)
            return value if os.path.isabs(value) else os.path.normpath(os.path.join(ROOT, value))
    return VENV_PYTHON


def model_name():
    if os.path.exists(CONFIG):
        try:
            return json.load(open(CONFIG, encoding="utf-8")).get("whisper_model", DEFAULT_MODEL)
        except json.JSONDecodeError:
            pass
    return DEFAULT_MODEL


def model_cached(python, name):
    """O modelo esta no cache local? (nao baixa nada)"""
    code = ("import sys\n"
            "from faster_whisper.utils import download_model\n"
            "try:\n"
            "    download_model(sys.argv[1], local_files_only=True)\n"
            "except Exception:\n"
            "    sys.exit(1)\n")
    return run([python, "-c", code, name]).returncode == 0


def download_model(python, name):
    print(f"Downloading Whisper model {name} (~1.6 GB). This runs once; it needs internet ...")
    env = {k: v for k, v in os.environ.items() if k != "HF_HUB_OFFLINE"}  # rede ligada so nesta execucao
    code = ("import sys\n"
            "from faster_whisper.utils import download_model\n"
            "print(download_model(sys.argv[1]))\n")
    proc = subprocess.run([python, "-c", code, name], env=env)
    ok = proc.returncode == 0
    record(ok, "whisper model", "downloaded" if ok else "download failed (check your connection and disk space)")
    return ok


def check_environment(python, model, want_download):
    """Parte comum de --check e setup: confere pacotes e modelo."""
    if not os.path.exists(python):
        record(False, "venv python", f"not found at {python}. Run ./ev setup")
        return
    version = python_version(python)
    record(True, "venv python", f"{python} (Python {version[0]}.{version[1]})" if version else python)
    missing = venv_imports_ok(python)
    if missing:
        record(False, "python packages", f"missing: {', '.join(missing)}. Run ./ev setup")
        return
    record(True, "python packages", "faster-whisper, numpy, pillow import fine")
    if model_cached(python, model):
        record(True, "whisper model", f"{model} is in the local cache")
    elif want_download:
        download_model(python, model)
    else:
        record(False, "whisper model", f"{model} is not cached yet (~1.6 GB). "
                                        "Run ./ev setup --download-model, or it is fetched on the first transcription "
                                        "if config.json has \"hf_offline\": false")


def print_summary(check_only):
    print("\n--- checklist ---")
    latest = {label: (ok, label, detail) for ok, label, detail in results}  # a ultima checagem de cada item vale
    results[:] = list(latest.values())
    for ok, label, detail in results:
        first = detail.splitlines()[0] if detail else ""
        print(f"{'[ok]' if ok else '[!!]'} {label:<16} {first}")
    bad = [r for r in results if not r[0]]
    essential = [r for r in bad if r[1] != "whisper model"]
    if not bad:
        print("\nAll set. Open this folder in Claude Code and say: edita o video <ID>")
    elif essential:
        print("\nSomething essential is missing. Fix the [!!] items above" +
              ("" if check_only else " and run ./ev setup again") + ".")
    else:
        print("\nEverything works except the Whisper model, which is downloaded on demand "
              "(./ev setup --download-model).")
    return 1 if essential else 0


def main():
    parser = argparse.ArgumentParser(description="Set up or check the editor-videos environment.")
    parser.add_argument("--check", action="store_true", help="only verify; install and create nothing")
    parser.add_argument("--download-model", action="store_true",
                        help="download the Whisper model (~1.6 GB) after setup")
    parser.add_argument("--python", help="force this Python interpreter for the venv")
    args = parser.parse_args()

    print(f"editor-videos setup ({platform.system()} {platform.machine()}, root {ROOT})\n")
    if platform.system() == "Windows":
        print("[!!] Windows is not supported (paths and venv layout assume macOS/Linux). Use WSL.")
        return 1

    ffmpeg_ok = check_ffmpeg()
    if args.check:
        if not os.path.exists(CONFIG):
            record(False, "config.json", "missing. Run ./ev setup (or copy config.example.json)")
        else:
            write_config()  # so reporta, o arquivo ja existe
        check_environment(configured_python(), model_name(), want_download=False)
        return print_summary(check_only=True)

    if not ffmpeg_ok:
        print("\nInstall ffmpeg first (see above), then run ./ev setup again.")
        return print_summary(check_only=False)

    python, info = find_python(args.python)
    if not python:
        record(False, "python", info)
        return print_summary(check_only=False)
    record(True, "system python", f"{python} (Python {info[0]}.{info[1]})")
    if info >= (3, 14):
        print("[warn] Python 3.14 may lack wheels for faster-whisper dependencies; if the install fails, use 3.11/3.12.")

    if create_venv(python, info) and install_packages():
        write_config()
        check_environment(configured_python(), model_name(), want_download=args.download_model)
    return print_summary(check_only=False)


if __name__ == "__main__":
    sys.exit(main())
