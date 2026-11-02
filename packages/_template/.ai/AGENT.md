# packages/<name> — local context for an agent working HERE

**What this is:** <one line — the single responsibility of this library.>
**Public API (the contract):** <the functions/classes in `src/__init__` other units may call.
  Don't break these signatures without a topology update.>
**Depends on:** <sibling packages via their public API, or externals — or "nothing (leaf)".>
  Must NOT import any app.
**Config / secrets:** <env vars it reads — never hardcode.>
**Tests:** `tests/` — write tests that CAN fail (break the input once to prove it). The Proof gate.
**Do / Don't:** <gotchas specific to this unit.>
