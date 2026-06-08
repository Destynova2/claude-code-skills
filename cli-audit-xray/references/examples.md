# Worked Examples

> **When to read:** When the user asks for examples or when calibrating report style.

## Repeated Normalization

Input:

```python
def handle(prompt):
    if not allowed(prompt):
        return "blocked"

    clean1 = normalize(prompt)
    scan = dlp_scan(normalize(prompt))
    emb = embed(normalize(prompt))

    if scan.has_secret:
        return "blocked"

    return retrieve_and_answer(emb, clean1)
```

Candidate:

````markdown
## Optimization Card 1 — Repeated prompt normalization

**Location**  
`handle(prompt)`

**Observed structure**  
`normalize(prompt)` is executed three times on the same input.

**Semantic / mathematical view**  
```text
clean = normalize(prompt)
scan = dlp_scan(clean)
emb = embed(clean)
answer = retrieve_and_answer(emb, clean)
```

**Operational issue**  
Repeated string normalization may allocate and traverse the prompt multiple times.

**Candidate rewrite**  
Compute `clean` once and reuse it.

**Required invariants**  
- `normalize(prompt)` is deterministic.
- `normalize(prompt)` has no side effects.
- Repeated exceptions/timing are not externally relied upon.

**Validation method**  
- Unit test for identical behavior.
- Property test: `normalize(x) == normalize(x)` for supported inputs.
- Benchmark on short, long, and multilingual prompts.

**Expected impact**  
Latency: medium  
Memory: medium  
Cloud cost: low  
Security/correctness: neutral or positive

**Risk**  
Low if `normalize()` is pure.

**Status**  
provable_under_assumptions

**Confidence**  
0.90
````

## AI Runtime Boundary

Pattern:

```text
linear_attention
  -> residual add
  -> RMSNorm
  -> MoE routing
  -> gather
  -> expert MLP
  -> weighted reduction
  -> residual add
```

Candidate focus:

```text
attention output -> residual add -> RMSNorm -> MoE routing input
```

Why: many small tensor operations can increase kernel launch overhead, memory traffic, and intermediate materialization. Validation requires output tolerance comparison, decode-path microbenchmark, kernel count, and representative shape/profile coverage.

## DLP Boundary

Pattern:

```text
request -> auth -> route -> prompt expansion -> DLP -> model call -> post-filter
```

Candidate: inspect whether a two-phase DLP is safer and cheaper:

```text
scan raw prompt -> safe expansion -> scan expanded prompt if expansion can introduce sensitive content
```

Risk: medium/high because this changes a security boundary. Requires threat model review, secret corpus tests, latency benchmark, and audit-log comparison.
