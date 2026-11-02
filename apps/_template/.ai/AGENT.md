# apps/<name> — local context for an agent working HERE

**What this is:** <one line — the deployable this app is.>
**Consumes:** <which packages it uses, via their public API. It REIMPLEMENTS nothing.>
**Run / serve:** <how to run it locally; the deploy target.>
**Config / secrets:** <env it needs — never hardcode.>
**Rule:** apps consume packages, never the reverse. Logic belongs in a package; the app wires it.
