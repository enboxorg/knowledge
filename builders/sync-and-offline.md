---
domain: builders
kind: guide
reviewed: 2026-08-28
---

# Sync and Offline Design

## Assume asynchronous replication

Clients and DWNs can be disconnected, partially synchronized, or receive the same signed messages in different orders.

Application correctness must therefore come from DWN admission and deterministic state semantics, not from a single online coordinator observing all writes first.

## Use logical state for UX, durable feeds for reconciliation

Application screens normally consume Records queries/current logical state. Replication engines consume durable message feeds.

Do not build application behavior around feed order unless the domain explicitly models immutable events.

## Subscription is acceleration, not correctness

In current Enbox, `MessagesSubscribe` should be treated as a wake/latency mechanism; durable `MessagesQuery` reconciliation closes gaps.

Design clients so:

- missing a wake is harmless,
- duplicate wakes are harmless,
- reconnect always resumes from durable progress,
- a successful wake does not itself imply durable sync completion.

See `enbox/sync.md` and ADR 0002.

## Offline writes

An offline client may create an operation using stale protocol, role, grant, or parent state. When connectivity returns, normal DWN admission decides whether the operation is still valid.

Do not silently mutate a rejected signed message into a different operation. Surface the conflict and, if appropriate, create a new valid operation with user/application intent preserved.

## Dependency repair

A message can be structurally valid but temporarily inadmissible because required dependencies have not arrived. Sync systems should distinguish incomplete/dependency-missing cases from definitively invalid messages so they can fetch and retry the former.

## Checkpoint discipline

Advance durable progress only after all required work through that point has settled. Otherwise a crash can permanently skip unresolved messages below the recorded checkpoint.

Application code should not invent its own checkpoint semantics on top of replication APIs.

## Optimistic UI

Optimistic local state is fine, but label it internally as pending until the target DWN admits the signed message. If rejected, reconcile explicitly rather than assuming local intent is authoritative.

## Multi-device behavior

Test at least:

```text
device A writes offline

device B changes membership/state

A reconnects
```

and:

```text
DWN A receives update/delete in one order
DWN B receives them in another
both later synchronize
```

The application should converge to the same logical state or clearly expose a domain-level conflict model layered above DWN state.