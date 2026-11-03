#!/usr/bin/env python3
"""Export-boundary gate: fail if a private-ent unit leaks into a public export set,
or a public-set file's unit is not Apache-compatible / not in topology. Stdlib only."""
import argparse, os, re, subprocess, sys

TOPOLOGY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".orchestrator", "topology.md")
OK_LICENSES = {"apache-2.0", "mit", "bsd-2-clause", "bsd-3-clause", "isc"}


def parse_units(text):
    """Units table -> {unit_path: (visibility, license)}. Columns located by header name."""
    units, cols = {}, None
    for line in text.splitlines():
        if not line.startswith("|"):
            cols = None if cols and units else cols
            continue
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if cells and cells[0] == "Unit":
            cols = {n: i for i, n in enumerate(cells)}
        elif cols and "Visibility" in cols and not set(cells[0]) <= set("-: "):
            units[cells[0]] = (cells[cols["Visibility"]].lower(), cells[cols["License"]].lower())
    return units


def unit_of(path, units):
    path = os.path.normpath(path)
    best = None
    for u in units:
        if path == u or path.startswith(u.rstrip("/") + "/"):
            if best is None or len(u) > len(best):
                best = u
    return best


def check(target, files, units):
    """Return list of violation strings (empty = pass)."""
    bad = []
    if target != "public":
        return bad  # private target may carry everything
    for f in files:
        u = unit_of(f, units)
        if u is None:
            bad.append(f"(b) {f}: not in any topology unit")
            continue
        vis, lic = units[u]
        if vis == "private-ent":
            bad.append(f"(a) {f}: unit {u} is private-ent")
        elif lic not in OK_LICENSES:
            bad.append(f"(b) {f}: unit {u} license '{lic}' not Apache-compatible")
    return bad


def self_test():
    units = parse_units(open(TOPOLOGY).read())
    assert units, "no units parsed from topology.md"
    units = dict(units)
    units["packages/secret"] = ("private-ent", "proprietary")
    clean = ["packages/_template/a.py", "apps/_template/b.py"]
    planted = clean + ["packages/secret/key.py"]
    ok = True
    v = check("public", planted, units)
    print(f"planted ({len(planted)} files): {len(v)} violation(s) -> {v}")
    caught = len(v) > 0 and any("packages/secret/key.py" in x for x in v)
    print("  expect FAIL:", "caught ✓" if caught else "MISSED ✗")
    ok &= caught
    v = check("public", clean, units)
    print(f"clean ({len(clean)} files): {len(v)} violation(s)")
    print("  expect PASS:", "passed ✓" if not v else f"false positive ✗ {v}")
    ok &= not v
    print(f"self-test: {'OK' if ok else 'FAILED'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=["public", "private"])
    ap.add_argument("--files", nargs="*", default=[])
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.target:
        ap.error("--target required")
    units = parse_units(open(TOPOLOGY).read())
    v = check(a.target, a.files, units)
    for x in v:
        print("EXPORT BLOCKED", x, file=sys.stderr)
    print(f"checked {len(a.files)} files for target={a.target}: {len(v)} violation(s)")
    return 1 if v else 0


if __name__ == "__main__":
    sys.exit(main())
