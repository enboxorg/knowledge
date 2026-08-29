---
domain: dwn
kind: normative
spec: https://dwn-spec.pages.dev/
spec-reviewed: 2026-08-28
---

# Distributed Semantics

## Core model

A DWN is an eventually convergent signed-message system, not a consensus database.

Replicas converge when they possess the same relevant valid message set and evaluate it with the same deterministic rules.

## Deterministic state

Record state must not depend on arrival order. Competing writes/deletes are resolved by protocol-defined deterministic ordering and lifecycle rules rather than by "last packet received."

The important invariant is:

```text
same valid retained message set
    -> same logical Record state
```

## No global transaction order

DWN timestamps are signed operation timestamps, not a causal or globally synchronized clock. Different Records do not gain a total transaction order merely because their messages carry timestamps.

Do not build cross-record invariants that require serializable global ordering unless an application adds its own coordination mechanism.

## Idempotent replay

A message CID gives an operation stable content identity. Reprocessing the same exact message should not create duplicate effects.

Replication and retry paths must distinguish exact duplicates from genuinely new state transitions.

## Dependency repair

A valid operation can be temporarily inadmissible because required state is missing locally. Examples include parent/ancestor Records, governing Protocol Configures, Permission Grants, roles, encryption-control state, or required data.

The correct response is dependency-aware repair and retry, not weakening validation.

## Deletes and terminal state

Deletion is represented by durable tombstone state. Implementations must define deterministic write/delete competition so disconnected replicas cannot permanently disagree based on delivery order.

A stale write must not revive a Record whose winning state is a terminal delete.

## Checkpoints and failure

Replication progress is local to a source/link. A checkpoint records settled work, not "messages observed." Retryable or incomplete work below a checkpoint must be resolved before advancing past it unless the sync policy explicitly records degraded/dead-letter state.

## Crash semantics

Durable implementations should atomically couple logical retained-state transitions with the replication-feed state that represents them. A crash must not leave application-visible state claiming one transition while durable replication metadata claims another.

Long-running maintenance such as prune/squash should be resumable or otherwise crash-safe.

## Common traps

- Do not use arrival order as conflict resolution.
- Do not treat `messageTimestamp` as a Lamport clock or transaction sequence.
- Do not bypass missing dependencies to force progress.
- Do not advance sync checkpoints merely because a page was fetched.
- Do not assume eventual consistency means temporary nondeterminism is acceptable; convergence still requires deterministic rules.
