---
domain: conformance
kind: guide
reviewed: 2026-09-03
---

# Records Conformance

Use with `dwn/records.md` and `dwn/distributed-semantics.md`.

## Identity and integrity

- [ ] Initial write establishes a stable `recordId`.
- [ ] Updates preserve immutable Record identity fields.
- [ ] `dataCid` / data-size commitments are verified.
- [ ] Descriptor and authorization payload commitments are verified before admission.
- [ ] Exact duplicate delivery is idempotent.
- [ ] Same-CID data/index completion preserves durable feed identity and fingerprint membership (`DWN-REC-007`).

## Lifecycle

- [ ] Valid update replaces visible mutable Record state.
- [ ] Invalid mutation of immutable fields is rejected.
- [ ] Delete produces the expected tombstone/terminal state.
- [ ] Under current-Enbox parity, prune beats plain delete, plain delete beats every write, and timestamp/CID orders candidates within a class (`ENBOX-REC-001`).
- [ ] Write-after-delete cannot resurrect the Record under the current-Enbox contract.
- [ ] Permission request, grant, and revocation Records reject updates with the structured immutable-record failure (`ENBOX-REC-002`, `ENBOX-ERR-001`).
- [ ] Historical retained messages do not become independently visible Records.

## Determinism

- [ ] Competing writes converge regardless of arrival order.
- [ ] Write/delete permutations converge regardless of arrival order.
- [ ] Equal-timestamp/tie cases use deterministic comparison.
- [ ] Mixed write/plain-delete/prune candidate sets converge across every arrival permutation.
- [ ] Replica convergence is based on message semantics, not storage insertion order.

## Context and protocol relationships

- [ ] Parent/context relationships are validated.
- [ ] Protocol path cannot be changed illegally across updates.
- [ ] Missing required parent/initial dependencies are classified as repairable when applicable.

## Persistence

- [ ] Crash/reopen after accepted transitions preserves query-visible state.
- [ ] Accepted state and replication-feed publication cannot diverge across a committed transition.
- [ ] Injected cleanup failure leaves the durable winner committed and live data intact; retry is safe and idempotent.
- [ ] A superseded resumable prune task rechecks the winner and performs no destructive cleanup.
