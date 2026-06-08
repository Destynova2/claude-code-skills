# Risk Rules

> **When to read:** During `cli-audit-xray` Step 4 when classifying optimization candidates.

## Candidate Status

| Status | Meaning | Typical next step |
|---|---|---|
| `provable_under_assumptions` | Local rewrite is valid if stated assumptions hold | Add unit/property tests; consider patch |
| `benchmarkable` | Semantics are plausible but performance depends on runtime facts | Run `cli-forge-perf` protocol |
| `needs_invariant` | Rewrite depends on a fact not present in code/contracts | Add/verify contract with `cli-audit-drift` |
| `risky` | Could be valid but hidden behavior may break it | Narrow scope, add tests, review boundary |
| `invalid` | Likely behavior-changing | Do not apply |

## Floating-Point and Numeric Risk

Check:

- NaN and infinity;
- signed zero;
- rounding;
- overflow and underflow;
- precision loss;
- operation order;
- tolerance thresholds;
- backend-specific kernel behavior.

Do not use real-number algebra as proof for floating-point code.

## Side-Effect Risk

Before moving, fusing, removing, caching, or deduplicating code, check for:

- logging and metrics;
- mutation and aliasing;
- global state;
- time and randomness;
- network, file, database, or device I/O;
- exceptions and panic order;
- async cancellation;
- lock acquisition/release order.

## Security Boundary Risk

Treat these as semantics, not overhead:

- authn/authz;
- DLP and policy checks;
- audit events;
- tenant scoping;
- secret redaction;
- validation before use;
- replay protection;
- rate limits and backpressure.

Moving a check earlier may be good. Moving it later is usually dangerous. Removing a duplicate check is only safe if the checks are at the same trust boundary and enforce the same policy over the same canonical input.

## Confidence Guidance

Use `../../shared/triage.md` for report confidence. Within optimization cards:

- `0.85-1.00`: exact local evidence and assumptions directly checkable;
- `0.65-0.84`: strong pattern, but runtime or cross-file facts still needed;
- `0.40-0.64`: plausible hypothesis with missing invariants;
- `<0.40`: exploratory idea; do not rank as a near-term fix.
