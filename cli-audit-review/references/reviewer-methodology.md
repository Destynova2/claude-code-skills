# Reviewer Methodology — Detailed Checks

> **When to read:** For any MR/PR review, especially infrastructure, automation, deployable behavior, or convention compliance.

---

## Review Posture

Review like a production maintainer who cares about what will happen when the change is deployed, rerun, released, and maintained six months later.

The reviewer lens is:

```text
contract -> validation -> execution -> proof -> documentation -> release safety
```

Do not start by nitpicking format. First find whether the change is complete, safe, idempotent, tested, documented, and releasable.

Approve when the change clearly improves the system and remaining issues are minor or explicitly non-blocking. Do not hold an otherwise safe MR/PR for personal preference, polish, or speculative future work.

## Reading Order

1. **Intent:** PR/MR description, linked issue, commit titles, acceptance criteria, reason for the change.
2. **Diff shape:** changed files, generated/vendor/lock files, migrations, tests, docs, CI, release metadata, file moves.
3. **Main design path:** the most behavior-bearing file or largest logical change first.
4. **Contract:** defaults, schema, CLI flags, environment variables, public API, README, metadata.
5. **Validation:** assertions, schema validation, preflight checks, type/bounds/enum checks.
6. **Execution:** tasks, templates, handlers, scripts, service operations, package/cluster/network/storage behavior.
7. **Proof:** Molecule, tests, CI matrix, lint, integration checks, idempotence, release dry-runs.
8. **Operator risk:** secrets, systemd/services, filesystems, storage, network, registries, airgap/offline, HA/single-node, rollback.
9. **Release impact:** semantic-release, package metadata, branch rules, tokens, artifacts, generated docs.
10. **Style:** naming, spacing, EOF, quotes, task separators, formatting.

If tests are the clearest executable specification, read the tests before the implementation. If a large MR/PR has major design risk, send that finding before spending review budget on smaller files that may disappear after redesign.

## Reviewability Checks

Flag reviewability problems when they create real risk:

- missing or vague PR/MR description hides why behavior changed;
- diff mixes refactor, behavior, formatting, and release metadata in one review;
- generated files or lock files obscure the hand-written change;
- file moves/renames are mixed with behavior changes;
- domain-specific changes lack the right maintainer or specialist reviewer;
- only part of the diff was reviewed and the scope is not stated.

Ask for a split when the current diff shape prevents reliable review. Otherwise, continue and state the scope you actually reviewed.

## Core Questions

For every changed behavior, ask:

- Is this a public contract change?
- Does the name express a desired state rather than an action?
- Is every public input defaulted or intentionally undefined?
- Is the input validated before execution?
- Is there a consumer proving the input matters?
- Does a second execution converge?
- Are imperative commands guarded with state/change/failure semantics?
- Are secrets impossible to print, template, store, or leak in CI?
- Are OS/topology/runtime/airgap variants separated at the right layer?
- Does the proof cover the variant actually introduced?
- Did README, Molecule paths, CI matrix, package metadata, and release scripts move with the change?
- Is the commit type/scope compatible with semantic-release and breaking changes?

## Contract Chain Findings

Create a finding when any link is missing:

```text
public option exists but is not asserted
assertion exists but no consumer uses it
consumer exists but no default/config/API contract exposes it
behavior changes but no proof covers it
behavior changes but README/operator docs remain stale
scenario/path is renamed but CI/docs/lint exclusions still point to old names
```

Default severity:

- `Critical` if the missing link can break deploys, leak secrets, corrupt state, or make rollback difficult.
- `Major` if the behavior likely works but cannot be proven or understood by operators.
- `Minor` if the issue is local naming/formatting and no higher risk exists.

## Desired-State Heuristic

When reviewing infrastructure, be suspicious of public options named as actions:

- `*_rename_*`, `*_install_now`, `*_remove_gateway`, `*_run_*`, `*_force_*`

Prefer desired-state contracts:

- connection has target name,
- service has desired state,
- feature is enabled/disabled,
- backend is selected,
- resource limits are declared,
- topology is explicit.

Action-like variables are acceptable only when they model an explicit operational escape hatch and are documented, asserted, and tested.

## Proof Expectations

A behavior-changing MR should include proof close to the behavior:

| Change type | Expected proof |
|---|---|
| New Ansible variable/default | assert + consumer + Molecule or role test + README/default comment. |
| OS-specific behavior | OS-specific assert/task/vars file + matrix entry or scenario. |
| Shell/command durable state | idempotence check or explicit state guard test. |
| Secret handling | negative proof that logs/templates/artifacts do not expose the value. |
| CI/release change | pipeline path proof, branch rule reasoning, token protection, release dry-run when possible. |
| Package/Galaxy metadata | install/build/publish proof and dependency metadata coherence. |
| Kubernetes/container deployment | readiness checks, resource tuning, runtime compatibility, and scenario/matrix coverage. |
| Documentation-only change | links, paths, examples, and generated references still resolve. |

## Comment Granularity

Use different comment sizes depending on severity:

- **Blocker/Critical:** full structured comment with risk, consequence, fix, proof.
- **Major:** concise paragraph plus exact expected proof.
- **Minor style/convention:** one line is enough when the fix is obvious.
- **Uncertain taxonomy/domain naming:** ask a short question and explain the naming consequence.

Label intent for non-blocking comments. Use `Nit:`, `Optional:`, `Question:`, or `Non-blocking:` when the author can proceed without changing the MR/PR. If all remaining comments are non-blocking and the gate is otherwise clean, prefer `APPROVE_WITH_NOTES` over `COMMENT`.

## Pattern: “à généraliser”

When a line-level issue appears multiple times, comment once with the local example and add that it should be generalized to the rest of the file or same pattern. Do not spam identical comments unless the review UI requires one thread per line.

## Pattern: Ready-to-Paste Fix

When the fix is small and syntax-sensitive, provide a ready-to-paste snippet. This is especially useful for:

- Ansible assertions,
- PowerShell `Param()` + `parameters`,
- GitLab CI matrix simplification,
- shellcheck commands,
- Go constructor or struct simplification,
- YAML quote/folded scalar cleanup.

Do not provide a full redesign when the author is better placed to choose the implementation. Point out the problem and the acceptance condition; provide exact code only when it makes the review faster and safer.

## Pattern: Clarifying Question

Use a question instead of an assertion when domain terminology, product taxonomy, or stakeholder naming is unclear. The question must still state the consequence:

```markdown
Est-ce que ce label correspond bien à un périmètre produit plutôt qu'à une équipe ? Si ce n'est pas le cas, le nom risque de devenir ambigu dans les filtres et les dashboards.
```

## Approval Bar

Approve only when:

- the public contract is coherent,
- validation runs before execution,
- idempotence is controlled,
- secrets are contained,
- variants are separated and covered,
- proof matches the changed behavior,
- docs/CI/release metadata are synchronized,
- remaining comments are minor and non-blocking.

A working implementation without proof is not enough for full approval.
