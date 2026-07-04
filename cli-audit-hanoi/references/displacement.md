# Displacement Catalog — What the Code Skips, the Stack Pays

Law 4 in practice. Each row: a capability missing at its natural layer,
the compensations it spawns above, and the fix at source. A gap
compensated in two or more layers is a confirmed finding; one clean
compensation at the layer closest to the gap may be an accepted
trade-off — then the finding is consolidation, not elimination.

## The catalog

| Missing in code | Docker compensation | Kubernetes compensation | Ansible compensation | Fix at source |
|---|---|---|---|---|
| Config via env vars / reload on SIGHUP | `sed`/`envsubst` in entrypoint rewriting config files | checksum annotations forcing rollouts, reloader operators | template + restart handler on every key change | 12-factor env config; watch or SIGHUP reload |
| Retry with backoff on dependencies | `wait-for-it.sh` in entrypoint | initContainers, startupProbe stretched to hide it, crashloop-as-ordering | `until`/`retries` loops, `pause` before start | retry with backoff in the client at startup |
| Graceful shutdown on SIGTERM | `trap` gymnastics in entrypoint | `preStop` sleep, inflated `terminationGracePeriodSeconds`, requests dropped anyway | serial restarts with manual drain steps | catch SIGTERM, drain, exit 0 |
| Real health/readiness endpoints | `HEALTHCHECK` running curl + grep on logs | exec probes shelling in, `tcpSocket` guessing readiness | `wait_for` port checks after start | `/healthz` + `/readyz` with true dependency checks |
| Structured logs to stdout | log-file volumes, logrotate baked into image | sidecar shippers, hostPath mounts | logrotate configs + cron tasks | structured logging to stdout/stderr |
| Idempotent DB migrations as an app command | raw SQL piped in entrypoint | migration Job/initContainer with a psql image | hand-rolled SQL tasks | ship `app migrate`, idempotent, versioned |
| Rootless operation (no fixed UID, port > 1024, known writable dirs) | `USER root`, `chmod -R 777` | securityContext fights, `fsGroup` workarounds, privileged pods | `chown` chains before every start | arbitrary-UID support, high ports, configurable data dir |
| Self-contained or pinned runtime | fat base image, layers of runtime libs | heavier pulls, larger CVE surface | per-host package and repo management | static build or vendored runtime, distroless-compatible |
| Idempotent startup/init | run-once guard files in entrypoint | Jobs with manual dedup annotations | `creates=` guards around init commands | make init safe to run twice |
| Versioned released artifact | image built from `git clone` at deploy time | `latest` tags, unreproducible rollbacks | `git clone` + compile on the target host | CI-released, versioned, immutable artifact |

## Reading the catalog

- The fix at source is **one move**. Each compensation is a move
  repeated per tool, per environment, per rebuild — and written in
  shell, the least verifiable material in the stack.
- Duplication detector: grep for the same magic across layers —
  `sleep N`, `wait-for`, `nc -z`, a `sed` of the same config key — in
  entrypoint scripts, initContainers, and playbooks. Two hits on the
  same gap = the tower is paying twice.
- When the source is out of reach (vendor binary, closed source,
  frozen legacy): consolidate into exactly one layer, the lowest one
  you control, and record it as a known disk out of place — an ADR or
  a comment naming the missing capability, so the day the source
  opens, the compensations are findable and deletable.

## What is NOT displacement

Do not flag legitimate platform ownership as a Law 4 violation:

- Probes existing at all: liveness/readiness is the orchestration
  contract even for a perfect app. The smell is a probe that greps
  logs or shells around a missing endpoint, not the probe itself.
- PID 1 signal reaping (`tini`, `--init`): a container-runtime
  concern, not an app gap.
- Scheduling, scaling, restarts on OOM, network policy, TLS
  termination at the edge, secrets distribution: platform work. The
  app should not reimplement these downward — displacement cuts both
  ways, and pulling orchestration into the app is the same finding
  mirrored.
- Defense in depth: a securityContext on a rootless-capable app is
  belt and suspenders, not duplication.

The test: does the upper layer *re-implement application semantics*
(waiting on the app's dependencies, parsing its logs, rewriting its
config format, encoding its startup order)? Then it is displacement.
Does it express a platform contract the app cannot know? Then it is
just the platform doing its job.
