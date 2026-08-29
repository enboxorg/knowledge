---
domain: agents
kind: guide
reviewed: 2026-08-28
---

# Implement Contract

## Purpose

Use this workflow only after a Behavioural Contract Packet has been reviewed and approved.

The implementation task is to realize the agreed behaviour without silently redefining it.

## Inputs

Required:

- approved Behavioural Contract Packet;
- target repository/branch;
- controlling invariant IDs;
- expected test matrix.

## Rules

### Implement the contract, not the easiest nearby behaviour

Do not broaden, narrow, or reinterpret the approved contract merely because another implementation would be simpler.

Do not use existing Rust behaviour as authority when it conflicts with the approved contract.

### Preserve source classification

Keep the distinction between:

- normative DWN behaviour;
- current Enbox parity behaviour;
- implementation-contract requirements;
- Rust-local implementation details.

An `enbox-parity` invariant must not be described as normative conformance.

### Keep changes scoped

Allowed:

- production changes required by the contract;
- tests required by the contract;
- narrowly necessary supporting refactors;
- comments/docs that clarify the controlling invariant or architecture.

Avoid:

- opportunistic unrelated refactors;
- adjacent semantic changes;
- broad API redesign without explicit approval;
- changing test expectations to fit current implementation behaviour.

### Use invariant-linked semantic tests

For semantic/conformance/parity tests, reference relevant invariant IDs using the repository's agreed convention, for example:

```rust
// Covers: DWN-REC-004
```

Do not annotate every unit test mechanically. Use invariant IDs where the test exists to prove a stable behavioural contract.

### Implement the whole test matrix

Do not stop after the happy path if the approved packet calls for duplicate, ordering, repair, crash/reopen, historical authorization, or convergence cases.

Prefer table-driven/permutation/property-style tests where the invariant is fundamentally about order-independence or replay.

## Discovery during implementation

If implementation reveals evidence that changes the intended semantics:

1. stop modifying behaviour;
2. document the new evidence;
3. return to `agents/contract-discovery.md`;
4. revise and re-approve the Contract Packet before continuing.

Do not silently update the contract inside the implementation.

## Required output

At completion, report:

```text
Implemented contract:
<short summary>

Controlling invariants:
- <ID> (<contract class>)

Files changed:
- ...

Tests added/updated:
- ...

Contract deviations:
- none
```

If there are deviations, stop and resolve them before calling the implementation complete.

Also state whether the change requires:

- knowledge updates;
- a new invariant;
- a divergence issue;
- a follow-up conformance fixture.

## Exit condition

Implementation is complete when:

- the approved behaviour is implemented;
- the required test matrix passes;
- invariant-linked tests exist where applicable;
- no unresolved contract deviation remains;
- any knowledge impact is identified explicitly.
