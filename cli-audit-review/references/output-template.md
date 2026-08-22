# Output Template — Scored Review

> **When to read:** Use this structure for final review reports unless the user asks for another format.

---

## Contents

- Full Scored Review
- Compact MR Review Variant
- Line Comment Only Variant
- JSON-ish Machine-Readable Summary

---

## Full Scored Review

```markdown
# Scored Review — {target}

**Decision**: {REQUEST_CHANGES | COMMENT | APPROVE_WITH_NOTES | APPROVE}  
**RMI Score**: {X.X}/10 — {verdict}  
**Scope**: {files/directories/diff reviewed}  
**Review context**: {PR/MR intent, diff size, main areas, scope limits}  
**Primary risk**: {one sentence}  
**Date**: {YYYY-MM-DD}

## Gate Status

| Gate | Status | Evidence |
|---|---|---|
| Public contract complete | PASS/WARN/FAIL/N/A | `file:line` or summary |
| Validation before execution | PASS/WARN/FAIL/N/A | `file:line` or summary |
| Idempotence controlled | PASS/WARN/FAIL/N/A | `file:line` or summary |
| Secrets contained | PASS/WARN/FAIL/N/A | `file:line` or summary |
| Deployable behavior proven | PASS/WARN/FAIL/N/A | `file:line` or summary |
| OS/topology/runtime variants covered | PASS/WARN/FAIL/N/A | `file:line` or summary |
| CI/release/package safe | PASS/WARN/FAIL/N/A | `file:line` or summary |
| Docs synchronized | PASS/WARN/FAIL/N/A | `file:line` or summary |

## Scorecard

| # | Category | Weight | Score | Weighted | Notes |
|---|---|---:|---:|---:|---|
| R1 | Public Contract & Naming | 11% | {0.00-1.00} | {x.xx} | ... |
| R2 | Validation & Fail-Fast | 11% | {0.00-1.00} | {x.xx} | ... |
| R3 | Idempotence & State Convergence | 12% | {0.00-1.00} | {x.xx} | ... |
| R4 | Change Propagation & Coherence | 9% | {0.00-1.00} | {x.xx} | ... |
| R5 | Secrets & Security Boundaries | 11% | {0.00-1.00} | {x.xx} | ... |
| R6 | Test, Molecule & CI Proof | 12% | {0.00-1.00} | {x.xx} | ... |
| R7 | Platform, OS & Topology Variants | 8% | {0.00-1.00} | {x.xx} | ... |
| R8 | CI, Release & Packaging Safety | 7% | {0.00-1.00} | {x.xx} | ... |
| R9 | Documentation & Operator Clarity | 6% | {0.00-1.00} | {x.xx} | ... |
| R10 | Language & Ecosystem Idioms | 6% | {0.00-1.00} | {x.xx} | ... |
| R11 | Reviewability & Commit Hygiene | 4% | {0.00-1.00} | {x.xx} | ... |
| R12 | Local Style & Formatting | 3% | {0.00-1.00} | {x.xx} | ... |
| | **RMI** | **100%** | | **{X.X}/10** | {cap applied?} |

## Findings

### Request Changes

#### [Severity] R# — {finding title}
- **File**: `path/to/file:line`
- **Risk**: ...
- **Why it matters**: ...
- **Fix**: ...
- **Proof expected**: ...
- **Confidence**: High/Medium/Low.
- **Disproof**: ...

### Comments / Should Fix

{same structure, only if applicable}

### Nice To Have

{same structure, only if applicable}

## Good Practices Found

- `path:line` — ...

## Smallest Next Actions

1. ...
2. ...
3. ...

## Approval Conditions

- ...
```

## Compact MR Review Variant

Use this when the user wants a concise MR comment rather than a full audit.

```markdown
**Decision**: {REQUEST_CHANGES | COMMENT | APPROVE_WITH_NOTES | APPROVE} — **RMI {X.X}/10**

{One-sentence summary of primary risk.}

### À corriger avant merge

1. `{file:line}` — {risk}. {smallest fix}. Preuve attendue : {proof}.
2. ...

### Commentaires

- `{file:line}` — {minor/major non-blocking comment}.

### Points positifs

- `{file:line}` — {good practice}.
```

## Line Comment Only Variant

When the user asks for GitLab/GitHub review comments only:

```markdown
`path/to/file:42` — [Major/R2] Il manque l'assertion associée à ce nouveau default. Ajoute type + valeurs autorisées avant les tasks de setup, puis couvre le cas dans Molecule.

`path/to/file:88` — [Minor/R12] Saut de ligne manquant en fin de fichier.
```

## JSON-ish Machine-Readable Summary

Use only if the user requests structured output:

```json
{
  "decision": "REQUEST_CHANGES",
  "rmi": 5.4,
  "caps": ["Deployable behavior changed without proof"],
  "findings": [
    {
      "severity": "Critical",
      "category": "R6",
      "file": "tasks/setup.yml",
      "line": 42,
      "risk": "Behavior changed without Molecule proof",
      "fix": "Add/update scenario covering the new path"
    }
  ]
}
```
