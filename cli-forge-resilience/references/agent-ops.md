# Agent-ready operations

> **When to read:** Workflow Step 6 when the user mentions support levels, N1/N2/N3, L1/L2/L3, agent autonomy, autonomous remediation, MCP tools, regulated operations, or an "ops pack".

## Separation rule

Keep these axes independent:

| Axis | Meaning | Example values |
|---|---|---|
| Support tier | Who owns the work | N0, N1, N2, N3, N4 |
| Severity | Business impact | SEV1, SEV2, SEV3, SEV4, SEV5 |
| Agent autonomy | What an agent may do | A0, A1, A2, A3, A4, A5 |
| Test proof | How deeply the operation is proven | T0, T1, T2, T3, T4, M0 |

Never use a support tier as permission. "N1" means support responsibility; it does not automatically mean an agent can mutate production.

## Support tier model

| Tier | Scope | Typical owner | Runbook expectation |
|---|---|---|---|
| N0 | Self-service, FAQ, portal, known checks | user, bot, docs | clear symptom pages and read-only checks |
| N1 | Frontline triage and deterministic fixes | service desk, junior ops | exact commands, expected outputs, escalation trigger |
| N2 | Deeper diagnosis and bounded remediation | ops, SRE, platform | decision tree, approval points, rollback proof |
| N3 | Engineering/root cause/code/infrastructure changes | senior SRE, product engineering | RCA, patch path, migration/rollback design |
| N4 | External dependency outside direct control | vendor, cloud provider, third party | evidence bundle and escalation contact |

Avoid N5 as a normal tier. Use `BREAKGLASS` or `GOVERNANCE` for legal, regulatory, executive, CISO, data destruction, root-key, or irreversible production decisions.

## Agent autonomy model

| Level | Allowed behavior | Examples |
|---|---|---|
| A0 | Observe only | summarize alert, classify symptom, prepare handoff |
| A1 | Recommend only | propose runbook path, draft commands, no execution |
| A2 | Execute read-only probes | logs, status, metrics, config reads, health checks |
| A3 | Execute bounded low-risk remediation | idempotent restart, cache clear, retry job, safe reconcile |
| A4 | Execute mutating remediation after approval | rollback, failover, resize, restore, migration step |
| A5 | Human-only breakglass | destructive data operation, root credential rotation, legal notification |

Default stance: production starts at A2 maximum unless the operation has an explicit capability contract, tested rollback, audit trail, and environment-specific approval policy.

## Default mapping

| Support tier | Default agent role | Production ceiling | Notes |
|---|---|---|---|
| N0 | A0-A2 | A2 | self-service and read-only evidence collection |
| N1 | A0-A3 | A2 by default, A3 only for approved low-risk runbooks | deterministic known fixes only |
| N2 | A1-A4 | A3 or A4 with approval | diagnostic judgment plus bounded remediation |
| N3 | A0-A4 | A4 with explicit engineering approval | code, infra, and architecture changes go through review |
| N4 | A0-A1 | A1 | agent prepares vendor evidence, does not operate outside boundary |
| BREAKGLASS | A0-A1 | A1 | human commander owns the decision |

## Capability contract

Every agent-executable action needs a contract. Use YAML when generating files, or a Markdown table when embedding inside a runbook.

```yaml
id: restart-api-pod
purpose: Restart one unhealthy API pod after readiness has failed for more than 5 minutes.
owner: platform-sre
support_tier: N1
max_autonomy: A3
environments:
  dev: A3
  staging: A3
  prod: A3-with-policy
severity_ceiling: SEV3
permissions:
  - kubernetes:pods:get
  - kubernetes:pods:list
  - kubernetes:pods:delete
inputs:
  - namespace
  - pod_name
preconditions:
  - exactly one pod is targeted
  - deployment has at least two ready replicas
  - no active SEV1 or SEV2 incident without incident commander approval
command: kubectl delete pod "$pod_name" -n "$namespace"
expected_output: pod deleted
success_signal: replacement pod ready and error rate returns to baseline
failure_signal: replacement pod not ready within 5 minutes
blast_radius: one pod
rollback: no rollback; Kubernetes recreates pod. Escalate if replacement fails.
evidence:
  - previous pod logs
  - deployment replica status before and after
audit_events:
  - command
  - actor
  - target
  - precondition results
  - before/after status
escalation:
  trigger: replacement pod fails readiness
  target: N2 platform on-call
  bundle: logs, describe pod, events, deployment status
```

## Human-only boundaries

These actions are A5 unless the user explicitly provides a stricter local policy:

- delete or rewrite production data
- restore production database from backup
- modify root/admin credentials or root trust anchors
- broaden IAM, firewall, network perimeter, or tenant access
- disable monitoring, audit logs, DLP, EDR, or security controls
- rotate signing keys, CA keys, or encryption roots
- contact regulators, customers, law enforcement, or legal counsel
- accept vendor guidance that changes production state without local review

## Ops pack output

When generating an agent-ready operations pack, include:

1. `docs/operations/{service}-runbook.md`
2. `docs/operations/{service}-agent-policy.md`
3. `docs/operations/{service}-capability-contracts.yaml`
4. `docs/operations/{service}-escalation-matrix.md`
5. `docs/operations/{service}-evidence-checklist.md`

Each artifact must share the same terms for service names, environments, support tiers, severity levels, and autonomy levels. If one fact appears in several files, nominate one source of truth and link to it.

## Quality gate

Reject the runbook as not agent-ready if any executable action lacks:

- exact command or tool call
- input schema
- expected output
- preconditions
- blast radius
- rollback or containment path
- audit events
- escalation trigger
- maximum autonomy level
