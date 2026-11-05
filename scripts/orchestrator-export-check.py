#!/usr/bin/env python3
"""Export-boundary gate: fail if a private-ent unit leaks into a public export set,
or a public-set file's unit is not Apache-compatible / not in topology, or a file carries
scrub findings (secrets, author paths, session ids, project denylist). Stdlib only."""
import argparse, os, re, subprocess, sys

TOPOLOGY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".orchestrator", "topology.md")
ORCH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".orchestrator")
# Generic leak classes. Patterns are split so this file never matches its own scrub.
GENERIC = {
    "secret-sk": re.compile("s" + "k-[A-Za-z0-9]{20,}"),
    "secret-ghp": re.compile("gh" + "p_[A-Za-z0-9]{20,}"),
    "abs-path": re.compile("/Us" + r"ers/[^/\s]+/"),
    "tilde-org": re.compile("(?<![\\w.])~" + "/[A-Z][A-Za-z0-9_-]*"),
    "session-id": re.compile(r"\bs[0-9]{2}-[0-9a-fA-F]{6}\b"),
}
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


# The three layers: one private shell, two public faces. `public` = the polished product core;
# `process` = the shown work (rings/flows) that sits between it and the rough private shell.
PUBLIC_TARGETS = {"public": "public-apache", "process": "public-process"}


def check(target, files, units):
    """Return list of violation strings (empty = pass). Every public target is partitioned:
    a set may carry ONLY its own visibility class, and never a private-ent unit."""
    bad = []
    if target not in PUBLIC_TARGETS:
        return bad  # private target may carry everything
    want = PUBLIC_TARGETS[target]
    for f in files:
        u = unit_of(f, units)
        if u is None:
            bad.append(f"(b) {f}: not in any topology unit")
            continue
        vis, lic = units[u]
        if vis == "private-ent":
            bad.append(f"(a) {f}: unit {u} is private-ent")
        elif vis != want:
            bad.append(f"(a) {f}: unit {u} is {vis}, but target '{target}' carries only {want}")
        elif lic not in OK_LICENSES:
            bad.append(f"(b) {f}: unit {u} license '{lic}' not Apache-compatible")
    return bad


def load_patterns(name, path=None):
    """One-regex-per-line file ('#' comments, blanks skipped). Default: optional file in
    .orchestrator/ (missing -> []). Explicit `path` (CLI flag): must exist."""
    if path is None:
        path = os.path.join(ORCH, name)
        if not os.path.isfile(path):
            return []
    return [re.compile(l.strip()) for l in open(path, encoding="utf-8")
            if l.strip() and not l.lstrip().startswith("#")]


def scrub_text(name, text, deny, allow):
    """Return 'scrub <name>:<line> [<class>] <match>' hits; a line matching any allow regex is exempt."""
    classes = list(GENERIC.items()) + [("denylist", d) for d in deny]
    hits = []
    for n, line in enumerate(text.splitlines(), 1):
        if any(r.search(line) for r in allow):
            continue
        for cls, rx in classes:
            for m in rx.finditer(line):
                hits.append(f"scrub {name}:{n} [{cls}] {m.group(0)}")
    return hits


def scrub_files(files, deny_path=None, allow_path=None):
    """CLI deny/allow files AUGMENT (union with) the .orchestrator/ ones."""
    deny, allow = load_patterns("scrub-denylist.txt"), load_patterns("scrub-allowlist.txt")
    if deny_path:
        deny += load_patterns(None, deny_path)
    if allow_path:
        allow += load_patterns(None, allow_path)
    hits = []
    for f in files:
        if os.path.isfile(f):
            try:
                hits += scrub_text(f, open(f, encoding="utf-8").read(), deny, allow)
            except UnicodeDecodeError:
                pass  # binary: not scannable as text
    return hits


def self_test():
    # The fixture is synthetic ON PURPOSE: a template's self-test must survive being copied into a
    # project whose units are named differently. Measured 2026-11-05 in `tidewater` — the earlier
    # version parsed this repo's own topology and asserted keel's `_template` rows, so a healthy
    # project failed its own gate self-test.
    fixture = ("| Unit | Kind | Role | Status | Visibility | License |\n|---|---|---|---|---|---|\n"
               "| `packages/core` | lib | x | live | public-apache | Apache-2.0 |\n"
               "| `apps/ui` | app | x | live | public-apache | Apache-2.0 |\n"
               "| `rings/tw01` | ring | x | live | public-process | MIT |\n"
               "| `workshop` | process | x | live | private-ent | proprietary |\n")
    units = parse_units(fixture)
    assert units, "fixture topology did not parse"
    units["packages/secret"] = ("private-ent", "proprietary")
    clean = ["packages/core/a.py", "apps/ui/b.py"]
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
    # the third layer: `process` carries ONLY public-process units, and never a private one
    v = check("process", ["rings/tw01/cycle.md"], units)
    print(f"process layer, its own unit: {len(v)} violation(s) -> expect PASS:",
          "passed ✓" if not v else f"false positive ✗ {v}")
    ok &= not v
    v = check("process", ["rings/tw01/cycle.md"] + planted, units)
    caught = any("packages/secret/key.py" in x for x in v)
    print(f"process layer + private file: {len(v)} violation(s) -> expect FAIL:",
          "caught ✓" if caught else f"MISSED ✗ {v}")
    ok &= caught
    v = check("process", clean, units)
    caught = len(v) == len(clean)
    print(f"process layer carrying core units: {len(v)} violation(s) -> expect FAIL:",
          "caught ✓" if caught else f"MISSED ✗ {v}")
    ok &= caught
    # scrub (condition c): synthetic leaks only, assembled at runtime
    deny, allow = [re.compile(r"AcmeClient")], [re.compile(r"intentional-example")]
    cases = {
        "sk secret": "key = " + "s" + "k-" + "a1B2" * 6,
        "ghp secret": "tok = " + "gh" + "p_" + "Z9y8" * 6,
        "abs path": "see /Us" + "ers/x/proj/file.py",
        "tilde org": "cd ~" + "/SomeOrg/repo",
        "session id": "log s" + "07-abc123 done",
        "denylist": "built for AcmeClient",
    }
    for label, txt in cases.items():
        h = scrub_text("sample", txt, deny, allow)
        print(f"scrub {label}: {len(h)} hit(s) -> expect FAIL:", "caught ✓" if h else "MISSED ✗")
        ok &= bool(h)
    h = scrub_text("sample", "plain text, version s1-ok, ~/lower, a/b/c", deny, allow)
    print(f"scrub clean: {len(h)} hit(s) -> expect PASS:", "passed ✓" if not h else f"false positive ✗ {h}")
    ok &= not h
    h = scrub_text("sample", "intentional-example /Us" + "ers/x/a", deny, allow)
    print(f"scrub allowlisted: {len(h)} hit(s) -> expect PASS:", "exempt ✓" if not h else f"allowlist ignored ✗ {h}")
    ok &= not h
    # CLI --denylist/--allowlist augment the file-based lists (temp files, cleaned up)
    import tempfile, shutil
    tmp = tempfile.mkdtemp()
    try:
        def w(n, t):
            q = os.path.join(tmp, n)
            open(q, "w", encoding="utf-8").write(t)
            return q
        dl, al = w("deny.txt", "# synthetic\nAcmeCorp\n"), w("allow.txt", "cli-allowed\n")
        tgt = w("t.txt", "built for AcmeCorp\n")
        base, h = scrub_files([tgt]), scrub_files([tgt], deny_path=dl)
        good = bool(h) and not base
        print(f"scrub cli-denylist: base {len(base)} hit(s), with flag {len(h)} -> expect FAIL:",
              "caught ✓" if good else "MISSED ✗")
        ok &= good
        pth = w("p.txt", "cli-allowed /Us" + "ers/x/a\n")
        base, h = scrub_files([pth]), scrub_files([pth], allow_path=al)
        good = bool(base) and not h
        print(f"scrub cli-allowlist: base {len(base)} hit(s), with flag {len(h)} -> expect PASS:",
              "exempt ✓" if good else "allowlist ignored ✗")
        ok &= good
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"self-test: {'OK' if ok else 'FAILED'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=["public", "process", "private"])
    ap.add_argument("--files", nargs="*", default=[])
    ap.add_argument("--scrub", action="store_true", help="scrub --files for leaks (implied by --target public|process)")
    ap.add_argument("--denylist", metavar="PATH", help="extra denylist regex file (augments .orchestrator/scrub-denylist.txt)")
    ap.add_argument("--allowlist", metavar="PATH", help="extra allowlist regex file (augments .orchestrator/scrub-allowlist.txt)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.target and not a.scrub:
        ap.error("--target or --scrub required")
    v = []
    if a.target:
        v += check(a.target, a.files, parse_units(open(TOPOLOGY).read()))
    if a.scrub or a.target in PUBLIC_TARGETS:
        v += scrub_files(a.files, a.denylist, a.allowlist)
    for x in v:
        print("EXPORT BLOCKED", x, file=sys.stderr)
    print(f"checked {len(a.files)} files for target={a.target or '-'}: {len(v)} violation(s)")
    return 1 if v else 0


if __name__ == "__main__":
    sys.exit(main())
