# Shared — The T0-T4 / M0 Gate Ladder

> **Cross-skill reference.** Canonical progressive proof ladder used by `cli-forge-resilience` (biology framing), `cli-forge-oci-rootless` (lithic framing), `cli-forge-pipeline` (CI gates), and `cli-audit-test` (maturity). Reference it as `../../shared/gate-ladder.md`. Each skill keeps its own metaphor vocabulary; this file fixes the **rung semantics** so the ladders mean the same thing across skills.

## The rungs

| Rung | Semantics | Runs against | Catches | Resilience name | OCI name |
|---|---|---|---|---|---|
| **T0** | **Contract / static** — schema, render, lint, policy, config validation; no runtime | source + manifests | malformed contracts, wrong refs, bad config before anything boots | Genome | Bedrock / contract |
| **T1** | **Component** — build the artifact, smoke a single component in isolation | one image / module | broken build, component-internal regressions | Organelle | Alloy / component |
| **T2** | **Fresh deploy** — deploy from scratch onto a clean, prod-like host/env | clean environment | "works on my machine", missing bootstrap, snowflake setup | Tissue | Fresh formation / deploy |
| **T3** | **Operations / day-2** — the real operator paths: restart, rotate, backup, upgrade, least-privilege | running system | operator-path breakage invisible to happy-path | Organism | Field operations / day-2 |
| **T4** | **Stress / failure injection** — latency, resource cliffs, clock shift, dependency loss | system under stress | hangs, false health, cliffs, time bugs | Immune | Stress & fracture |
| **M0** | **Memory** — every fixed incident becomes a durable anti-regression test/runbook entry | the incident history | the same bug shipping twice | Memory cells | Stratigraphic memory |

## Rules

- **Climb in order.** A green T4 over a red T0 is meaningless — a stress test on a system that doesn't even validate its config proves nothing.
- **The golden path lives at T2-T3.** The happy-path end-to-end run (what a demo shows, what a smoke test asserts) is the T2 fresh-deploy + T3 first operation. `cli-forge-demo`'s golden path is exactly this rung made visible.
- **Release gate = lowest red rung.** A pipeline release gate fails at the lowest rung that is red; never let a green scanner (T0) mask a skipped runtime smoke (T2+).
- **M0 is not optional.** A fix that doesn't produce an M0 entry will recur.

## Who uses which rungs

| Skill | Emphasis |
|---|---|
| `cli-forge-resilience` | full ladder T0-T4 + M0; failure-injection battery at T4 |
| `cli-forge-oci-rootless` | T0-T4/M0 as migration proof gates with convergence decision |
| `cli-forge-pipeline` | maps rungs onto CI stages; release gate = lowest red rung |
| `cli-audit-test` | scores how far up the ladder the test plan actually reaches |
| `cli-forge-demo` | shows the T2-T3 golden path as the live demo |
| `cli-audit-data` / `cli-forge-data` | maps T0-T4/M0 to SQLx prepare, PostgreSQL tests, migrations, day-2 repair, concurrency/failure, and incident memory |
