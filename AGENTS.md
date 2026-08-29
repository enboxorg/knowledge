# AGENTS.md

Guidance for coding agents working on Enbox and DWN-related code.

## Before changing DWN behaviour

1. Read the relevant document under `dwn/` for the semantic invariant.
2. Read the relevant document under `enbox/` for current Enbox implementation architecture.
3. Read `implementation/` for engine-level contracts and `conformance/` for expected observable behaviours.
4. Check linked GitHub issues for known parity gaps or intentional divergences.
5. Distinguish the DWN draft from current `enboxorg/enbox` TypeScript behaviour and current `enboxorg/enbox-rust-core` behaviour.
6. For Rust parity work, current TypeScript Enbox is the behavioural target where a documented draft divergence exists.

## Before building on DWNs

1. Read the relevant `dwn/` pages first; they remain the semantic authority.
2. Use `builders/` for design guidance, trade-offs, and application patterns.
3. Use `examples/` to see the builder process applied end-to-end.
4. Treat builder guidance and examples as synthesis, not a substitute for protocol semantics.
5. Start protocol design from actors, authority, lifecycle, context structure, query needs, privacy/encryption, and offline behaviour before writing protocol JSON.
6. Do not cargo-cult an example into a different authority model. Rebuild the actor/authorization matrix first.
7. Validate illustrative protocol JSON/action syntax against the current draft and runtime before production use.

## Before implementing a DWN engine

1. Use `implementation/` to identify the required processing, storage, authorization, replication, dependency, and error contracts.
2. Use `conformance/` to turn those contracts into behavior-focused tests.
3. Do not copy Enbox internals unless the internal structure is itself a documented decision; conformance is about externally observable semantics.
4. Label fixtures that target an intentional Enbox/spec divergence as implementation-parity rather than normative conformance.
5. Test delivery-order permutations, crash/reopen boundaries, duplicate delivery, dependency repair, and authorization state changes.

## Core rules

- A DWN message is a signed description of an operation; a Record is logical state derived from retained messages.
- Cryptographic signer identity and semantic author identity are distinct when delegation is involved.
- Replication does not bypass normal DWN admission.
- Arrival order must not determine final Record state.
- Deletes are terminal tombstones in the current Enbox convergence model.
- Durable replication uses `MessagesQuery`; `MessagesSubscribe` is a latency/wake layer in current Enbox.
- Do not reintroduce `MessagesSync`, `StateIndex`, or SMT reconciliation as current Enbox architecture.
- Progress tokens are source-local high-water cursors, not causal clocks or dense event counters.
- Authorization and decryption authority are related but separate capabilities.
- Permission Grant revocation is evaluated relative to the operation's authorization timestamp for historical admission; live subscriptions re-evaluate continuing authority.

## Distributed-systems review checklist

For any change to retained state, authorization, or sync, test or reason about:

- duplicate delivery,
- different arrival orders,
- missing dependencies,
- replay after mutable role/protocol state changes,
- crash/reopen boundaries,
- multi-replica convergence,
- stale checkpoints,
- revocation and expiry,
- encrypted records with missing key-control dependencies.

For application/protocol design, also review:

- actor/authorization matrix,
- role and membership lifecycle,
- metadata leakage through tags/indexes,
- schema/protocol evolution,
- offline stale-authority operations,
- key recovery and membership-change effects,
- whether an example's assumptions actually match the target product.

## Knowledge maintenance

When code or upstream semantics change:

- update the relevant knowledge page in the same PR when practical,
- record the reference upstream commit for implementation-derived claims,
- link spec divergences to `enboxorg/dwn-spec` issues,
- avoid presenting implementation behaviour as normative spec behaviour,
- review affected `builders/`, `examples/`, `implementation/`, and `conformance/` pages when their assumptions change.
