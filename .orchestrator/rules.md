# Global rules — every crew obeys these

1. **apps consume packages, never the reverse.** A package knows nothing about any app.
2. **Packages talk only through public `__init__`.** No reaching into a sibling's internals.
   Changing a package's public API = a topology update + the lead's gate (it's a contract).
3. **A crew edits only its unit.** A cross-unit change touches a contract → stop, update
   `topology.md`, take it to the lead.
4. **Secrets never commit.** Keep them in env / a secrets store.
5. **Process → `workshop/`. Product → the core.** Don't mix.
6. **Verified beats asserted.** Every "done" has a test or `_run/` command that proves it.
   A PR goes green on CI (tests + lint) before the lead's gate even looks.
7. **The adversary holds the close.** The builder's own tests are never the review.
8. **Gathered code is a candidate** (provenance + license), adopted only by a named act — never drift.
