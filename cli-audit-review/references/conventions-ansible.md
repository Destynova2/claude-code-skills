# Ansible, Molecule and YAML Conventions

> **When to read:** For Ansible roles/collections, Molecule scenarios, YAML, Jinja templates, handlers, tasks, defaults, vars, and role metadata.

---

## Public Contract

Every public variable should have a complete chain:

```text
default/config -> assertion -> consumer -> proof -> docs/default comment
```

Check:

- variable names are prefixed/namespaced consistently with the role or collection;
- variables describe desired state rather than one-off actions;
- optional variables can be intentionally undefined;
- optional module parameters use `default(omit)`;
- complex defaults are split into precise, unitary options instead of a permissive “raw global block”;
- defaults that affect topology, image, port, storage, timeout, retry, package source, runtime, or airgap behavior are explicit;
- comments belong near defaults when they explain operator constraints.

Block or major finding when a public variable is consumed without a default/contract, or defaulted without assertion/proof.

## Assertions

Assertions should run before expensive, destructive, or externally visible operations.

Check:

- types: `is boolean`, `is integer`, `is string`, `is sequence`, `is mapping`;
- non-empty constraints: `| length > 0` where empty is invalid;
- numeric bounds: ports, timeouts, retries, UID/GID, sizes;
- enum values: allowed strings/backends/runtimes/states;
- mutually exclusive options;
- OS/topology-specific constraints in OS/topology-specific assertion files;
- optional variables expressed as `var is not defined or (...)`;
- secrets checked without printing their value.

Avoid late failures where a package, service, filesystem, cluster, or remote API is already modified before configuration is rejected.

## FQCN Everywhere

Use fully qualified collection names for modules, filters, and tests when available:

```yaml
ansible.builtin.assert
ansible.builtin.regex_replace
ansible.builtin.search
ansible.builtin.match
ansible.windows.win_powershell
community.general.some_module
```

Flag short names in tasks, filters, and Jinja expressions when local convention requires FQCN.

## Idempotence

Prefer declarative modules. For `command`, `shell`, raw PowerShell, or custom scripts, require explicit state semantics:

- `changed_when`,
- `failed_when`,
- `creates` / `removes`,
- `state`,
- `when` guard,
- registered output interpreted safely,
- handler notified only on real change.

Block when a command mutates durable state without a convergence model.

Do not hide idempotence failures by disabling checks. If a task is inherently non-idempotent, isolate it and document the minimal exemption.

## Task Organization

Prefer readable task names and vertical separation:

- names start with the operation area: `Assert |`, `Setup |`, `Configure |`, `Install |`, `Template |`, `Wait |`, `Verify |`, `Cleanup |`;
- OS-specific tasks include platform context when the role already does so;
- OS branches live in explicit files such as `assert-RedHat.yml`, `assert-Windows.yml`, `setup-RedHat.yml`, `setup-Windows.yml`, `vars/RedHat.yml`, `vars/Windows.yml` when the role structure uses that pattern;
- large flows are decomposed with `include_tasks`, `include_vars`, or `include_role`;
- duplicated module calls for enable/disable or add/remove states should be collapsed when a single desired-state task is clearer.

## Jinja and Facts

- Avoid `set_fact` for expressions used once; inline the expression where readable.
- Avoid late `default(...)` when assertions should guarantee the value.
- Prefer explicit intermediate variables only when they reduce cognitive load or prevent repeated expensive expressions.
- Keep Jinja in YAML, not injected into embedded scripts when module `parameters` can pass values safely.

## Windows and PowerShell in Ansible

When using `ansible.windows.win_powershell`:

- use `Param()` and module `parameters` instead of raw Jinja interpolation inside code;
- follow PowerShell naming conventions: PascalCase variables and approved Verb-Noun cmdlets;
- use type accelerators consistently, for example `[String]`, `[Int]`, `[Boolean]`;
- simplify boolean inversions and duplicated CmdLet calls;
- prefer one desired-state task over mirrored enable/disable tasks when possible.

## Molecule

Molecule is proof, not decoration.

Check:

- scenario covers the behavior and platform changed by the MR;
- matrix covers introduced OS/image/backend/topology/runtime variants;
- scenario paths in CI, README, lint exclusions, and docs are synchronized after renames;
- convergence and idempotence are not bypassed without a narrow, justified exemption;
- readiness waits check real system state: services, pods, ports, files, APIs, or cluster health;
- cleanup/side-effect tasks are named and scoped;
- image versions/checksums are updated together when relevant.

## YAML Formatting

Treat YAML formatting as low weight unless it affects parsing or operators.

Common comments:

- remove unnecessary scalar quotes when they add noise;
- avoid nested quotes in `when` expressions;
- keep a newline at end of file;
- remove extra tabs/spaces;
- separate logical task blocks with one blank line;
- avoid blank lines that split a single logical task;
- use folded/literal scalars when they improve readability.

## Templates

Templates are a boundary where unvalidated input can become dangerous.

Check:

- user-provided strings cannot inject extra config lines unintentionally;
- secrets are not rendered into world-readable files;
- owner/group/mode are explicit for sensitive files;
- template variables are validated before render;
- generated files notify handlers only when content changes.

## Metadata and Collections

For roles/collections:

- `meta/main.yml`, `meta/runtime.yml`, `galaxy.yml`, `requirements.yml`, and README must agree;
- package metadata must include files needed by build/publish/install;
- collection dependencies must be coherent for both local CI and Galaxy/server installation;
- renaming a role/scenario/project path must propagate to CI, docs, metadata, and examples.
