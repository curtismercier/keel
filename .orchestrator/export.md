# Export boundary — license partition gate

Public repos are generated exports of this monorepo, never hand-edited. Each unit in
`topology.md` carries `Visibility` + `License`. The gate `scripts/orchestrator-export-check.py`
**FAILS the export** if:

- **(a)** a `private-ent` unit's file appears in a `public` export set;
- **(b)** a file in a `public` set belongs to a unit whose License is not Apache-compatible
  (proprietary, unlicensed, GPL/AGPL), or to a unit missing from topology.

Usage: `python3 scripts/orchestrator-export-check.py --target public|private --files <path>...`
Prove the gate can fail: `python3 scripts/orchestrator-export-check.py --self-test`

Scope + remaining conditions (scrub = 0 findings, generator): `.soma/meetsoma/decisions/2026-11-02-estate-monorepo-export-scope.md`, Phase 2.
