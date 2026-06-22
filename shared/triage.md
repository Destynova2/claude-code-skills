# Shared — Finding Triage (Phoenix 3-2-1, GRADE, Triangulation)

> **Cross-skill reference.** Canonical finding-classification ladder used by `cli-cycle` (orchestrator), `cli-forge-resilience` (Step 9 action plan), and any audit skill (`cli-audit-code`, `cli-audit-shell`, `cli-audit-doc`, `cli-audit-test`, `cli-audit-wizard`) that produces findings. Reference it as `../../shared/triage.md`. One system, one vocabulary, two independent axes: **tier = urgency**, **confidence = evidence strength**.

## The 3 tiers (Phoenix 3-2-1)

Inspired by emergency-medicine triage (treat the most critical first) and the immune system (prioritize threats by severity). The semantics are universal; each skill specializes the examples to its domain.

| Tier | Semantics | Typical examples | Response time |
|---|---|---|---|
| **Tier 3 — Critical** | Security flaws, broken functionality, data-loss risk, false green in CI, deploy non-idempotency, missing runtime proof | hardcoded secrets, `runAsUser` mismatch, missing `exit 1` on fatal error, secrets in plaintext, auth drift | fix now / next merge |
| **Tier 2 — Major** | Architecture debt, missing tests, obsolete or misleading docs, weak observability, missing CI/CD, parity gaps | unpinned `:latest` tags, monolithic scripts without functions, no negative tests, stale `USER_STORY.md`, incomplete runbook | this sprint |
| **Tier 1 — Minor** | Style, missing diagrams, structural organization, nice-to-have docs, low-risk UX improvements | missing `CHANGELOG`/`LICENSE`, files in wrong directory, no Mermaid diagrams, no `Makefile` | when convenient |

**Display rules** (used by `cli-cycle`): count per tier in the header (`Tier 3 — Critical (N items)`); within each tier, sort by **effort ascending** (quick wins first); never truncate — show every finding.

## GRADE confidence

After classification, each finding gets a confidence score (independent from tier). Adapted from the GRADE evidence framework.

| Start state | Downgrade if... | Upgrade if... |
|---|---|---|
| **HIGH** (multi-method) | Single file only (-1), heuristic-based (-1) | Cross-file confirmed (+1), exact AST match (+1) |
| **MEDIUM** (single source) | No file:line evidence (-1), pattern-only (-1) | Multi-line context (+1) |
| **LOW** (heuristic) | Known false-positive pattern (-2) | Manual review confirmed (+2) |

## Triangulation rule

A finding is **HIGH confidence only if detected by ≥2 independent methods**.

- "Dead function" detected by `cli-audit-tangle` (call graph) AND `cli-audit-code` (DRY check) → HIGH.
- "Hardcoded secret" detected by `cli-audit-code` (C9) only → MEDIUM.
- Same `file:line+description` flagged by N independent skills → confidence floor = N (highest priority in triage).

**Deduplication:** findings about the same `file:line+description` from multiple skills are MERGED into one item with `confidence = number of detecting skills`. The `cli-cycle` orchestrator does this automatically by reading `.claude/<skill>.json` envelopes (see `../../shared/result-schema.md`).

## Per-skill usage

| Skill | What it produces |
|---|---|
| `cli-cycle` | Full Phoenix Triage 3-2-1 across all skills' findings, with triangulation and GRADE downgrade applied during merge. |
| `cli-forge-resilience` | Step 9 action plan in the same 3 tiers, specialized to resilience surfaces (false green, parity gaps, observability). |
| `cli-audit-code` | Findings tagged with tier + dimension + confidence; emitted in the `result-schema.md` envelope as `findings[].tier ∈ {1,2,3}` and `findings[].confidence ∈ {low,medium,high}`. |
| `cli-audit-shell` | Same envelope; S-dimension findings (S1-S12) tagged by tier. |
| `cli-audit-review` | Same envelope; R-dimension MR/PR gate findings tagged by tier, confidence, and expected proof. |
| `cli-audit-doc` | Same envelope; D-dimension findings (Diataxis, freshness) tagged by tier. |
| `cli-audit-test` | Same envelope; D-dimension findings (coverage, NFR, pyramid) tagged by tier. |
| `cli-audit-wizard` | Same envelope; Law violations are Tier 3 by default, lifecycle gaps Tier 2. |

## Rule

**Tier = urgency. Confidence = evidence strength.** A LOW-confidence finding can still be Tier 3 if the **impact** is critical (security, data loss). A HIGH-confidence finding can still be Tier 1 if the impact is cosmetic. Always show both — the operator decides what to fix based on tier × confidence × effort, not on a single composite number.
