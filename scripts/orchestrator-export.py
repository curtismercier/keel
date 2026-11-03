#!/usr/bin/env python3
"""Export generator: select the topology units whose Visibility matches --target, enumerate their
files (git ls-files), run the export gate (orchestrator-export-check.py: (a)+(b)+(c)) over that
set. PASS -> print the manifest, exit 0 (with --out <dir>: also copy the tree + marker + LICENSE).
FAIL -> print violations, exit 1, write nothing. Stdlib only."""
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


def write_tree(root, files, out, target):
    """Copy files into out (relative paths preserved) + .soma-core-export marker + LICENSE.
    Caller must have passed the gate; this never runs on a failing set."""
    for f in files:
        dst = os.path.join(out, f)
        os.makedirs(os.path.dirname(dst) or out, exist_ok=True)
        shutil.copy2(os.path.join(root, f), dst)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, ".soma-core-export"), "w", encoding="utf-8") as fh:
        fh.write(f"generated export tree ({target}) -- do not edit here; changes are applied upstream\n")
    lic = os.path.join(root, "LICENSE")
    if target == "public" and os.path.isfile(lic):
        shutil.copy2(lic, os.path.join(out, "LICENSE"))
    elif target == "private":
        with open(os.path.join(out, "LICENSE"), "w", encoding="utf-8") as fh:
            fh.write("Proprietary and confidential. All rights reserved. No license is granted.\n")
    else:
        print("warning: no LICENSE at repo root; public tree has none", file=sys.stderr)


def tree_files(out):
    return sorted(os.path.relpath(os.path.join(d, n), out).replace(os.sep, "/")
                  for d, _, ns in os.walk(out) for n in ns)


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
        open(os.path.join(tmp, "LICENSE"), "w").write("Apache License fixture\n")
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

        # tree: public export into --out holds only the public unit + marker + LICENSE, no private file
        files, v = generate(gate, tmp, topo, "public")
        out = os.path.join(tmp, "_out_pub")
        rc = main(["--target", "public", "--out", out], root=tmp, topo=topo)
        got = tree_files(out) if os.path.isdir(out) else []
        want = sorted(files + [".soma-core-export", "LICENSE"])
        tree_ok = rc == 0 and got == want and not any("priv" in g for g in got)
        print(f"public tree (rc={rc}): {got} -> expect only public unit + marker + LICENSE:", "✓" if tree_ok else f"✗ want {want}")
        ok &= tree_ok

        # negative: leak a secret into the public unit, and a private file into public set
        open(os.path.join(tmp, "packages/pub/leak.py"), "w").write(f"T = '{secret}'\n")
        subprocess.run(["git", "add", "-A"], cwd=tmp, check=True)
        files, v = generate(gate, tmp, topo, "public")
        caught = any("leak.py" in x and "secret-sk" in x for x in v)
        print(f"planted leak in public unit: {len(v)} violation(s) -> expect FAIL:", "caught ✓" if caught else f"MISSED ✗ {v}")
        ok &= caught
        # negative: gate FAIL must refuse -- non-zero exit, --out dir never created
        out2 = os.path.join(tmp, "_out_leak")
        rc = main(["--target", "public", "--out", out2], root=tmp, topo=topo)
        refused = rc != 0 and not os.path.exists(out2)
        print(f"gate-failing tree (rc={rc}): out dir exists={os.path.exists(out2)} -> expect refusal:", "refused ✓" if refused else "LEAKING TREE ✗")
        ok &= refused
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


def main(argv=None, root=ROOT, topo=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=list(TARGET_VIS))
    ap.add_argument("--out", help="write the export tree (files + .soma-core-export + LICENSE) here; only if the gate passes")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.target:
        ap.error("--target or --self-test required")
    gate = load_gate()
    files, v = generate(gate, root, topo or open(gate.TOPOLOGY, encoding="utf-8").read(), a.target)
    if v:
        for x in v:
            print("EXPORT BLOCKED", x, file=sys.stderr)
        print(f"export target={a.target}: {len(files)} file(s), {len(v)} violation(s) -> FAIL")
        return 1
    if a.out:
        write_tree(root, files, a.out, a.target)
    print("\n".join(files))
    print(f"export target={a.target}: {len(files)} file(s), 0 violations -> PASS"
          + (f"; tree written to {a.out}" if a.out else ""), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
