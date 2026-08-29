---
domain: conformance
kind: guide
reviewed: 2026-08-28
---

# Records Conformance

Use with `dwn/records.md` and `dwn/distributed-semantics.md`.

## Identity and integrity

- [ ] Initial write establishes a stable `recordId`.
- [ ] Updates preserve immutable Record identity fields.
- [ ] `dataCid` / data-size commitments are verified.
- [ ] Descriptor and authorization payload commitments are verified before admission.
- [ ] Exact duplicate delivery is idempotent.

## Lifecycle

- [ ] Valid update replaces visible mutable Record state.
- [ ] Invalid mutation of immutable fields is rejected.
- [ ] Delete produces the expected tombstone/terminal state.
- [ ] Write-after-delete behaviour matches the targeted contract.
- [ ] Historical retained messages do not become independently visible Records.

## Determinism

- [ ] Competing writes converge regardless of arrival order.
- [ ] Write/delete permutations converge regardless of arrival order.
- [ ] Equal-timestamp/tie cases use deterministic comparison.
- [ ] Replica convergence is based on message semantics, not storage insertion order.

## Context and protocol relationships

- [ ] Parent/context relationships are validated.
- [ ] Protocol path cannot be changed illegally across updates.
- [ ] Missing required parent/initial dependencies are classified as repairable when applicable.

## Persistence

- [ ] Crash/reopen after accepted transitions preserves query-visible state.
- [ ] Accepted state and replication-feed publication cannot diverge across a committed transition.
