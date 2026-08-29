# DWN Learning Path

`learning/` is a guided path for experienced engineers who want to become competent at reasoning about, implementing, or building on DWNs.

It is not a second source of protocol semantics. The authoritative conceptual material remains under `dwn/`; implementation-specific facts remain under `enbox/`. This layer provides sequence, exercises, and checkpoints.

## Recommended path

1. [`01-mental-model.md`](01-mental-model.md) — messages, Records, identity, and derived state.
2. [`02-records-and-state.md`](02-records-and-state.md) — lifecycle, deterministic state, deletion, and retention.
3. [`03-protocols-and-authorization.md`](03-protocols-and-authorization.md) — protocol structure, roles, grants, delegation, and authority.
4. [`04-distribution-and-sync.md`](04-distribution-and-sync.md) — replicas, durable feeds, dependency repair, and convergence.
5. [`05-identity-encryption-and-trust.md`](05-identity-encryption-and-trust.md) — DID verification, attestations, encryption, and trust boundaries.
6. [`06-build-a-protocol.md`](06-build-a-protocol.md) — turn a product model into a protocol design.
7. [`exercises.md`](exercises.md) — scenario-based checks that require reasoning, not recall.

## How to use this layer

For each module:

- read the listed canonical pages first;
- answer the checkpoint questions without looking up the answer;
- work through the exercise and state the invariant that controls the outcome;
- use `invariants/` to verify the governing rule;
- use `examples/` only after attempting the design yourself.

The goal is to be able to predict DWN behaviour from first principles, not memorize API calls.