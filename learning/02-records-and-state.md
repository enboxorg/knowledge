---
domain: learning
kind: guide
reviewed: 2026-08-28
---

# 02 — Records and Derived State

## Read first

- `dwn/records.md`
- `dwn/distributed-semantics.md`
- `implementation/records-state-machine.md`
- `conformance/records.md`

## Core model

A Record lifecycle is a deterministic state machine over accepted messages, not a sequence defined by network arrival order.

Important distinctions:

- the initial write establishes immutable identity/shape;
- later writes carry full replacement state for mutable fields;
- deletes create terminal tombstone semantics in the current Enbox convergence model;
- retained historical messages and visible current state are related but not identical;
- duplicate delivery must be idempotent.

For a convergent implementation, the same valid message set must produce the same logical state regardless of delivery order.

## State-transition reasoning

When evaluating an incoming RecordsWrite or RecordsDelete, ask:

1. Does the message satisfy integrity/schema constraints?
2. Are required dependencies available?
3. Is it authorized for the relevant operation time/context?
4. Does it refer to the same logical Record and preserve immutable fields?
5. How does it compare to retained competing state under deterministic ordering rules?
6. What retained-state and durable-feed changes must commit atomically?

## Checkpoint

You should be able to explain:

- why wall-clock arrival is not a conflict-resolution rule;
- why a stale write must not resurrect a terminally deleted Record;
- why exact duplicate replay should not mutate state twice;
- why latest-visible-state and retained-message history are different projections.

## Exercise

Start with initial write `W0`. Two valid messages are later created:

- `W12` — an update;
- `D11` — a delete.

Replica A receives `W0, W12, D11`.
Replica B receives `W0, D11, W12`.

Determine the required final logical state for the current Enbox convergence model. Then list the minimum test permutations needed to prove the result does not depend on delivery order or duplicate delivery.

Verify against `invariants/records.json` and `conformance/records.md`.