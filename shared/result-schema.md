# Shared — Machine-Readable Result Envelope

> **Cross-skill reference.** Generalizes the pattern `cli-audit-tangle` already uses (`.claude/tangle-partition.json`) into one envelope every skill can emit. Reference it as `../../shared/result-schema.md`. The point: turn prose handoffs ("go run skill X") into a **data pipeline** that `cli-cycle` and `cli-forge-chef` consume without re-parsing markdown.

## When to emit

- **Always optional for a standalone run** (the human-readable report is the primary output).
- **Recommended when run under `cli-cycle`** — the orchestrator aggregates these instead of scraping each report's prose.
- Write to `.claude/<skill-name>.json` at the project root. Fixed path, latest run wins (mirrors `tangle-partition.json`).

## Envelope

```json
{
  "skill": "cli-audit-code",
  "schema_version": 1,
  "generated_at": "2026-05-28T10:00:00Z",
  "scope": "src/core/",
  "score": { "value": 7.2, "scale": 10, "label": "CQI" },
  "findings": [
    {
      "id": "C9-001",
      "tier": 3,
      "dimension": "security",
      "file": "src/auth/token.rs",
      "line": 42,
      "description": "Hardcoded secret in token signer",
      "confidence": "high",
      "effort": "low"
    }
  ],
  "strengths": [
    { "dimension": "naming", "note": "Consistent, intention-revealing names" }
  ],
  "handoffs": [
    { "target": "cli-audit-tangle", "scope": "src/core/", "reason": "3 god modules" }
  ]
}
```

## Field contract

| Field | Meaning |
|---|---|
| `skill` | the emitting skill's name |
| `schema_version` | this schema's version (currently `1`) |
| `scope` | directory/file scanned, or `null` for whole project |
| `score.value/scale/label` | the skill's headline score and its name (CQI, DQI, SQI, WQI, tangle_score…); omit if the skill produces no score |
| `findings[]` | one entry per issue: `tier` (1 minor / 2 major / 3 critical, per `cli-cycle` triage), `dimension`, `file`, `line`, `description`, `confidence` (low/medium/high), `effort` (low/medium/high) |
| `strengths[]` | what's done well (feeds the cycle "Strengths" section) |
| `handoffs[]` | structured version of the skill's Dynamic Handoffs: `target` skill, `scope`, `reason` |

## How `cli-cycle` consumes it

- **Scorecard** ← `score` from each `.claude/<skill>.json`.
- **Triage** ← merged `findings[]`; same `file:line+description` from ≥2 skills → confidence upgraded (triangulation).
- **Adaptive handoffs** ← `handoffs[]`, deduplicated by `(target, scope)` per the orchestration rules.
- **Strengths / Trends** ← `strengths[]` and score deltas vs. the previous run.

A skill that emits this envelope needs **no prose parsing** to participate in a cycle. A skill that doesn't is still fine — the orchestrator falls back to reading its markdown report.

## Specializations

`cli-audit-tangle` keeps its richer `tangle-partition.json` (clusters, boundary_functions, cut points) — that is a **domain-specific superset** consumed by `cli-forge-chef` for worktree assignment. The generic envelope here is the common denominator for aggregation; skills may emit both.
