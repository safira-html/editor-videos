"""Combinatorial outputs: every hook × body × CTA (or any blocks) from ONE recording.

Usage (through the launcher, so the right Python is used):
    python3 scripts/venv_run.py scripts/variants.py projects/<brand>/<ID>/plan.json --list
    python3 scripts/venv_run.py scripts/variants.py projects/<brand>/<ID>/plan.json [--jobs 3] [--dry] [--no-qa]
    python3 scripts/venv_run.py scripts/variants.py projects/<brand>/<ID>/plan.json --only h1-m2-c1 h2-m1-c1

plan.json gets a `variants` block (see docs/08-variacoes-e-saidas.md):
    "variants": {
      "order": ["hook", "body", "cta"],
      "blocks": {"hook": {"h1": {"keep": [[12.1, 17.4]]}, "h2": {"keep": [[40.2, 44.9]]}},
                 "body": {"m1": {...}, "m2": {...}}, "cta": {"c1": {...}, "c2": {...}}},
      "exclude": [["h2", "m1", "c2"]],   # optional, "*" is a wildcard
      "only": null                         # optional explicit list of combos
    }

Each combination becomes a derived plan in projects/<brand>/<ID>/variants/<combo>/plan.json (with
symlinks to the shared transcription), is rendered by edit.py into output/<brand>/<ID>_<combo>_vN.mp4
and checked by qa.py. The rest of plan.json (captions, sound anchors, overrides) applies to every combo.
"""
import itertools
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")


def load_variants(plan):
    v = plan.get("variants")
    if not v:
        raise SystemExit("plan.json has no 'variants' block — see docs/08-variacoes-e-saidas.md")
    order, blocks = v.get("order"), v.get("blocks")
    if not order or not blocks:
        raise SystemExit("'variants' needs 'order' (list of block names) and 'blocks'")
    for name in order:
        if name not in blocks or not blocks[name]:
            raise SystemExit(f"block '{name}' is in 'order' but has no options in 'blocks'")
        for opt, body in blocks[name].items():
            if not body.get("keep"):
                raise SystemExit(f"option '{opt}' of block '{name}' has no 'keep'")
            for a, b in body["keep"]:
                if b - a < 0.3:
                    raise SystemExit(f"option '{opt}' of block '{name}': take [{a}, {b}] is empty or too short")
    ids = [list(blocks[name]) for name in order]
    seen = [o for group in ids for o in group]
    if len(seen) != len(set(seen)):
        raise SystemExit("option ids must be unique across all blocks (they name the output files)")
    return order, blocks, ids


def matches(pattern, combo):
    return len(pattern) == len(combo) and all(p == "*" or p == c for p, c in zip(pattern, combo))


def expand(plan):
    order, blocks, ids = load_variants(plan)
    v = plan["variants"]
    combos = [tuple(c) for c in itertools.product(*ids)]
    if v.get("only"):
        combos = [c for c in combos if any(matches(o, c) for o in v["only"])]
    for pattern in v.get("exclude") or []:
        combos = [c for c in combos if not matches(pattern, c)]
    return order, blocks, combos


def version_of(output_name):
    m = re.search(r"_(v\d+)\.mp4$", output_name or "")
    return m.group(1) if m else "v1"


def derive(plan, project_dir, order, blocks, combo):
    """Derived plan for one combination: keep = the chosen takes in order, plus the block map for anchors."""
    name = "-".join(combo)
    vplan = {k: v for k, v in plan.items() if k not in ("variants", "keep", "keep_window", "_keep")}
    keep, block_map = [], []
    for block, option in zip(order, combo):
        takes = blocks[block][option]["keep"]
        keep += takes
        block_map.append({"name": block, "option": option, "ranges": len(takes)})
    vplan["keep"] = keep
    vplan["_blocks"] = block_map
    vplan["_combo"] = dict(zip(order, combo))
    pid = os.path.basename(os.path.abspath(project_dir))
    vplan["output_name"] = f"{pid}_{name}_{version_of(plan.get('output_name'))}.mp4"
    sound = vplan.get("sound")
    if sound and any(e.get("path") for e in sound.get("sfx", [])):
        print(f"  ! {name}: effects with 'path' (tick beds) are not supported with variants — dropped")
        vplan["sound"] = dict(sound, sfx=[e for e in sound["sfx"] if not e.get("path")])
    work = os.path.join(project_dir, "variants", name)
    os.makedirs(work, exist_ok=True)
    for shared in ("audio16k.wav", "words.json"):
        link = os.path.join(work, shared)
        if os.path.lexists(link):
            os.remove(link)
        target = os.path.join(project_dir, shared)
        try:
            os.symlink(os.path.relpath(target, work), link)
        except OSError:  # no symlinks (e.g. Windows without privileges): copy
            import shutil
            shutil.copy2(target, link)
    path = os.path.join(work, "plan.json")
    json.dump(vplan, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return path, vplan["output_name"], keep


def estimate(plan, keep):
    return sum(b - a for a, b in keep) / plan.get("speed", 1.25)


def run_one(plan_path, output, brand, extra, qa):
    cmd = [sys.executable, os.path.join(SCRIPTS, "edit.py"), plan_path, *extra]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return output, False, "edit.py failed: " + (r.stderr.strip().splitlines() or r.stdout.strip().splitlines() or ["?"])[-1]
    if "--dry" in extra:
        return output, True, r.stdout
    out_path = os.path.join(ROOT, "output", brand, output)
    if not qa:
        return output, True, "rendered (QA skipped)"
    q = subprocess.run([sys.executable, os.path.join(SCRIPTS, "qa.py"), out_path, "--sheet"], capture_output=True, text=True)
    ok = q.returncode == 0
    detail = "QA ok" if ok else "QA FAILED: " + " | ".join(l for l in q.stdout.splitlines() if l.startswith("❌"))
    return output, ok, detail


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        sys.exit(__doc__)
    plan_path = os.path.abspath(args[0])
    project_dir = os.path.dirname(plan_path)
    plan = json.load(open(plan_path, encoding="utf-8"))
    order, blocks, combos = expand(plan)
    if "--only" in args:
        wanted = [a for a in args[args.index("--only") + 1:] if not a.startswith("--")]
        combos = [c for c in combos if "-".join(c) in wanted]
        if not combos:
            sys.exit(f"--only matched nothing; valid combos come from --list")
    jobs = int(args[args.index("--jobs") + 1]) if "--jobs" in args else 2

    print(f"{len(combos)} combination(s) · order: {' → '.join(order)}")
    for c in combos:
        labels = [blocks[b][o].get("label", o) for b, o in zip(order, c)]
        keep = [t for b, o in zip(order, c) for t in blocks[b][o]["keep"]]
        print(f"  {'-'.join(c):<14} ~{estimate(plan, keep):5.1f}s  {' + '.join(labels)}")
    if "--list" in args:
        return

    derived = [derive(plan, project_dir, order, blocks, c) for c in combos]
    extra = ["--dry"] if "--dry" in args else []
    brand = plan["brand"]
    qa = "--no-qa" not in args
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = [pool.submit(run_one, p, out, brand, extra, qa) for p, out, _ in derived]
        results = [f.result() for f in futures]
    print()
    failed = 0
    for output, ok, detail in results:
        if "--dry" in args:
            print(f"== {output}\n{detail}")
        else:
            print(f"{'✅' if ok else '❌'} {output}  {detail}")
        failed += not ok
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
