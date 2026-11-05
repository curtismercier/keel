# Export boundary — license partition gate

Public repos are generated exports of this monorepo, never hand-edited. Each unit in
`topology.md` carries `Visibility` + `License`. **Three layers, two public faces:** `public` (the polished core),
`process` (the shown work — rings/flows), and `private` (the rough workshop shell). The gate
`scripts/orchestrator-export-check.py` **FAILS the export** if:

- **(a)** a `private-ent` unit's file appears in a `public` or `process` export set;
- **(a2)** a file belongs to a different visibility layer than the target carries (a core file in the shown-work
  export, or a ring in the product export);
- **(b)** a file in a `public` or `process` set belongs to a unit whose License is not Apache-compatible
  (proprietary, unlicensed, GPL/AGPL), or to a unit missing from topology;
- **(c)** scrub finds a leak in a file: `sk-`/`ghp_` secret shapes, absolute home paths (macOS user-dir prefix) or tilde-plus-Capitalized-dir paths,
  session ids (`sNN-xxxxxx`), or a project-denylist match. Runs with `--target public`, or alone via
  `--scrub --files <path>...`. Each hit prints `file:line [class] match`; any hit exits 1.
  Optional per-project files (one regex per line, `#` comments): `.orchestrator/scrub-denylist.txt`
  (client names; keel ships none, it is public) and `.orchestrator/scrub-allowlist.txt` (a line matching
  any regex is exempt: author notices, intentional examples). `--denylist <path>` / `--allowlist <path>`
  add regex files that AUGMENT (union with, never replace) those two, so an external tree can be scrubbed
  with a custom list; a missing path errors.

Usage: `python3 scripts/orchestrator-export-check.py --target public|private --files <path>...`
Prove the gate can fail: `python3 scripts/orchestrator-export-check.py --self-test`

## Generator
`scripts/orchestrator-export.py --target public|process|private` reads the Units table, selects units whose
Visibility matches (`public` -> `public-apache`, `process` -> `public-process`, `private` -> `private-ent`), lists
their files (`git ls-files`, so only tracked files), then runs the gate above over that set (a)+(b)+(c).
PASS: prints the manifest (one path per line), exit 0. FAIL: prints `EXPORT BLOCKED ...`, exit 1.
Pair: the generator decides *what* ships; the check is the independent verdict on it (it can also be
run standalone on any file list).
`--out <dir>`: after the gate PASSES, copies each manifest file into `<dir>` (relative paths kept),
writes `<dir>/.soma-core-export` (do-not-edit marker) and `<dir>/LICENSE` (public: copy of repo-root
LICENSE if present; private: proprietary notice). Gate FAIL -> exit 1, `<dir>` is never created.
Prove it: `python3 scripts/orchestrator-export.py --self-test` (temp fixture: public export excludes the
private unit and passes; `--out` tree has only the public unit + marker + LICENSE; a planted leak must
FAIL and a gate-failing `--out` must produce nothing).

Scope + remaining work: `.soma/meetsoma/decisions/2026-11-02-estate-monorepo-export-scope.md`, Phase 2.
