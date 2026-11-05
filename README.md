# keel

**The keel every project is laid on.** A GitHub template for a self-contained, baton-ready
monorepo: clean public core + a `workshop/` process shell, organized by domain, with the
guardrails and CI that let agent crews build in parallel without colliding.

> A keel is the backbone laid down first — the foundation the whole vessel is built on.
> (Family: Tidewater · Breakwater · keel.)

## Start a project

Click **Use this template** → name your repo → clone. Then:
1. Rename `packages/_template` and `apps/_template` to real units (copy the template dir).
2. Fill `.orchestrator/topology.md` (what depends on what) and keep `rules.md` as-is.
3. Set the charter in `workshop/flows/_template` and run the first wave.
4. `pip install -e ".[dev]" && pytest` — CI runs the same on every PR.

## The shape

```
<project>/                    PUBLIC CORE (what users/judges see)
├── README · LICENSE · CHANGELOG · pyproject.toml
├── .orchestrator/   topology.md (dep map) · rules.md (crew guardrails)
├── packages/        shared libs = contracts   (each: src · tests · .ai/AGENT.md)
├── apps/            deployable                 (each: src · .ai/AGENT.md)
└── workshop/        PROCESS shell: flows · ideas · journals   (baton two-shell law)
```

**Two shells:** the core is the product; `workshop/` is how it got made. The project stays
atomic — it moves or extracts as one unit.

**Three layers, two public faces.** `packages/` + `apps/` are the polished product (`public-core` → `--target public`);
a `rings/` unit is the *shown* work (`public-process` → `--target process`); `workshop/` is the rough shell
(`private-ent` → `--target private`). Each face is a generated, gate-checked export and a unit may appear in exactly one
of them — the middle layer exists so reviewers can follow the work without reading the workshop.

**Localized memory:** every unit carries `.ai/AGENT.md` — an agent working *there* reads *that*
unit's contract, not the whole repo.

**Runs under [baton](https://github.com/micaforge/baton-flow):** rotating-lead waves, a written
packet per wave, a lead-gated return. The git mapping + the crew rules are in `CONTRIBUTING.md`.
