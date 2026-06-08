# Semantic Optimization Graph

> **When to read:** During `cli-audit-xray` Step 1 when building the semantic map.

The Semantic Optimization Graph (SOG) is a reasoning model, not necessarily a literal file. Build it only as deeply as the scope demands.

## Node Types

| Node | Meaning | Examples |
|---|---|---|
| Operation | A transformation or action | parse, normalize, map, reduce, scan, route, authorize |
| Data | Values moving through the system | request, tensor, token buffer, AST, config, policy result |
| Control flow | Branching, looping, retrying, waiting | if, match, loop, async await, retry, cancellation |
| Resource | Runtime cost carrier | allocation, copy, lock, file, socket, GPU buffer, DB connection |
| Constraint | Fact that limits valid rewrites | order must be stable, tenant isolation, shape equality |
| Invariant | Property expected to always hold | input length = output length, normalized before cache |
| Cost | Runtime or operational burden | O(n^2), extra pass, network hop, kernel launch |
| Risk | What may break | side effects, FP order, exception ordering, auth boundary |
| Candidate | Possible rewrite | fuse maps, cache after canonicalization, preallocate |

## Minimal SOG Card

```yaml
node: op_42
kind: map
source: src/pipeline.rs:118
input: normalized_tokens
output: scored_tokens
properties:
  pure: maybe
  deterministic: likely
  parallelizable: likely
  vectorizable: maybe
constraints:
  - input_len = output_len
  - no_external_state_access_required
cost:
  complexity: O(n)
  allocates_intermediate: true
  memory_passes: 1
risk:
  side_effect_risk: medium
  floating_point_order_risk: low
  behavior_change_risk: medium
optimization_candidates:
  - fuse_with_next_map
  - remove_intermediate_vec
  - parallel_iter
```

## Three Required Views

### Dataflow

Answer:

- Where does data enter?
- How is it transformed?
- Where is it canonicalized?
- Where is it cached?
- Where does it cross trust, process, network, or device boundaries?
- Where is the same value recomputed?

### Control Flow

Answer:

- Which branches change resource usage?
- Which loops contain invariant work?
- Which retries amplify cost?
- Which async waits serialize work that could overlap?
- Which cancellation or exception order is observable?

### Resource Flow

Answer:

- Where are allocations and copies created?
- Where are buffers materialized?
- Where are formats converted?
- Where are locks held?
- Where are network, database, filesystem, or GPU boundaries crossed?
- Where is serialization/deserialization repeated?

## Mapping Rules

- Prefer exact `file:line` evidence over inferred global claims.
- When a node's purity or determinism is unknown, mark it `maybe` and expose the missing invariant.
- Treat security checks, audit logs, metrics, and errors as observable behavior.
- Do not collapse two operations just because names look similar; prove or state the equivalence condition.
