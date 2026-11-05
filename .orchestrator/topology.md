# Topology — what depends on what

Fill this as units appear. Arrows point DOWN only: `apps → packages → externals`.
No package imports an app; a package imports a sibling ONLY through its public `__init__`.

```
apps/<app>  ──►  packages/<lib>  ──►  packages/<leaf>
                       └──►  (external service)
```

## Units
| Unit | Kind | Role | Status | Visibility | License |
|------|------|------|--------|------------|---------|
| `packages/_template` | lib | (rename + describe) | template | public-apache | Apache-2.0 |
| `apps/_template` | app | (rename + describe) | template | public-apache | Apache-2.0 |

`Visibility` = which export target may carry the unit; `License` = its license (`Apache-2.0` | `MIT` | `proprietary`). Read by the export gate — see `export.md`.

### The three layers

One private shell, two public faces. Nothing is hand-copied between them: each face is a generated export.

| Layer | Visibility | Target | What belongs there |
|-------|------------|--------|--------------------|
| **Inner — the polished product** | `public-apache` | `--target public` | `packages/`, `apps/`: what a user, judge or client sees and runs |
| **Middle — the shown work** | `public-process` | `--target process` | `rings/` (and `flows/`): the cycles, gates and records that show HOW it was made |
| **Outer — the rough work** | `private-ent` | `--target private` | `workshop/`: ideas, journals, half-plans, anything not yet fit to show |

The middle layer is deliberate: it sits between the rough shell and the polished core so a reviewer can follow the
work without reading the workshop. A unit may appear in exactly ONE public face — the gate treats a cross-layer
file as a violation, not a convenience.

## External services
- (name · URL · what it's for)
