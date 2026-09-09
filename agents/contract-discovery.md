---
domain: agents
kind: guide
reviewed: 2026-09-09
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

Establish the problem and intended outcome before deriving requirements from the issue or
reference implementation. Treat suggested mechanisms as proposals unless evidence establishes
them as constraints.

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

### 6. Separate the contract from the mechanism

Write the contract as observable behaviour. Do not promote the parity target's implementation
mechanism into a requirement.

When you have just traced an upstream implementation line by line, its mechanism is the most
available thing to write down and the easiest to mistake for the contract. Ask of every sentence
in the required-behaviour section: *would a correct implementation using a different data
structure, library, or API violate this?* If yes, and the mechanism is not itself the contract,
move it to the packet's non-binding reference section.

Implementation choices are non-binding only insofar as changing them preserves the required
observable behaviour and accepted architectural constraints. String handling, iteration order,
parsing, and control flow can affect accepted inputs, normalization, selected results, error
precedence, or durable state. Capture those effects as requirements; leave the means of achieving
them open.

```text
binding      "a reference is resolved by its fragment"
non-binding  "split on the last '#'"
```

### 7. Surface the assumptions worth challenging

Identify the statements the contract rests on that you did not independently verify — inherited
from an issue title, an upstream implementation, a prior packet, or the phrasing of the request.

These are where wrong contracts come from. Mechanism drift produces a working implementation that
looks unlike the packet; a wrong inherited assumption produces an implementation that matches the
packet exactly and is wrong. The second failure survives review against the packet, so it has to
be caught before approval.

Record them in the packet's "Assumptions to challenge" section with their source and what breaks
if each is false. An assumption that reads as settled prose will be approved as settled.

### 8. Build the behavioural test matrix

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
- problem and intent, including the concrete scenario, desired outcome, rationale, and non-goals;
- relevant sources;
- controlling invariant IDs and contract classes;
- draft / TypeScript / Rust behaviour comparison;
- explicit required observable behaviour, separated from non-binding reference mechanism;
- the assumptions a reviewer should challenge;
- edge cases;
- test matrix;
- implementation constraints;
- knowledge/documentation impact;
- unresolved questions.

The test matrix supplies concrete evidence for the contract; it does not replace it. Prefer
externally anchored fixtures where they apply to the intended target, and retain the general
behavioural rule each fixture illustrates. Resolve conflicts between fixtures, prose, and source
evidence before approval.

## Stop conditions

Stop and ask for human resolution rather than implementing when:

- intended behaviour remains ambiguous;
- draft and current Enbox differ without a documented parity decision;
- the requested behaviour conflicts with an accepted ADR;
- required historical/authorization semantics cannot be established from current sources;
- implementation would require changing the agreed behavioural contract rather than merely realizing it.

## Exit condition

Contract discovery is complete only when the Behavioural Contract Packet is precise enough that implementation can be judged against it without re-deciding the semantics during coding.
