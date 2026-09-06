---
domain: enbox
kind: implementation
repositories:
  - enboxorg/enbox
  - enboxorg/enbox-rust-core
upstream-baseline: c63bf424ac0997583db825e8a5fddf1507d30c40
reviewed: 2026-09-03
related-issues:
  - enbox-rust-core#169
  - enbox-rust-core#187
  - enbox-rust-core#189
---

# Storage Architecture

## MessageStore is the durable source

Current Rust stores retained DWN messages in `MessageStore`. The SQLite implementation owns the durable replication feed metadata in the same database transaction as message insertion/removal.

For feed-eligible messages, a put transaction updates:

- the message row,
- feed entry/position,
- feed head,
- canonical fingerprint contributions.

Removing a retained message also removes its feed row and fingerprint contribution. Feed positions are sparse and are not reused.

## EventLog is an adapter, not a second history

`DurableEventLog` reads the durable replication feed through `ReplicationFeedReader`. It does not maintain an independent authoritative event history.

This avoids a dual-write invariant between MessageStore and EventLog:

```text
MessageStore/feed = durable truth
EventLog          = replay/live adapter over that truth
```

Wake notifications are best-effort. Consumers recover from the durable feed, so a lost or duplicate wake must not lose or duplicate logical progress.

## Three storage projections

Do not conflate these concerns:

1. **Record/query indexes** in MessageStore support application operations such as Records Query/Read/Count.
2. **Ordered durable feed** supports MessagesQuery, replay, checkpoints and fingerprints.
3. Legacy Rust `StateIndex`/SMT supported the old MessagesSync path and is being retired from current parity claims.

## Atomicity boundary

SQLite gives strong atomicity inside the MessageStore/feed transaction. Records latest-state mutation across the new winner, retained/reindexed messages, displaced messages, query projections, and durable feed effects uses one store-owned transition in current Rust and TypeScript.

The handler decides validity and transition contents; the store commits those contents atomically. Data and descendant cleanup can follow the durable commit and must be safely resumable.

An update to the stored representation or indexes of an existing CID preserves its feed position and fingerprint membership rather than emitting another durable event (`DWN-REC-007`).

## Progress model

Replication feed cursors are high-water scan positions, not counts of returned messages. Filters and deleted rows can create gaps.

A cursor may therefore advance past positions that produced no returned entry. Never derive a durable checkpoint from the last visible message CID.

## Fingerprints

Canonical fingerprints summarize retained message-set membership using XOR of SHA-256(message CID) contributions across defined domains. They verify convergence; they do not identify which message is missing.

Protocol-scoped convergence also includes relevant permissions and encryption-control domains as implemented by current Enbox.

## Durability testing

Real-file SQLite tests matter for:

- reopen persistence,
- crash boundaries around latest-state/feed transitions,
- resumable prune/squash work,
- checkpoint monotonicity,
- concurrent admission.

Tracked under `#169` and the state-transition work in `#189`.
