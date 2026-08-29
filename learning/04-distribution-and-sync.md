---
domain: learning
kind: guide
reviewed: 2026-08-28
---

# 04 — Distribution and Sync

## Read first

- `dwn/queries-and-sync.md`
- `dwn/distributed-semantics.md`
- `dwn/topology.md`
- `implementation/replication-contract.md`
- `conformance/replication.md`

## Core model

DWN replication is eventual convergence over signed messages, not a trusted database-copy channel and not a global consensus log.

A correct sync loop has three conceptual jobs:

1. discover durable source progress/messages;
2. fetch missing messages, data, and dependencies;
3. submit them through ordinary destination admission.

In current Enbox architecture, durable replication is driven by `MessagesQuery`; `MessagesSubscribe` is a wake/latency layer, while `MessagesRead` supports exact retrieval and dependency/data fetches.

## Progress and dependencies

A progress token is a source-local cursor. It is not a causal timestamp and does not prove downstream work is fully settled unless the sync orchestration only advances it after required work has completed.

Replication may need closure over:

- initial writes;
- protocol configurations;
- parent/ancestor Records;
- roles and grants;
- cross-protocol references;
- encryption-control Records;
- external data payloads.

Missing a dependency is different from receiving an invalid message.

## Checkpoint

You should be able to explain:

- why replicas may see different arrival orders yet still converge;
- why a sync engine must not bypass authorization;
- why `MessagesSubscribe` alone is not durable replication;
- why checkpoint advancement must be coupled to settled work;
- why dependency repair needs a distinct retry/error class.

## Exercise

Replica B discovers messages through a source cursor and receives a RecordsWrite whose required parent and governing ProtocolsConfigure have not arrived yet.

Design the correct response:

1. classify the failure;
2. identify the missing dependency closure;
3. describe what may and may not happen to the checkpoint;
4. describe the retry path;
5. explain why accepting the write without dependencies would violate convergence/security.

Verify against `invariants/sync.json` and `implementation/dependency-resolution.md`.