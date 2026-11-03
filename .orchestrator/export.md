# Export boundary — license partition gate

Public repos are generated exports of this monorepo, never hand-edited. Each unit in
`topology.md` carries `Visibility` + `License`. The gate `scripts/orchestrator-export-check.py`
**FAILS the export** if:

- **(a)** a `private-ent` unit's file appears in a `public` export set;
- **(b)** a file in a `public` set belongs to a unit whose License is not Apache-compatible
  (proprietary, unlicensed, GPL/AGPL), or to a unit missing from topology;
- **(c)** scrub finds a leak in a file: `sk-`/`ghp_` secret shapes, absolute home paths (macOS user-dir prefix) or tilde-plus-Capitalized-dir paths,
  session ids (`sNN-xxxxxx`), or a project-denylist match. Runs with `--target public`, or alone via
  `--scrub --files <path>...`. Each hit prints `file:line [class] match`; any hit exits 1.
  Optional per-project files (one regex per line, `#` comments): `.orchestrator/scrub-denylist.txt`
  (client names; keel ships none, it is public) and `.orchestrator/scrub-allowlist.txt` (a line matching
  any regex is exempt: author notices, intentional examples).

Usage: `python3 scripts/orchestrator-export-check.py --target public|private --files <path>...`
Prove the gate can fail: `python3 scripts/orchestrator-export-check.py --self-test`

Scope + remaining work (generator): `.soma/meetsoma/decisions/2026-11-02-estate-monorepo-export-scope.md`, Phase 2.
