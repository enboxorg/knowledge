---
domain: implementation
kind: guide
reviewed: 2026-08-28
---

# Storage Contracts

Storage is part of DWN correctness. The database shape is implementation-specific; the atomicity and durability guarantees are not incidental.

## Required logical stores

An implementation generally needs durable representations for:

- retained messages,
- Record/query indexes or equivalent projections,
- ordered replication-feed entries/progress,
- data blobs or references to them,
- protocol/permission state derivable from retained messages.

These can share one physical database.

## Atomicity boundary

A logical state transition should not be externally visible unless all durable effects required to reproduce and replicate it are committed together.

For a Records transition this commonly means:

```text
retained message
+ current/query projection updates
+ durable feed publication
= one commit boundary
```

If a crash can leave the query-visible state newer than the replication feed, replicas can miss an accepted transition. If the feed advances without the retained state, readers can observe an unrecoverable event.

## Durable-feed rule

There should be one authoritative persisted history for replication. Adapters, subscriptions, or event APIs should derive from it rather than introducing an independently committed second history.

## Testing

Use real persistent storage for crash/reopen tests. In-memory transaction tests cannot establish fsync/reopen behaviour.

Test failures at each commit boundary, duplicate admission, transaction rollback, reopen after partial attempted transition, and feed/query consistency.

See `dwn/distributed-semantics.md` and `implementation/replication-contract.md`.
