# shared/

Cross-skill reference files — the common denominators that several `cli-*` skills point to instead of each re-deriving them. Skills reference these as `../../shared/<file>.md` (same resolution convention as `../../gotchas.md`).

| File | What it canonicalizes | Consumed by |
|---|---|---|
| `recon.md` | The "read the project first" brief (what/who/problem/headline/differentiator/golden-path) | readme, prez, demo |
| `gate-ladder.md` | The T0-T4/M0 progressive proof-gate semantics | resilience, oci-rootless, pipeline, audit-test, demo, perf (T4 stress) |
| `determinism.md` | Reproducibility & idempotence toolkit (seed, clock, env, content-hash) | demo, pipeline, resilience, wizard, oci-rootless, perf (reproducible baselines) |
| `result-schema.md` | Machine-readable result envelope `.claude/<skill>.json` | cli-cycle (aggregates), all audit/forge skills (emit) |
| `metaphors.md` | Catalog of shared vs. signature metaphors | all biomimetic skills; cli-cycle (consistent vocabulary) |
| `cli-ergonomics.md` | The 4 Laws (ask once / defaults / recap / config-as-code) and surface mapping (CLI / TUI / wizard / CI) | audit-wizard, audit-shell, forge-chef, forge-infra |

These ship to `~/.claude/skills/shared/` alongside `~/.claude/skills/gotchas.md`.
