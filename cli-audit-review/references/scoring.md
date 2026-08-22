# Review Methodology Index (RMI) — Scoring Framework

> **When to read:** Mandatory for every scored review.

---

## Contents

- Formula
- Score Scale
- Category Weights
- RMI Thresholds
- Gate Caps
- Severity Classification
- Category Scoring Hints
- Decision from RMI
- Tech Debt Estimate

---

## Formula

```text
RMI = Σ(wᵢ × sᵢ) / Σ(wᵢ) × 10

Where:
  wᵢ = category weight
  sᵢ = category score from 0.0 to 1.0
```

Use `N/A` only when a category truly does not apply. If a category applies but was not inspected, keep it applicable and score it low, or explicitly mark the whole review as incomplete.

## Score Scale

| Score | Meaning |
|---:|---|
| 0.00 | Absent, unsafe, or contradicted by evidence. |
| 0.25 | Sporadic, implicit, late, or only partially wired. |
| 0.50 | Present but incomplete; significant gaps remain. |
| 0.75 | Solid and mostly coherent; minor gaps remain. |
| 1.00 | Complete, explicit, tested, documented, and easy to review. |

For each category, ask: “Would this pass a strict production MR review without needing external explanation?”

## Category Weights

| # | Category | Weight | Full-score evidence |
|---|---:|---:|---|
| R1 | Public Contract & Naming | 11% | Public variables/config/API/flags/env vars are scoped, desired-state oriented, defaulted or intentionally undefined, documented, and consumed. |
| R2 | Validation & Fail-Fast | 11% | Type, bounds, emptiness, enum, platform, topology, and prerequisite checks happen before risky work. |
| R3 | Idempotence & State Convergence | 12% | Repeated execution converges; imperative steps have state guards and controlled change/failure semantics. |
| R4 | Change Propagation & Coherence | 9% | All affected layers move together: defaults/config, assertions, tasks/templates, handlers, tests, docs, CI, packaging. |
| R5 | Secrets & Security Boundaries | 11% | Sensitive data cannot leak through logs, diffs, templates, artifacts, CI variables, command output, or errors. |
| R6 | Test, Molecule & CI Proof | 12% | The changed deployable behavior is proven by a relevant scenario, matrix, integration test, lint, or idempotence check. |
| R7 | Platform, OS & Topology Variants | 8% | Variants are separated, named, guarded, and tested: Linux/Windows, RedHat-like systems, single-node/HA, airgap, runtime, backend. |
| R8 | CI, Release & Packaging Safety | 7% | Workflow rules, branch behavior, semantic-release, package metadata, tokens, artifacts, and release skips are coherent and safe. |
| R9 | Documentation & Operator Clarity | 6% | Operators can understand defaults, prerequisites, constraints, offline behavior, upgrade impact, failure modes, and rollback. |
| R10 | Language & Ecosystem Idioms | 6% | Code follows the idioms of the ecosystem instead of forcing another language’s style. |
| R11 | Reviewability & Commit Hygiene | 4% | PR/MR description, commits, scopes, diff shape, renames, reviewer scope, and WIP cleanup make the change easy to review and release. |
| R12 | Local Style & Formatting | 3% | Formatting, YAML quotes, EOF newline, spacing, task separators, and lint conventions are clean after higher risks are addressed. |

## RMI Thresholds

| RMI | Verdict | Meaning |
|---:|---|---|
| 9.0-10.0 | Excellent | Methodology is fully respected; approve unless external constraints exist. |
| 8.0-8.9 | Strong | Ship-ready with minor follow-ups. |
| 6.0-7.9 | Needs attention | Plausible but proof, docs, validation, CI/release, or variant handling is incomplete. |
| 4.0-5.9 | Risky | Request changes; production, security, contract, or proof risk is material. |
| 0.0-3.9 | Unsafe | Request changes; major redesign, proof, or containment is required. |

## Gate Caps

Gate caps limit the final RMI even if other dimensions look good. Apply the lowest applicable cap.

| Gate failure | Max RMI | Default decision |
|---|---:|---|
| Secret/token/password/private key can leak or is committed | 3.5 | `REQUEST_CHANGES` |
| Destructive operation can run before validation or rollback safety is known | 4.0 | `REQUEST_CHANGES` |
| Non-idempotent durable state change without guard/change control | 5.0 | `REQUEST_CHANGES` |
| Public contract changed without validation or consumer proof | 5.2 | `REQUEST_CHANGES` |
| Deployable behavior changed without relevant test/Molecule/CI proof | 5.9 | `REQUEST_CHANGES` |
| CI/release token, branch, artifact, or versioning behavior is unsafe | 6.0 | `REQUEST_CHANGES` |
| OS/topology/airgap/runtime variant can regress silently | 6.5 | `REQUEST_CHANGES` or `COMMENT` depending on impact |
| README/docs/Molecule/CI paths stale after rename or scenario split | 7.0 | `COMMENT`, or `REQUEST_CHANGES` if it breaks users/CI |
| Mixed-purpose or oversized diff prevents reliable review | 7.5 | `COMMENT`, or `REQUEST_CHANGES` if design risk cannot be isolated |
| Commit history contains WIP/noise or wrong semantic type but code is safe | 8.0 | `COMMENT` |
| Pure formatting/style issue only | 8.8 | `APPROVE_WITH_NOTES` or `COMMENT` |

Explain each applied cap in the report.

## Severity Classification

| Severity | Definition | Typical action |
|---|---|---|
| Blocker | Can leak secrets, break deploys, corrupt state, bypass validation, or make CI/release unsafe. | Must fix before merge. |
| Critical | Concrete production risk with a credible failure mode, but not necessarily immediate. | Must fix or provide proof before merge. |
| Major | Methodology gap: missing assertion, weak idempotence, missing scenario, stale docs, unsafe variant handling. | Fix recommended before merge. |
| Minor | Local clarity, naming, formatting, small doc, or maintainability issue. | Can be follow-up if no higher risk exists. |
| Info | Positive observation, optional improvement, or clarifying question. | No blocking action. |

## Category Scoring Hints

Start each applicable category at `1.0`, then reduce based on evidence:

- Blocker in category: score `0.0-0.25` and apply gate cap.
- Critical in category: score at most `0.50`.
- Major in category: score at most `0.75`, lower if repeated.
- Minor only: score `0.75-0.90` depending on density.
- No evidence inspected but category applies: score at most `0.50` and state scope limitation.

## Decision from RMI

| Decision | Conditions |
|---|---|
| `REQUEST_CHANGES` | Any blocker, any critical unproven production risk, or RMI `< 6.0`. |
| `COMMENT` | RMI `6.0-7.9` or non-blocking gaps in proof/docs/CI/release. |
| `APPROVE_WITH_NOTES` | RMI `8.0-8.9`, no gate failure, minor follow-ups only. |
| `APPROVE` | RMI `>= 9.0`, no gate failure, proof and docs coherent. |

## Tech Debt Estimate

When useful, estimate review debt:

```text
Debt = blocker_findings × 3h + critical_findings × 2h + major_findings × 1h + minor_findings × 0.25h
```

Use this as a rough prioritization tool, not as a precise delivery estimate.
