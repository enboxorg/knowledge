# AGENTS.md

Guidance for coding agents working on Enbox and DWN-related code.

## Before changing DWN behaviour

1. Read the relevant `dwn/` page for the semantic invariant.
2. Read the relevant `enbox/` page for current Enbox architecture.
3. Read `implementation/` for engine contracts and `conformance/` for observable behaviours.
4. Consult `invariants/` for stable IDs and contract class; cite those IDs when they control a conclusion.
5. Check linked GitHub issues for known parity gaps or intentional divergences.
6. Distinguish DWN draft, current TypeScript Enbox, and current Rust behaviour.
7. For Rust parity work, current TypeScript Enbox is the target where a documented draft divergence exists.

## Before building on DWNs

1. Use `learning/` when you need a guided route or reasoning exercises.
2. Read relevant `dwn/` pages first; they remain semantic authority.
3. Use `builders/` for design guidance and `examples/` for end-to-end worked designs.
4. Start from actors, authority, lifecycle, context structure, query needs, privacy/encryption, and offline behaviour before protocol JSON.
5. Do not cargo-cult an example into a different authority model.
6. Validate illustrative protocol syntax against the current draft/runtime before production use.

## Before implementing a DWN engine

1. Use `implementation/` to identify processing, storage, authorization, replication, dependency, and error contracts.
2. Use `conformance/` to turn those contracts into tests.
3. Use `invariants/` to anchor test intent and code-review conclusions.
4. Do not copy Enbox internals unless the internal structure is itself a documented decision.
5. Label fixtures that target an intentional Enbox/spec divergence as implementation-parity rather than normative conformance.
6. Test delivery-order permutations, crash/reopen boundaries, duplicate delivery, dependency repair, and authorization state changes.

## Core rules

- A DWN message is a signed operation; a Record is logical state derived from retained messages.
- Signer and semantic Author are distinct when delegation is involved.
- Replication does not bypass normal admission.
- Arrival order must not determine final Record state.
- Deletes are terminal tombstones in the current Enbox convergence model.
- Current durable replication uses `MessagesQuery`; `MessagesSubscribe` is a wake layer.
- Do not reintroduce `MessagesSync`, `StateIndex`, or SMT reconciliation as current architecture.
- Progress tokens are source-local cursors, not causal clocks.
- Authorization and decryption capability are separate.
- Historical grant validity is evaluated at the operation time; live disclosure may re-check current authority.

## Review checklist

For retained state, authorization, or sync changes, reason about duplicate delivery, arrival permutations, missing dependencies, mutable role/protocol state, crash/reopen, multi-replica convergence, checkpoints, revocation/expiry, and encrypted Records with missing key-control dependencies.

For application/protocol design, also review the actor matrix, role lifecycle, metadata leakage, protocol evolution, stale offline authority, key recovery/membership changes, and whether an example's assumptions actually match the product.

## Knowledge maintenance

When semantics or implementation behaviour changes, update or explicitly review affected `dwn/`, `enbox/`, `learning/`, `invariants/`, `builders/`, `examples/`, `implementation/`, and `conformance/` material. Never present implementation behaviour as normative merely because it has an invariant ID.