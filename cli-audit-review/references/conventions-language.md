# Language, Runtime and Ecosystem Conventions

> **When to read:** For Go, PowerShell, shell, Python, Kubernetes, containers, Terraform/OpenTofu, or generic code outside pure Ansible/YAML.

---

## Contents

- Go and Cobra/Viper CLIs
- PowerShell
- Shell and Bash
- Python
- Kubernetes, Containers and Runtimes
- Dockerfiles / Containerfiles
- Terraform / OpenTofu
- Documentation as Code

---

## Go and Cobra/Viper CLIs

Review Go code for clarity, explicit contracts, and idiomatic simplification.

Check:

- environment variables have a clear project/component prefix;
- Cobra/Viper flag names state which system or backend they affect when multiple systems exist;
- CLI flags are understandable in scripts without requiring documentation lookup;
- global mutable variables are avoided unless they are deliberate command-level state;
- constructors take explicit dependencies and return initialized structs;
- struct fields of the same type can be grouped when it improves readability;
- request/response types use action-subject naming that will scale when API coverage grows;
- dead interfaces, unused mocks, and unused helpers are removed unless generated or used by reflection;
- prefer a maintained official client/library over archived third-party clients;
- use `fmt.Errorf` instead of `errors.New(fmt.Sprintf(...))`;
- Go error strings should not start with unnecessary capital letters;
- tests can use `require`/`assert` helpers when they reduce boilerplate without hiding behavior;
- command output format should usually be a flag such as `-o/--output`, not an awkward subcommand, when it matches CLI norms.

Severity:

- Block/Critical for leaked tokens, unsafe TLS defaults, unbounded API calls, or broken command behavior.
- Major for unclear flags/env vars that make automation fragile.
- Minor for grouping vars, blank lines, or small idiom improvements.

## PowerShell

Treat PowerShell like .NET-flavored code, not Bash or Python.

Check:

- variables and parameters use PascalCase, not snake_case;
- CmdLets use approved Verb-Noun naming and correct capitalization;
- type accelerators are consistent, for example `[String]`, `[Int]`, `[Boolean]`;
- avoid raw string interpolation from YAML/Jinja into scripts;
- pass inputs through `Param()` and module `parameters` when called from Ansible;
- simplify inverted booleans and duplicated CmdLet calls;
- prefer explicit object pipelines over fragile text parsing;
- scripts are lintable and tested where they affect deployable behavior.

## Shell and Bash

Check:

- shell scripts are linted with `shellcheck`;
- `.sh` files are checked as POSIX sh when intended; `.bash` files are checked as Bash;
- CI lint commands operate over tracked files, for example using `git ls-files` to avoid comments, generated files, or missed scripts;
- variables are quoted unless word splitting is intended;
- `set -euo pipefail` or equivalent defensive handling is used where appropriate;
- commands that manage state have checks before and after;
- `FIXME` is preferred over ad hoc markers when tooling expects it;
- release hooks do not print secrets or depend on interactive state.

## Python

Check:

- constants are uppercase when they are constants;
- scripts pass `black`/formatting and expected lint checks;
- `pathlib` and structured parsing are preferred over brittle string path manipulation when practical;
- dead helper scripts are removed when no longer generated or referenced;
- command-line scripts have clear failure modes and do not silently swallow errors;
- generated `.env` or local config files contain only values required for the project.

## Kubernetes, Containers and Runtimes

Check:

- CPU/memory requests and limits are configurable when workloads can scale or OOM;
- concurrency values are bounded and documented;
- readiness checks wait for real state, not only longer timeouts;
- single-node and HA behavior are separated when addons/storage/networking behave differently;
- runtime assumptions are documented when a specific runtime is required;
- image tags/checksums are pinned where reproducibility matters;
- offline/airgapped image handling is explicit;
- generated manifests do not hardcode credentials, paths, UID/GID, or cluster-specific addresses without a contract.

## Dockerfiles / Containerfiles

Check:

- base images are pinned or intentionally floating with release rationale;
- build dependencies and runtime dependencies are separated;
- mirrors/proxies are configurable for offline or restricted environments;
- secrets are not passed as build args that remain in layers;
- final image contains only necessary files;
- health checks and entrypoints match runtime expectations;
- package manager caches are cleaned when appropriate.

## Terraform / OpenTofu

Check:

- variables have types, descriptions, validation, and sensitivity flags when needed;
- provider versions are pinned or constrained;
- resources use stable names and do not encode transient environment details;
- secrets are marked sensitive and not rendered to outputs/logs;
- modules expose desired state, not imperative toggles;
- destructive changes are visible in plan and documented when intentional;
- CI protects state access and credentials.

## Documentation as Code

For docs that include commands, examples, labels, paths, or configuration:

- examples should be copy/paste-safe;
- paths must match repository structure;
- diagrams are requested when interactions between tools are hard to infer;
- airgap/offline variants deserve their own explanation when behavior differs;
- typos matter when they alter commands, variable names, labels, or links.
