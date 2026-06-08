# Optimization Families

> **When to read:** During `cli-audit-xray` Step 3 when discovering candidate rewrites.

## Algebraic Rewrites

Examples:

```text
x + 0 -> x
x * 1 -> x
x - x -> 0, if no NaN/overflow/side-effect issue
map(g, map(f, xs)) -> map(g . f, xs)
filter(p, filter(q, xs)) -> filter(lambda x: p(x) and q(x), xs)
A * (B * C) -> (A * B) * C, if shape/cost/backend favors it
```

Always check floating-point behavior, integer overflow, exception order, evaluation order, and side effects.

## Loop and Collection Optimizations

Look for:

- loop-invariant code motion;
- map/filter/reduce fusion;
- scan recognition;
- avoiding intermediate collections;
- preallocation;
- replacing repeated linear search with a map/index;
- replacing nested loops with joins, indexes, or matrix/tensor operations;
- vectorization or parallelization when iterations are independent.

## Memory and Allocation Optimizations

Look for:

- temporary buffers that can be removed;
- buffers that can be reused;
- needless clone/copy;
- repeated string normalization;
- repeated serialization/deserialization;
- host/device transfers;
- lazy sequences materialized too early;
- extra memory passes;
- poor cache locality or layout;
- missing tiling/chunking for large data.

## AI / Tensor / LLM Runtime Optimizations

Look for:

- tensor operation fusion;
- materialization between kernels;
- device/host roundtrips;
- static shapes that could specialize branches;
- request batching;
- KV-cache misuse;
- padding waste;
- repeated tokenization or embedding;
- quantization/dequantization boundaries;
- small kernels that should be fused;
- repeated normalization.

## Distributed Systems / DevSecOps Optimizations

Look for:

- caching before canonicalization instead of after;
- DLP or validation too late in the pipeline;
- policy checks repeated across layers without boundary justification;
- network calls inside loops;
- duplicate validation with different trust semantics;
- retry amplification;
- missing backpressure;
- expensive synchronous gates;
- excessive or sensitive log volume;
- unclear trust boundaries.

## Security and Correctness-Aware Optimizations

Never suggest an optimization that weakens:

- authentication;
- authorization;
- audit logging;
- DLP;
- tenant isolation;
- secret handling;
- policy enforcement;
- input validation;
- constant-time or timing-sensitive behavior.

If an optimization touches these, classify it as high risk unless the boundary preservation is explicit and testable.
