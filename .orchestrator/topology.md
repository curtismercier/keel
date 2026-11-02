# Topology — what depends on what

Fill this as units appear. Arrows point DOWN only: `apps → packages → externals`.
No package imports an app; a package imports a sibling ONLY through its public `__init__`.

```
apps/<app>  ──►  packages/<lib>  ──►  packages/<leaf>
                       └──►  (external service)
```

## Units
| Unit | Kind | Role | Status |
|------|------|------|--------|
| `packages/_template` | lib | (rename + describe) | template |
| `apps/_template` | app | (rename + describe) | template |

## External services
- (name · URL · what it's for)
