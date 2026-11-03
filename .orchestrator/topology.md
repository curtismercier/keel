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

`Visibility` = which export target may carry the unit (`public-apache` | `private-ent`); `License` = its license (`Apache-2.0` | `proprietary`). Read by the export gate — see `export.md`.

## External services
- (name · URL · what it's for)
