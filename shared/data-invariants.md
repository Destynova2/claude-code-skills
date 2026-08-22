# Shared — Data Safety Invariants

> **Cross-skill reference.** Canonical contract for database reasoning shared by
> `cli-audit-data`, `cli-forge-data`, `cli-audit-drift`, `cli-audit-test`,
> `cli-audit-review`, and `cli-forge-lld`.

## Contents

- Two independent scales
- Mandatory reasoning order
- Database decision
- Invariant matrix
- Conservation and state transitions
- Interleaving and idempotency proof
- Proof ladder
- Runtime uncertainty
- Completion gate

---

## Two independent scales

Do not collapse scope and risk into one label:

| Scale | Meaning | Values |
|---|---|---|
| Scope tier | Amount of material to inspect or generate | S / M / L / XL from `tiering.md` |
| Data criticality | Consequence of violating an invariant | L0 / L1 / L2 / L3 |

A one-line ledger update may be scope S and criticality L3. Choose the scope tier from project
size and the criticality level from blast radius; use the deeper proof required by either.

| Criticality | Typical concern | Minimum proof |
|---|---|---|
| L0 | Local read or CRUD, no new invariant | Schema review + PostgreSQL integration test |
| L1 | Uniqueness, lifecycle, deletion, derived field | Invariant matrix + DB constraints + migration test |
| L2 | Money, stock, quota, tenant, queue, concurrency | Interleaving proof + concurrent PostgreSQL test + audit query |
| L3 | Ledger, authorization, compliance, distributed protocol | L2 + repair plan + formal-model decision |

## Mandatory reasoning order

1. **Source of truth** — assign one owner to every business fact and identify reconstructible copies.
2. **Conservation** — state what must not appear, disappear, cross scope, or be counted twice.
3. **State machine** — enumerate legal, conditional, terminal, reversible, and replayed transitions.
4. **Concurrency and failure** — test duplicates, retries, races, timeouts, crashes, and mixed versions.
5. **Homeostasis** — define how drift is detected, bounded, audited, and repaired.
6. **Counterexample** — search for a concrete execution that falsifies the design.

Metaphors may help discovery, but only constraints, atomic operations, explicit protocols, and
reproducible tests count as proof.

## Database decision

Record:

```text
Business objective:
Out of scope:
Entities, owners and cardinalities:
Authoritative sources and derived copies:
Exact meaning of NULL:
Lifecycle and terminal states:
Business time, recorded time and authoritative clock:
Tenant and authorization boundary:
Deletion, retention, anonymization and restoration:
Identifier and uniqueness scope:
Dominant access paths and expected volumes:
Required consistency and convergence bound:
Deployment compatibility:
Assumptions:
```

Reject ambiguous words such as `unique`, `active`, `recent`, `deleted`, or `synchronized` until
their scope and temporal meaning are explicit.

## Invariant matrix

Use one row per positive, observable, falsifiable invariant:

| ID | Testable invariant | Scope | Always/eventual | Primary guarantee | Defense | Detection | Repair | Proof |
|---|---|---|---|---|---|---|---|---|

Consider value domain, unit, precision, nullability, uniqueness, cardinality, references, tenant
scope, conservation, state transitions, temporal overlap, idempotency, derived data, retention,
audit, deletion, and restoration. An eventual invariant must have a maximum convergence bound.

## Conservation and state transitions

For each conserved resource:

```text
Resource and unit:
State before:
Inputs:
Outputs:
State after:
Bounds and rounding:
Atomic operation:
Audit and reconstruction:
```

For each lifecycle, record command, source state, preconditions, target state, writes, external
effects, and replay behavior. A conditional write affecting zero rows is a business result.

## Interleaving and idempotency proof

For every `read -> decide -> write` flow, show at least actors A and B. Test:

- duplicate creation or request;
- two stale updates;
- final-unit reservation;
- lost response after commit;
- crash between durable write and acknowledgement;
- out-of-order event;
- old and new binaries together;
- stale replica read before a critical write;
- deadlock or serialization retry;
- cancellation with an unknown outcome.

Resolve races in this order: declarative constraint and atomic DML; conflict/conditional DML;
targeted row lock; serializable transaction with bounded whole-transaction retry; documented
advisory-lock protocol.

An idempotency protocol defines key scope, request hash, persisted result, in-progress behavior,
payload mismatch, expiration, and cleanup.

## Proof ladder

Map database evidence onto `gate-ladder.md`:

| Rung | Database evidence |
|---|---|
| T0 | Schema/static SQL validation, migration parsing, SQLx prepare |
| T1 | Repository/component tests against PostgreSQL |
| T2 | Empty-database migration and N-1 upgrade on a clean environment |
| T3 | Backup/restore, expand-contract rollout, repair and operator paths |
| T4 | Synchronized concurrency, retries, cancellation, failover and resource pressure |
| M0 | Every database incident becomes a durable regression test and runbook entry |

SQLite and mocks do not prove PostgreSQL concurrency, locking, isolation, migration-runner, or
query-planner behavior.

## Runtime uncertainty

Use exactly:

```text
À PROUVER SUR POSTGRESQL RÉEL
```

when a conclusion depends on untested PostgreSQL scheduling, isolation, locks, deadlocks, timeout,
cancellation, pool behavior, SQLx/PostgreSQL version, migration runner, replicas, or production
topology.

## Completion gate

Apply `done-gate.md`: reconstruct the contract before work, keep changes reversible and isolated
during work, then capture reproducible proof. Apply `determinism.md` to fixtures, clocks, IDs,
retries, and migration data. Classify findings with `triage.md` and emit `result-schema.md` when
running under `cli-cycle`.
