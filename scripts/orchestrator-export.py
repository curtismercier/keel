#!/usr/bin/env python3
"""Export generator: select the topology units whose Visibility matches --target, enumerate their
files (git ls-files), run the export gate (orchestrator-export-check.py: (a)+(b)+(c)) over that
set. PASS -> print the manifest, exit 0. FAIL -> print violations, exit 1. Stdlib only."""
import argparse, importlib.util, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
TARGET_VIS = {"public": "public-apache", "private": "private-ent"}


def load_gate():
    spec = importlib.util.spec_from_file_location("export_check", os.path.join(HERE, "orchestrator-export-check.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def select_units(units, target):
    want = TARGET_VIS[target]
    return sorted(u for u, (vis, _lic) in units.items() if vis == want)


def list_files(root, unit_dirs):
    """git ls-files under each unit dir, relative to root."""
    files = []
    for u in unit_dirs:
        out = subprocess.run(["git", "ls-files", "--", u], cwd=root, capture_output=True, text=True, check=True)
        files += [l for l in out.stdout.splitlines() if l]
    return sorted(set(files))


def generate(gate, root, topology_text, target):
    """Return (files, violations). Gate runs with cwd=root so paths resolve for scrub."""
    units = gate.parse_units(topology_text)
    files = list_files(root, select_units(units, target))
    cwd = os.getcwd()
    os.chdir(root)
    try:
        v = gate.check(target, files, units)
        if target == "public":
            v += gate.scrub_files(files)
    finally:
        os.chdir(cwd)
    return files, v


def self_test():
    gate = load_gate()
    tmp = tempfile.mkdtemp(prefix="export-gen-")
    ok = True
    try:
        topo = ("| Unit | Kind | Role | Status | Visibility | License |\n|---|---|---|---|---|---|\n"
                "| `packages/pub` | lib | x | live | public-apache | Apache-2.0 |\n"
                "| `packages/priv` | lib | x | live | private-ent | proprietary |\n")
        secret = "s" + "k-" + "a1B2" * 6  # synthetic, assembled at runtime
        for rel, body in {"packages/pub/a.py": "print('ok')\n", "packages/pub/b.py": "x = 1\n",
                          "packages/priv/key.py": f"KEY = '{secret}'\n"}.items():
            p = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w").write(body)
        subprocess.run(["git", "init", "-q"], cwd=tmp, check=True)
        subprocess.run(["git", "add", "-A"], cwd=tmp, check=True)

        files, v = generate(gate, tmp, topo, "public")
        sel = files == ["packages/pub/a.py", "packages/pub/b.py"]
        print(f"public export: {len(files)} file(s) {files}")
        print("  expect only public unit:", "excludes private ✓" if sel else "WRONG SELECTION ✗")
        print(f"  gate: {len(v)} violation(s) -> expect PASS:", "passed ✓" if not v else f"✗ {v}")
        ok &= sel and not v

        files, v = generate(gate, tmp, topo, "private")
        psel = files == ["packages/priv/key.py"]
        print(f"private export: {len(files)} file(s) {files} -> expect only private unit:", "✓" if psel else "✗")
        ok &= psel

        # negative: leak a secret into the public unit, and a private file into public set
        open(os.path.join(tmp, "packages/pub/leak.py"), "w").write(f"T = '{secret}'\n")
        subprocess.run(["git", "add", "-A"], cwd=tmp, check=True)
        files, v = generate(gate, tmp, topo, "public")
        caught = any("leak.py" in x and "secret-sk" in x for x in v)
        print(f"planted leak in public unit: {len(v)} violation(s) -> expect FAIL:", "caught ✓" if caught else f"MISSED ✗ {v}")
        ok &= caught
        os.remove(os.path.join(tmp, "packages/pub/leak.py"))
        subprocess.run(["git", "add", "-A"], cwd=tmp, check=True)
        # negative: unit flipped to public while holding the secret (cond a/c via topology)
        flipped = topo.replace("private-ent | proprietary", "public-apache | Apache-2.0")
        files, v = generate(gate, tmp, flipped, "public")
        caught = any("secret-sk" in x for x in v)
        print(f"private unit flipped public: {len(v)} violation(s) -> expect FAIL:", "caught ✓" if caught else f"MISSED ✗ {v}")
        ok &= caught
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"temp dir removed: {not os.path.exists(tmp)}")
    print(f"self-test: {'OK' if ok else 'FAILED'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=list(TARGET_VIS))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.target:
        ap.error("--target or --self-test required")
    gate = load_gate()
    files, v = generate(gate, ROOT, open(gate.TOPOLOGY, encoding="utf-8").read(), a.target)
    if v:
        for x in v:
            print("EXPORT BLOCKED", x, file=sys.stderr)
        print(f"export target={a.target}: {len(files)} file(s), {len(v)} violation(s) -> FAIL")
        return 1
    print("\n".join(files))
    print(f"export target={a.target}: {len(files)} file(s), 0 violations -> PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
