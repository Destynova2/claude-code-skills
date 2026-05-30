# Shared — Definition-of-Done Gate

> **Cross-skill reference.** Canonical definition-of-done gate for any skill that produces an artifact and needs verification before "shipping". Factored from `cli-forge-perf`'s explicit 3-phase GATE (pre-conditions → during → post-verification) so resilience, pipeline, oci-rootless, demo, chef, and doc share the same scaffold. Reference it as `../../shared/done-gate.md`. Each skill keeps its domain-specific checklist; this file fixes the **phase structure** so a gate failure means the same thing everywhere. Complementary to `../../shared/gate-ladder.md` (T0-T4/M0 rungs across the system) — the done-gate is the per-artifact micro-gate, the gate-ladder is the system-wide proof ladder.

## The 3 phases

| Phase | Question | Examples |
|---|---|---|
| **Pre-conditions** | Are we even allowed to start? Is the baseline measured, the bottleneck localized, the input understood? | baseline measured (perf), contract extracted (resilience), DAG mapped (pipeline), bedrock contract validated (oci), seed pinned (demo), brigade tier chosen (chef) |
| **During** | Are we changing one variable at a time? Are we keeping the work reversible? | single-variable A/B (perf), one mutation injected (pipeline mutation testing), one rung climbed at a time (oci), one commis on one branch (chef) |
| **Post-verification** | Did the change actually do what we said it did? Is the proof reproducible? Did we revert if no gain? | distribution + Δ > noise (perf), score ≥ threshold (resilience), pipeline mutation budget passed (pipeline), proof per rung captured (oci), 8 quality boxes ticked (demo), 8 hard gates passed (chef) |

## Universal principles

- **No claim without evidence.** "It works" / "it's fast" / "it's safe" are not states — they're hypotheses until a check shows them.
- **One change at a time.** Multi-variable changes invalidate the gate: you cannot attribute the outcome to a specific cause.
- **Gate before merge.** The gate is run before the artifact moves to the next stage (merge, deploy, release, demo). Skipping it transfers the cost downstream.
- **Revert if no gain.** A change that doesn't pass the post-verification phase is reverted — readability and stability beat a marginal improvement that doesn't survive measurement.
- **Reproducible proof.** Every box ticked must be re-runnable; one-shot manual checks rot. The reproducibility toolkit is `../../shared/determinism.md`.

## Per-skill usage

| Skill | Domain-specific gate | Where to look |
|---|---|---|
| `cli-forge-perf` | explicit GATE: baseline + bottleneck + ceiling (pre) → single variable (during) → distribution + permutation test + anti-DCE (post) | section "Le GATE — definition-of-done" |
| `cli-forge-resilience` | 15-dimension score ≥ 45/60 + Step 9 action plan + mutation tests pass | Step 6 scoring + Step 8 score + Step 9 |
| `cli-forge-pipeline` | Pipeline Mutation Testing (6 mutations, > 2 silent passes = gate fails) + 15-dimension scorecard | "Pipeline Mutation Testing" section |
| `cli-forge-oci-rootless` | T0-T4/M0 convergence with **proof captured per rung** before declaring "done" | Step 6 — Require proof before declaring convergence |
| `cli-forge-demo` | Step 6 quality gate (8 boxes: same show, idempotent reset, showstopper, golden path, no scene > 76 s, understudy, show-don't-tell, runner-native) | Step 6 — Quality gate |
| `cli-forge-chef` | Phase 3 — Check before service (8+ hard gates: tmuxinator doctor, paths, branches, permissions, setup script, ccheck, contre-chef prompt) | Phase 3 — Check before service |
| `cli-forge-doc` | DCI completeness score + Diataxis coverage before publishing | DCI-REPORT.md section |

## Rule

A gate is the boundary between **"I think it's done"** and **"the artifact proves it's done"**. Skipping a phase doesn't make the artifact faster to ship — it makes the cost surface later, in production, in front of an operator. The done-gate is the cheapest place to find a defect; treat it like a hard wall, not a suggestion. Pass everything, or revert.
