---
domain: dwn
kind: normative
spec: https://dwn-spec.pages.dev/
spec-reviewed: 2026-08-28
---

# Records

## Lifecycle

A Record begins with an initial `RecordsWrite`. Later writes update mutable state while preserving the Record's stable identity and immutable properties. A `RecordsDelete` produces terminal deleted state.

Conceptually:

```text
NONEXISTENT
    |
    v
  LIVE
    |
    v
 DELETED
```

Updates do not mutate the original message. They add a newer valid state message and displace superseded retained state according to lifecycle rules.

## Initial write

The initial write establishes the Record's immutable identity and structural properties, including values such as protocol placement, creation time, schema/recipient relationships, and other fields defined as immutable by the Records model.

The initial write remains important after updates because later writes alone are insufficient to reconstruct all lifecycle invariants.

## Updates

A later `RecordsWrite` represents a complete new Record state, not a JSON patch. Validation must compare it with the initial write and current retained state.

The implementation must reject attempts to change immutable properties.

If an update omits new data bytes while retaining the same `dataCid`/`dataSize`, an implementation may reuse the previously retained data representation rather than require retransmission.

## Deterministic ordering

Conflicting candidate state messages must be ordered deterministically without using arrival order.

Current Enbox additionally uses a delete-wins tombstone lattice so a delete cannot lose merely because a later write was observed first. The draft/current implementation distinction should remain explicit until the spec convergence work is resolved.

The required distributed invariant is:

```text
same admissible messages
    -> same final Record state
```

regardless of delivery permutation.

## Delete semantics

A winning delete creates terminal Record state. A stale or replayed write must not revive a deleted Record.

Among retained tombstones, deterministic ordering still applies. Current Enbox also distinguishes prune/delete behaviour where relevant.

## Retention

DWN Record storage is not an append-only audit history. Superseded state may be removed while retaining the messages required to represent current logical state and validate lifecycle semantics.

Typical retained shapes are conceptually:

```text
initial only
initial + latest write
initial + delete tombstone
```

Event/subscription history and durable replication feed concerns are separate from the minimal retained Record state.

## Squash and resumable cleanup

Protocol rules may allow squash semantics that collapse retained lifecycle state. Destructive cleanup can require resumable tasks so a crash does not leave the Record half-transitioned.

Storage implementations should bias failure toward harmless extra retained data rather than deleting required data before the logical state transition is durable.

## Admission vs storage

The handler decides whether a candidate state transition is valid. The store should make the accepted transition atomic wherever multiple retained rows/feed projections must change together.

This separation is especially important for crash safety:

```text
validate transition
      |
      v
atomic durable commit
      |
      v
best-effort cleanup / notification
```

## Common traps

- Do not use insertion order as conflict order.
- Do not model updates as partial patches.
- Do not allow a stale write to reopen a deleted Record.
- Do not treat all historical writes as permanently retained audit entries.
- Do not advance external replication progress before the accepted state transition is durable.
