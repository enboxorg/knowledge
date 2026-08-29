# AGENTS.md

Guidance for coding agents working on Enbox and DWN-related code.

## Before changing DWN behaviour

1. Read the relevant document under `dwn/` for the semantic invariant.
2. Read the relevant document under `enbox/` for implementation architecture once that mapping exists.
3. Check linked GitHub issues for known parity gaps or intentional divergences.
4. Distinguish the DWN draft from current `enboxorg/enbox` TypeScript behaviour and current `enboxorg/enbox-rust-core` behaviour.
5. For Rust parity work, current TypeScript Enbox is the behavioural target where a documented draft divergence exists.

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

## Knowledge maintenance

When code or upstream semantics change:

- update the relevant knowledge page in the same PR when practical,
- record the reference upstream commit for implementation-derived claims,
- link spec divergences to `enboxorg/dwn-spec` issues,
- avoid presenting implementation behaviour as normative spec behaviour.
