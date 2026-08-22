# Shared — Optimization Card

> **Cross-skill reference.** Canonical candidate format for optimizations that are hypotheses until proven. Reference it as `../../shared/optimization-card.md`. Used by `cli-audit-xray` to report candidates, by `cli-forge-perf` to benchmark them, by `cli-audit-drift` to promote missing invariants into contracts, and by `cli-audit-test` to derive equivalence tests.

## Contents

- Purpose
- Card Template
- Status Semantics
- JSON Shape
- Rules

---

## Purpose

An optimization card prevents vague advice. It forces every proposed rewrite to name its evidence, assumptions, validation method, risk, and next owner.

## Card Template

```markdown
## Optimization Card {id} — {short title}

**Location**  
`path/to/file.ext:start-line`

**Observed structure**  
What the code is doing now, stated in plain language.

**Semantic / mathematical view**  
Expression, relation, state machine, tensor operation, dataflow, or constraint. Omit math if it adds no decision value.

**Operational issue**  
The cost or risk: allocation, copy, network call, repeated computation, lock, serialization, device boundary, trust-boundary placement, etc.

**Candidate rewrite**  
The proposed transformation. Include pseudocode only when it clarifies the change.

**Required invariants**  
- Invariant 1
- Invariant 2
- Invariant 3

**Validation method**  
- Unit test / property-based test / integration test
- Benchmark or profile comparison
- Runtime trace comparison
- Contract update or proof obligation

**Expected impact**  
Latency: low/medium/high  
Memory: low/medium/high  
Cloud cost: low/medium/high  
Security/correctness: low/medium/high

**Risk**  
Low/medium/high, with the reason.

**Status**  
provable_under_assumptions / benchmarkable / needs_invariant / risky / invalid

**Confidence**  
0.0 to 1.0, with a short explanation.

**Next owner**  
cli-forge-perf / cli-audit-drift / cli-audit-test / cli-audit-tangle / cli-forge-resilience / direct patch
```

## Status Semantics

| Status | Meaning | Next owner |
|---|---|---|
| `provable_under_assumptions` | Locally safe if listed assumptions hold | direct patch or `cli-audit-test` |
| `benchmarkable` | Semantics are plausible, but gain depends on runtime facts | `cli-forge-perf` |
| `needs_invariant` | Missing contract or behavioral guarantee blocks the rewrite | `cli-audit-drift` |
| `risky` | Security, concurrency, side effects, or architecture boundaries make this unsafe without deeper review | `cli-forge-resilience`, `cli-audit-tangle`, or human review |
| `invalid` | Likely behavior-changing or contradicted by evidence | no patch |

## JSON Shape

When emitted inside `.claude/<skill>.json`, put optimization cards in `findings[]` using `dimension: "optimization"` and include the card details under `metadata` if the consumer supports it:

```json
{
  "id": "XRAY-001",
  "tier": 2,
  "dimension": "optimization",
  "file": "src/pipeline.rs",
  "line": 84,
  "description": "Repeated normalization can be computed once if normalize is pure",
  "confidence": "medium",
  "effort": "low",
  "metadata": {
    "status": "needs_invariant",
    "expected_impact": {"latency": "medium", "memory": "medium"},
    "required_invariants": ["normalize is deterministic", "normalize is side-effect free"],
    "validation": ["property test", "microbenchmark"],
    "next_owner": "cli-audit-drift"
  }
}
```

`metadata` is an extension field. Consumers that only understand `shared/result-schema.md` can ignore it and still aggregate the finding.

## Rules

- Every card needs source evidence when source is available.
- A benchmarkable card is not a proven gain.
- A proof card is valid only under the listed assumptions.
- A missing invariant is a first-class blocker, not a footnote.
- Security, audit, policy, tenant isolation, and validation boundaries are semantics, not overhead.
