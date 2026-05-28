# Shared — Determinism & Reproducibility

> **Cross-skill reference.** The same property shows up under different names across skills: `cli-forge-demo` ("same show every night"), `cli-forge-pipeline` (cache keys, tardigrade), `cli-forge-resilience` (hysteresis / clean reruns), `cli-audit-wizard` (idempotent setup), `cli-forge-oci-rootless` (reproducible builds). Reference it as `../../shared/determinism.md`. One definition, one toolkit.

## Definition

A process is **deterministic** when the same inputs produce the same outputs every time. It is **reproducible** when anyone, anywhere, can re-obtain that output from the pinned inputs. Most "works on my machine" failures, flaky CI, and broken demos are a missing pin.

## The pins (what to fix)

| Pin | Why | How |
|---|---|---|
| **Seed** | random ids/data shift the output | fix the PRNG seed; keep demo/test data separate from app seed data |
| **Clock** | timestamps, TTLs, "today" leak non-determinism | pin `SOURCE_DATE_EPOCH`; inject a fake clock; avoid `now()` in fixtures |
| **Environment** | host tools/versions differ | pin tool versions (lockfiles, mise/nix), hermetic containers |
| **Inputs / deps** | floating versions resolve differently | lockfiles, content-addressed deps, pinned image digests (not `:latest`) |
| **Order** | map/set iteration, parallel races | sort before output; stable ordering; avoid order-dependent assertions |
| **Filesystem / locale** | path order, `LC_ALL`, line endings | set `LC_ALL=C`, normalize newlines, sort `find`/glob results |

## Idempotence (the reset property)

A reset/setup is **idempotent** when running it twice lands on the same state: `f(f(x)) = f(x)`. This is what lets a demo run back-to-back, a wizard re-run safely, and a deploy re-apply without snowflakes.

- **Test it:** run twice, diff the resulting state — must be identical.
- **Hysteresis is the enemy:** reruns/rollbacks that leave stale volumes, caches, labels, secrets, or artifacts behind. A clean reset removes them.

## Content-hashing (cache & verification)

Key caches and verify artifacts by a **hash of their real inputs**, not by a timestamp or a branch name. Same inputs → same key → cache hit and reproducible artifact. This is the link between determinism and CI speed.

## Per-skill application

| Skill | Determinism shows up as |
|---|---|
| `cli-forge-demo` | seed + clock pinned → "same show every night"; idempotent reset between takes |
| `cli-forge-pipeline` | content-hashed cache keys; tardigrade = survive/restore identical state |
| `cli-forge-resilience` | hysteresis detection; clean reruns; mutation tests assume a deterministic baseline |
| `cli-audit-wizard` | idempotent setup; re-runnable `doctor`; defaults are deterministic decisions |
| `cli-forge-oci-rootless` | reproducible builds (`SOURCE_DATE_EPOCH`), pinned digests, hermetic stages |
