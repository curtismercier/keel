# Changelog

All notable changes. Newest at top. Keep current to the tagged version (Release gate).

## [Unreleased]
- **Third layer: `public-process` (`--target process`).** A unit may now carry three visibilities — `public-core` (the polished product), `public-process` (the *shown* work: rings/flows) and `private-ent` (the rough workshop shell) — and each public face is a generated export that carries **only its own layer**. The gate treats a cross-layer file as a violation (a core file in the shown-work export, a ring in the product export) in addition to the existing private-leak and license checks; `--self-test` proves all three outcomes on both scripts.
- **The product layer is named for the layer, not for a licence.** `public-apache` (and the `Apache-2.0` rows beside it) claimed a licence the repo's own `LICENSE` does not grant: this template ships MIT. Renamed to `public-core`; the `License` column now has to match `LICENSE`, and the gate's message says *public license* rather than *Apache-compatible*.
- Export gate `--denylist <path>` / `--allowlist <path>`: extra scrub regex files that augment (union with) `.orchestrator/scrub-*.txt`, so external trees can be scrubbed with a custom list (meetsoma/issues #17); `--self-test` proves a CLI-only term is caught and a CLI allowlist exempts a flagged line.
- Export generator `--out <dir>`: after the gate passes, copies the manifest into `<dir>` with a `.soma-core-export` do-not-edit marker and a LICENSE (public: repo-root copy; private: proprietary notice); a failing gate refuses and writes nothing; `--self-test` proves the tree contents and the refusal.
- Export generator `scripts/orchestrator-export.py --target public|private`: selects units by Visibility from topology, enumerates files via `git ls-files`, runs the export gate over them, prints the manifest or the violations; `--self-test` builds a temp fixture and proves public excludes private and a planted leak fails.
- Export gate condition (c): `--scrub` (also run by `--target public`) flags secret shapes, author paths, session ids, optional project denylist/allowlist (`.orchestrator/scrub-*.txt`); `--self-test` plants each class.
- Project scaffolded from `keel` (the baton-ready monorepo template).
