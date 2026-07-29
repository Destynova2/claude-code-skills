# Shared — Tiering (Mitosis S/M/L/XL)

> **Cross-skill reference.** Canonical S/M/L/XL tier semantics used by `cli-forge-chef` (brigade composition), `cli-audit-tangle` (analysis depth), `cli-forge-hld` (document size), `cli-audit-sync` (doc audit depth), and `cli-forge-pipeline` (workflow fission). Reference it as `../../shared/tiering.md`. Each skill keeps its domain-specific tier table; this file fixes the **scaling rule** so a tier-M project gets a tier-M response everywhere. The cell-biology metaphor (Mitosis) is shared (`../../shared/metaphors.md`): scale the depth of output to the size of the input.

## The 4 tiers

| Tier | Abstract trigger | Abstract behavior |
|---|---|---|
| **S — Single concern** | one feature / one module / one CLI / one team / one DB | minimal output: only the sections, agents, or analysis the input *demands* |
| **M — Multi-concern** | several features / a small service / 1 team across a few modules | standard output: the default set of sections / agents / depth |
| **L — Cross-cutting** | multi-service / multi-team / multi-repo / many modules | full output: cross-cutting sections, larger team, deeper analysis |
| **XL — Regulated or monorepo** | compliance-heavy / monorepo / distributed system / regulated industry | audit-trailed: every decision logged, full traceability, max breadth |

## Dimension axes

A tier is rarely a single number — each skill weights the axes differently.

`cli-audit-data` and `cli-forge-data` also use L0-L3 **data criticality** from
`data-invariants.md`. It is orthogonal to scope tiering: S/M/L/XL controls breadth and output depth;
L0-L3 controls proof depth and safety consequence.

| Axis | Question | Drives... |
|---|---|---|
| **Tasks / scope** | how many independent work items? | brigade size (chef), section count (hld) |
| **Modules / files** | how many call sites? how much code? | analysis depth (tangle), audit depth (sync) |
| **Regulatory burden** | compliance / audit / formal sign-off needed? | XL tipping point (chef, hld) |
| **Blast radius** | who breaks if this is wrong? | review depth, gate strictness |

## Per-skill specialization

Each skill keeps its own tier table (signals → tier), specialized to its domain:

| Skill | Axis used | What the tier drives | Where to look |
|---|---|---|---|
| `cli-forge-chef` | tasks + repo count + regulation | brigade size (1 commis → full XL brigade w/ sous-chef clusters) and execution model (stigmergy vs full vote) | section "0.4 — Choose model and brigade size (Mitosis)" |
| `cli-audit-tangle` | function count | analysis depth (full graph + Fiedler vs module-level sampling) | section "Mitosis — Scale analysis to project size" |
| `cli-forge-hld` | system complexity | document section inclusion matrix (S = 6 sections, XL = full arc42) | section "Step 3 — Size the document (Mitosis)" |
| `cli-audit-sync` | doc file count | audit layers covered (Layer 1 only → all 3 + terminology map) | section "Mitosis — Scale to doc volume" |
| `cli-forge-pipeline` | pipeline size | workflow fission decision (1 mega-pipeline → event-driven mesh) | Patterns table, row 6 "Mitosis" |
| `cli-audit-data` / `cli-forge-data` | files/models/services touched | audit/design breadth; L0-L3 separately selects database proof depth | `shared/data-invariants.md` |

## Why Mitosis (the rule)

A tier-S project does not need a tier-XL artifact. Empty sections, oversized brigades, or full-graph analysis on a tiny module are **noise** — they push the operator past the cognitive budget (Miller's Law) without earning their place. Every section, agent, and dimension the output adds must be **demanded by the input**. The metaphor is the cell: it divides only when both signals (size + nutrients + checkpoint passed) say go. Skills do the same — they divide deeper only when the input demands it.

When the project sits between two tiers, **bias down**. A tier-L project run as M is recoverable (re-run at L); a tier-M project run as XL wastes time and trust.
