# Domain Stacks — Canonical Orders, Anti-Patterns, Quick Checks

## Contents

- Container images (Dockerfile / Containerfile)
- Ansible
- Kubernetes
- Rust workspaces and build systems
- CI pipelines
- Text and documents

---

For each domain: the canonical stack reads bottom → top, i.e. first
executed → last executed, most stable → most volatile.

## Container images (Dockerfile / Containerfile)

Canonical stack:

1. `FROM` pinned by digest (the biggest disk: changes rarely, redoes everything)
2. OS packages — single `RUN`, cache cleaned **in the same layer**
3. Language runtime / toolchain
4. Dependency manifests only: `COPY package.json package-lock.json` /
   `Cargo.toml Cargo.lock` / `requirements.txt`
5. Dependency install
6. Source `COPY`
7. Build
8. Final stage: multi-stage `FROM` distroless/slim, artifacts only

Anti-patterns:

- `COPY . .` before dependency install — the signature inversion: every
  source edit re-downloads every dependency.
- `apt-get update` in its own layer — stale index cached forever.
- Cleanup (`rm -rf /var/cache`, `apt-get clean`) in a *later* layer —
  the weight is already committed; size unchanged.
- One `RUN` per shell command — layer count and dead weight.
- Missing `.dockerignore` — `.git/` or `target/` in the context
  invalidates the `COPY` layer on every commit.
- Build toolchain present in the final image — no multi-stage split.
- `FROM x:latest` — the bottom disk changes under the tower.

Quick checks: does editing one source file invalidate the dep-install
layer? `docker history <img>` for per-layer weight; build twice, second
build should be near-instant.

## Ansible

Canonical stack per role/play:

1. Preflight asserts (fail fast on the wrong host, not mid-change)
2. Repositories and GPG keys
3. Packages — one module call with a list, not a loop
4. Users, groups, directories
5. Config templates/files — each with `notify`
6. Services enabled and started
7. Handlers — restart **once**, at flush point

Anti-patterns:

- Inline `service: restarted` after each config file instead of one
  notified handler — N restarts where 1 suffices (restart storm).
- `with_items`/`loop` over a package module — N transactions instead
  of one.
- Config template written before its package is installed — the
  package postinst overwrites it (Law 2), or the parent dir is missing.
- `shell`/`command` where an idempotent module exists — the disk moves
  on every run even when already placed.
- Repeated `gather_facts` across plays that share a host.

Quick checks: count `notify` versus inline restarts; run twice with
`--check --diff` — the second run must report `changed=0` (idempotence:
disks already placed do not move).

## Kubernetes

Canonical apply order:

1. Namespace
2. CRDs — and wait for `Established`
3. RBAC, ServiceAccounts
4. ConfigMaps, Secrets, PVCs
5. Workloads (Deployment/StatefulSet/DaemonSet)
6. Services
7. Ingress, HPA, PDB, NetworkPolicy

Tools that encode the order: kustomize sort, Argo CD sync-waves, Helm
hooks. Prefer declaring the order over relying on retries.

Anti-patterns:

- CR applied in the same wave as its CRD — race on first install.
- Workload mounting a ConfigMap/Secret applied after it — crashloop as
  retry-based ordering; first-install "eventually works" is a Law 2
  violation, not a feature.
- No config-checksum annotation on the pod template — the inverse
  problem: a move that *should* happen (rollout on config change) never
  does.
- Immutable field edits (selector, storageClass) forcing delete/recreate
  of a bottom disk in routine changes.

Quick checks: fresh-namespace install — count crashloops before green
(that number is wasted moves); `kubectl apply --dry-run=server` on the
ordered stream.

## Rust workspaces and build systems

Blast radius is compile time: touching crate X recompiles every
dependent crate. Canonical layering:

1. Foundation crates: stable interfaces, heavy dependencies (serde,
   tokio) isolated behind them
2. Domain crates
3. Volatile app/binary crates on top

Anti-patterns:

- One mega-crate — every edit is a full recompile.
- A daily-edited `utils`/`common` crate at the bottom that every crate
  depends on — the signature inversion. Split the stable types out;
  let the churn float to the top.
- `build.rs` without `cargo:rerun-if-changed` — reruns on every build.
- Feature soup causing repeated dependency unification rebuilds across
  workspace members.

Quick checks: `cargo build --timings` after touching the hottest file
(from git heat); `cargo tree --invert <crate>` to count dependents —
frequency × dependents ranks the inversions.

The same law covers Makefiles and JS monorepos: measure what one edit
rebuilds; anything beyond its true dependents is a wasted move.

## CI pipelines

Fail fast: cheap volatile gates first (fmt, lint, typecheck), expensive
stable stages later and cached (full matrix, e2e). A nightly-rebuilt
base image that every job pulls is a bottom disk that moves daily.
For redesign beyond ordering findings, hand off to `cli-forge-pipeline`.

## Text and documents

The reader's cache is attention. Canonical stack:

1. The point / decision / TL;DR (what every reader needs)
2. Stable reference material
3. Volatile sections (status, changelog, open questions) — grouped at a
   known spot so re-readers re-read only that

Anti-patterns: conclusion on page four; status lines scattered through
stable prose (every update churns the whole document and every anchor);
headings that get renamed on routine edits, breaking inbound links.

Quick check: diff the last five edits of the document — if stable
sections churn, the volatile disks are buried. For outbound messages,
hand off to `cli-forge-plume` (front-loaded ask is the same law).
