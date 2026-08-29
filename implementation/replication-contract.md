---
domain: implementation
kind: guide
reviewed: 2026-08-28
---

# Replication Contract

Replication should move signed DWN messages and preserve normal admission semantics. It is not a trusted database-copy channel.

## Core contract

A replication engine should provide:

- ordered durable feed reads from a source-local progress position,
- idempotent delivery,
- exact message fetch when a feed item references data not already present,
- dependency repair before checkpoint advancement,
- ordinary DWN admission at the destination,
- durable per-direction progress,
- recovery after lost connections without message loss.

## Checkpoint rule

A source progress token is a high-water cursor for that source, not a causal timestamp.

Advance a durable checkpoint only after all work represented below it has settled: admitted, deterministically rejected, or otherwise classified according to the sync contract. Do not advance past unresolved repairable dependencies and silently forget them.

## Live transport

Live notifications may reduce latency, but durable replication correctness must not depend on every notification being delivered. A robust design can recover by pulling the durable feed from the last committed checkpoint.

## Convergence

Two replicas that eventually receive the same admissible message set must converge regardless of arrival order. The replication layer must therefore avoid introducing alternate conflict or authorization semantics.

## Test cases

- lost and duplicated live notifications,
- reconnect from stale checkpoint,
- repeated pages,
- page boundary duplicates,
- missing data/dependencies,
- destination rejection,
- opposite-direction sync,
- same messages delivered in different orders.

See `dwn/queries-and-sync.md`, `dwn/distributed-semantics.md`, and `implementation/dependency-resolution.md`.
