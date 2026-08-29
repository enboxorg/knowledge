---
domain: agents
kind: guide
reviewed: 2026-08-28
---

# Contract Discovery

## Purpose

Use this workflow before modifying code for any non-trivial DWN behavioural change, parity fix, authorization change, replication/state change, protocol semantic change, or architectural refactor whose correctness depends on DWN semantics.

The goal is to determine **what must be true** before deciding **how to implement it**.

This workflow is investigation-only. Do not modify production code while performing contract discovery.

## Inputs

At least one of:

- GitHub issue;
- bug report;
- feature request;
- failing test;
- design question;
- proposed refactor.

## Required evidence collection

### 1. Identify the domain

Classify the task as primarily one or more of:

- Records/state;
- Protocols;
- authorization/permissions;
- queries/visibility;
- sync/replication;
- storage/durability;
- identity/signatures/attestation;
- encryption/key lifecycle;
- topology/transport.

### 2. Retrieve the relevant knowledge slices

Read only the relevant files rather than the entire knowledge repository.

Use this order:

1. `dwn/` for spec-derived semantics;
2. `enbox/` for current Enbox implementation/parity mapping;
3. `implementation/` for engine contracts;
4. `conformance/` for observable behaviour and test cases;
5. `invariants/` for stable IDs and contract classification;
6. `decisions/` when an accepted architectural decision controls the solution;
7. linked issues for unresolved divergence/ownership.

Use `builders/` and `examples/` only when the task concerns application/protocol design or they clarify a concrete semantic scenario.

### 3. Inspect source implementations

When implementation behaviour matters, inspect the actual current code:

- current TypeScript `enboxorg/enbox` reference;
- current `enboxorg/enbox-rust-core` implementation.

Do not infer intended behaviour solely from Rust code or solely from tests.

### 4. Classify the intended contract

State separately:

- DWN draft behaviour;
- current TypeScript Enbox behaviour;
- current Rust behaviour;
- intended target for this task;
- known divergence issue, if any.

Use the following classification discipline:

```text
Spec == TS == Rust
    → aligned

TS == Spec, Rust != TS
    → Rust implementation gap

TS != Spec, Rust == TS
    → Enbox parity / documented upstream divergence

TS != Spec, Rust == Spec
    → Rust follows draft but does not match current Enbox parity
```

Do not silently collapse draft and current Enbox semantics.

### 5. Identify controlling invariants

List the stable invariant IDs that control the behavioural conclusion and preserve each invariant's contract class.

If no existing invariant captures an important behavioural contract, note that as a knowledge-gap follow-up rather than inventing an ID locally.

### 6. Build the behavioural test matrix

Before implementation, enumerate the cases required to prove the behaviour.

For distributed/stateful semantics, consider as applicable:

- normal path;
- exact duplicate delivery;
- different arrival orders;
- stale historical operations;
- delete/write ordering;
- missing dependencies;
- dependency repair/retry;
- role/grant revocation and expiry;
- protocol version changes;
- replay after mutable authorization state changes;
- crash/reopen boundaries;
- multi-replica convergence;
- stale checkpoints;
- encrypted Records without key-control dependencies;
- Signer vs semantic Author.

## Required output

Produce a Behavioural Contract Packet using `agents/templates/contract-packet.md`.

The packet must include:

- task and classification;
- relevant sources;
- controlling invariant IDs and contract classes;
- draft / TypeScript / Rust behaviour comparison;
- explicit required behaviour;
- edge cases;
- test matrix;
- implementation constraints;
- knowledge/documentation impact;
- unresolved questions.

## Stop conditions

Stop and ask for human resolution rather than implementing when:

- intended behaviour remains ambiguous;
- draft and current Enbox differ without a documented parity decision;
- the requested behaviour conflicts with an accepted ADR;
- required historical/authorization semantics cannot be established from current sources;
- implementation would require changing the agreed behavioural contract rather than merely realizing it.

## Exit condition

Contract discovery is complete only when the Behavioural Contract Packet is precise enough that implementation can be judged against it without re-deciding the semantics during coding.
