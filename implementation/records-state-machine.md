---
domain: implementation
kind: guide
reviewed: 2026-09-03
---

# Records State Machine

A Record is logical state derived from retained Records messages. Implementations should model that explicitly rather than treating the latest database row as the Record.

## Core invariants

- `recordId` is established by the initial write and remains stable.
- immutable descriptor fields cannot be changed by later writes.
- updates replace mutable Record state; they do not create a new logical Record identity.
- conflict resolution is deterministic across replicas.
- deletes are terminal tombstones in the current Enbox convergence model; stale or newer writes must not reopen a deleted Record where that model applies.
- exact duplicate messages are idempotent.

For the current Enbox parity contract, winner classes are ordered `prune delete > plain delete > write`; only candidates within the same class use timestamp/CID ordering (`ENBOX-REC-001`). Keep this classification separate from normative DWN claims.

## State transition shape

```text
no record
  → initial write

active record
  → accepted update
  → accepted delete

deleted record
  → terminal tombstone
```

A correct implementation must distinguish message retention from visible logical state. Historical messages can remain stored even when only one state version is visible.

## Transition contract

For a candidate message:

1. perform the integrity/authentication work needed to identify the signed operation,
2. establish the relevant existing Record state and classify an exact retained CID as duplicate before mutable admission is re-evaluated,
3. for an unseen operation, validate dependencies, immutable relationships, protocol context, and authorization,
4. compare the candidate using the deterministic conflict rule,
5. decide the retained/current-state transition,
6. commit all affected state and feed effects atomically,
7. perform safely resumable data/descendant cleanup after commit.

## Test permutations

At minimum test:

- update A then update B versus B then A,
- write versus delete in both arrival orders,
- plain-delete versus prune in both arrival orders,
- equal-time CID ties within each winner class,
- duplicate initial/write/update/delete delivery,
- data-bearing replay of a retained initial write before and after a newer write/delete,
- duplicate delivery after mutable protocol/role state changes,
- delete followed by stale and newer writes,
- cleanup failure and stale resumable-task replay,
- crash/reopen around the latest-state transition.

See `dwn/records.md` and `dwn/distributed-semantics.md`.
