---
domain: agents
kind: guide
reviewed: 2026-08-28
---

# Review Change

## Purpose

Use this workflow to independently review a completed change against its approved Behavioural Contract Packet, controlling invariants, conformance expectations, and source hierarchy.

Prefer a different agent/session/model from the implementer when practical.

This workflow is review-first. Do not modify production code unless explicitly asked to switch from review into remediation.

## Inputs

Required:

- diff, branch, or PR;
- approved Behavioural Contract Packet;
- controlling invariant IDs;
- target test matrix.

## Review dimensions

### 1. Contract fidelity

Check whether the implementation actually realizes the approved behaviour.

Look for:

- behaviour broader or narrower than approved;
- adjacent semantic changes;
- fallback logic that weakens the contract;
- tests changed to fit implementation rather than contract;
- implicit contract changes hidden in refactors.

### 2. Source classification

Verify the change keeps separate:

- DWN draft semantics;
- current TypeScript Enbox parity behaviour;
- Rust-local implementation details;
- architecture-neutral implementation contracts.

Flag any code/test/docs that present `enbox-parity` behaviour as normative DWN semantics without evidence.

### 3. Invariant coverage

For each controlling invariant:

- verify the implementation preserves it;
- identify the tests that prove it;
- confirm the test is strong enough for the invariant's failure mode;
- preserve the invariant's contract class.

A test name/comment containing an invariant ID is useful traceability but is not itself proof of coverage.

### 4. Distributed/stateful edge cases

As applicable, explicitly review:

- exact duplicate delivery;
- different arrival orders;
- stale historical operations;
- delete/write races;
- missing dependency vs invalid operation;
- dependency repair/retry;
- role/grant revocation and expiry;
- protocol temporal/version resolution;
- replay after mutable authorization state changes;
- crash/reopen atomicity;
- multi-replica convergence;
- checkpoint advancement;
- encrypted Records lacking key-control dependencies;
- Signer vs semantic Author.

### 5. Architecture boundaries

Check relevant ADR/implementation constraints, including where applicable:

- replication goes through normal DWN admission;
- durable progress advances only after work is settled;
- handler determines valid transition while storage owns atomic persistence;
- no reintroduction of legacy `MessagesSync`, `StateIndex`, or SMT reconciliation as current architecture;
- authorization and decryptability remain separate concepts.

### 6. Knowledge drift

Determine whether the change makes any current `knowledge` page, invariant, example, conformance checklist, or implementation mapping stale.

If so, require one of:

- same-change knowledge update;
- linked focused follow-up;
- explicit explanation of why no update is necessary.

## Required output

Use `agents/templates/semantic-review.md`.

Classify findings by severity:

- `BLOCK` — violates contract/invariant or introduces incorrect semantic behaviour;
- `GAP` — required conformance/test case is missing or insufficient;
- `RISK` — plausible semantic/operational concern requiring human judgement;
- `NOTE` — non-blocking clarification or maintainability observation.

For each finding, cite the relevant invariant ID or source where possible.

## Review verdict

End with one of:

- `PASS` — contract and required conformance coverage are satisfied;
- `PASS WITH FOLLOW-UP` — implementation is correct but a non-blocking knowledge/test/tooling follow-up is required;
- `CHANGES REQUIRED` — one or more `BLOCK`/material `GAP` findings remain.

## Exit condition

Review is complete when every controlling invariant has an explicit coverage assessment, the Contract Packet has been checked against the diff, and any knowledge impact is identified.
