# Conflict Resolution — Recency and Convention Precedence

> **When to read:** Whenever two possible conventions disagree, or when older code conflicts with newer review comments.

---

## Precedence Order

Apply conventions in this order:

1. **Explicit user instruction for the current task**, unless unsafe.
2. **Target repository rules**: linters, README, CONTRIBUTING, AGENTS, style guides, CI checks, generated templates.
3. **Safety gates**: security, idempotence, validation, proof, release safety. These override style preferences.
4. **Newest relevant review convention** encoded in this skill.
5. **Newest implementation pattern** in the target repository.
6. **Language/tool official idioms**.
7. **Older historical pattern** only if no newer signal exists.

When still uncertain, write the finding as a question with the concrete risk and the proof needed.

## Recency Rules

- Recent MR review comments beat older commits because they represent review expectations, not just code that happened to exist.
- Recent commits beat old initial commits and generated boilerplate.
- Release commits, generated version bumps, WIP commits, `_to_rebase`, `to-squash`, and mechanical sync commits are weak evidence for conventions.
- A new safety convention can invalidate an older style convention immediately.

## Common Convention Conflicts

### `is defined` vs type tests in Ansible assertions

Use the narrowest correct assertion:

- If a variable is guaranteed by `defaults/main.yml`, a type test such as `var is boolean` is usually enough.
- If a variable may intentionally be undefined, assert as `var is not defined or (...)`.
- If a secret or optional input is consumed only when present, check definedness before length/content checks.
- Do not add redundant `is defined` everywhere if defaults already define the variable and local convention accepts type tests.

### `default(...)` vs assertions

- If a public variable is mandatory or defaulted, prefer asserting it early rather than hiding problems with `default(...)` at consumption time.
- Use `default(omit)` for optional Ansible module parameters so undefined means “do not pass this option”.
- Use `default(value)` at consumption only when the fallback is a deliberate part of the contract and documented.

### Role-level loops vs multiple role invocations

For multiple independent instances of a role-like behavior, prefer looping over `include_role` from the caller when it keeps each role invocation atomic and idempotent. Avoid turning a role into nested loops and deeply nested defaults unless the role contract explicitly models a collection of instances.

### Desired state vs action flags

Prefer desired-state variables. If a change introduces action flags, request justification, documentation, assertion, and proof. An action flag may be acceptable for a deliberate operational override but should not become the normal contract.

### `galaxy.yml` vs `requirements.yml`

Do not assume one replaces the other. Packaging metadata and installation requirements can serve different contexts. If both are required by the workflow, both must remain coherent.

### Molecule idempotence skips

Do not disable idempotence to make CI pass. Prefer idempotent code. If a task is inherently non-idempotent, isolate it and use the smallest justified exemption, with a comment and proof that the rest converges.

### YAML quotes

Avoid unnecessary scalar quotes when they add noise, but keep quotes when YAML ambiguity, special characters, templating, or operator clarity requires them. Do not enforce quote removal over correctness.

### Commit type conflicts

- Use `test:` for test-only changes.
- Use `ci:` for pipeline-only behavior.
- Use `chore:` for maintenance, dependency bumps, template sync, or non-runtime housekeeping.
- Use `fix:` for user-visible bug fixes.
- Use `feat:` for new behavior.
- Use `feat!` or a breaking-change footer when support is removed or compatibility changes.
- Do not use `fix: lint` for pure lint cleanup unless the lint failure blocks a released artifact and the subject explains the actual bug.

### External dependency conflicts

Prefer maintained official clients/libraries when the current dependency is archived or unmaintained. If switching is too broad for the MR, request an issue or explicit follow-up.

### Local style vs production risk

If style and risk compete, handle risk first. Formatting comments should not block a MR that otherwise has a production blocker; they can be grouped as follow-up cleanup.
