---
domain: dwn
kind: normative
spec: https://dwn-spec.pages.dev/
spec-reviewed: 2026-08-28
---

# Queries and Sync

## Read and query surfaces

DWN read/query methods expose derived logical state, not a raw append-only log.

Use the interfaces for different purposes:

```text
RecordsRead       exact logical record access
RecordsQuery      filtered logical record population
RecordsCount      count of that population
RecordsSubscribe  live/snapshot view of Records visibility
MessagesRead      exact retained message retrieval
MessagesQuery     ordered retained-message feed
MessagesSubscribe live message-feed notification/subscription
```

## Records versus Messages

Records interfaces answer application-state questions. Messages interfaces answer retained-message and replication questions.

Do not use `RecordsQuery` as a substitute for replication inventory: replicas need the signed messages and dependencies that produced state, not only the final visible Records.

## Durable replication feed

The durable Messages feed is ordered by source-local progress positions. A progress token is a high-water cursor for that source, not a globally meaningful clock and not necessarily the position of the last returned message.

Filtered/deleted positions can create gaps. Consumers must persist the returned cursor rather than infer progress from the final message CID.

## Checkpoint invariant

A replication checkpoint advances only after all required work below it has settled.

```text
read page
   -> apply/fetch dependencies
   -> classify every entry
   -> settle retryable work
   -> commit checkpoint
```

Advancing beyond unresolved work can make a missing message permanently invisible to that sync link.

## Admission

Replicated messages pass through normal DWN validation. The source's decision is not authoritative for the destination.

Useful result classes include successful application, duplicate/already-known state, superseded state, incomplete dependency closure, invalid/permanent rejection, and temporarily deferred processing.

## Dependency closure

A message can depend on other durable state, including:

- governing Protocol Configure messages,
- initial Writes,
- parent/ancestor Records,
- protocol role Records,
- Permission Grants,
- encryption-control Records,
- cross-protocol references,
- required Record data.

The destination identifies what it needs; the sync layer fetches dependencies and retries.

## Fingerprints

A replication fingerprint summarizes retained message membership for a canonical scope. It is useful for verifying convergence after reconciliation.

A fingerprint is evidence of set equality for its defined domain; it does not reveal which messages differ and should not replace the feed/checkpoint algorithm.

## Live sync

The draft and current Enbox implementation differ on live delivery semantics; see `enboxorg/dwn-spec#67`.

The key invariant is that loss, duplication, or reconnection of live notifications must not cause durable messages to be skipped. Durable checkpoint recovery remains the backstop.

## Common traps

- Do not derive a progress token from the last returned message.
- Do not treat source-local positions as global ordering.
- Do not advance a checkpoint past unresolved dependencies.
- Do not trust a remote node's admission result in place of local validation.
- Do not treat a matching cursor alone as proof of convergence when dead-lettered or degraded work exists.
