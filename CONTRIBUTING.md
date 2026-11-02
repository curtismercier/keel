# Contributing — the baton → git workflow

Work runs under the baton flow. The git workflow IS the baton.

## One wave = one branch = one PR
1. The lead issues the wave as `workshop/flows/<flow>/wNN-<name>/BATON.md` (the pass). Record receipt.
2. Branch `<seat>/<flow>-wNN-<slug>`. Keep records in `wNN-<name>/_run/` + a `JOURNAL.md`.
3. Open a PR when the return condition is met; the PR body = the BATON return section.
4. **The lead's return-gate = the merge.** Failed gate = review comments, not a merge.

## Working rules (before you build)
_Adopted 2026-11-02 from [github/replica](https://github.com/github/replica) `AGENTS.md` (MIT) — a named adoption, not drift._
- **Agree first, build second.** Settle the user · outcome · access · lifecycle · non-goals BEFORE implementation.
- **Separate accepted requirements from proposed implementation.** Say which is which.
- **One complete user flow at a time.** Finish a flow end-to-end before starting the next.
- **Lead with the outcome, plain language.** Follow existing patterns over inventing new ones.

## PR descriptions
- Short plain-English paragraphs for a first-time reader. Mermaid (before/after) when it clarifies.
- OMIT routine checklists / CI summaries / drafting disclaimers. Name only **real** verification gaps.
- The PR body = the BATON return section (landed · gates moved · NEXT · intake · adversary verdict).

## The bar (crew self-law — amend only UPWARD, never down to fit a miss)
- **Proof, not reports.** A check counts only after it has **failed for the right reason**.
  Visual work ships a screenshot/recording. Cite the readback, never the command.
- **The adversary holds the close.** Every flow closes with a **named adversary** who reads the
  work IN FULL. The builder's own tests are never the review. A medium finding stops the close.
- **Gaps on the face.** Known deficits + unmet gates are named where the claim is, not hidden.
- **Set the target before the build.** Each flow's brief states the numbers it'll be judged on.

## Boundaries (enforced by .orchestrator/rules.md)
- apps consume packages, never the reverse. Packages talk only through their public `__init__`.
- A crew edits only its unit. Cross-unit change touches a contract → topology update + lead gate.
- Secrets never commit. Gathered code is a candidate (provenance + license), adopted by named act.
- Process → `workshop/`. Product → the core.

## Graduation (definition of done — 7 verified gates, baton)
Core (verified by use) · Proof (break-evidence) · Docs (stranger test) · Face (live page) ·
Motion (demo of current build) · Provenance (license record + clean scan) · Release (tag + changelog).

Commits: conventional, atomic (`feat(<unit>): …`). Small diffs, each traceable.
