# Changelog

All notable changes. Newest at top. Keep current to the tagged version (Release gate).

## [Unreleased]
- Export generator `--out <dir>`: after the gate passes, copies the manifest into `<dir>` with a `.soma-core-export` do-not-edit marker and a LICENSE (public: repo-root copy; private: proprietary notice); a failing gate refuses and writes nothing; `--self-test` proves the tree contents and the refusal.
- Export generator `scripts/orchestrator-export.py --target public|private`: selects units by Visibility from topology, enumerates files via `git ls-files`, runs the export gate over them, prints the manifest or the violations; `--self-test` builds a temp fixture and proves public excludes private and a planted leak fails.
- Export gate condition (c): `--scrub` (also run by `--target public`) flags secret shapes, author paths, session ids, optional project denylist/allowlist (`.orchestrator/scrub-*.txt`); `--self-test` plants each class.
- Project scaffolded from `keel` (the baton-ready monorepo template).
