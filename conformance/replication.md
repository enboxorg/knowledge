---
domain: conformance
kind: guide
reviewed: 2026-09-03
---

# Replication Conformance

Use with `dwn/queries-and-sync.md`, `dwn/distributed-semantics.md`, and `implementation/replication-contract.md`.

## Durable feed

- [ ] Source feed ordering/progress is stable for a persisted source history.
- [ ] Re-reading from an older checkpoint is safe and idempotent.
- [ ] Duplicate pages/items do not create duplicate logical effects.
- [ ] Lost live notifications do not cause permanent message loss.

## Admission

- [ ] Replicated messages pass ordinary DWN admission.
- [ ] Replication does not bypass protocol, permission, integrity, or state checks.
- [ ] Destination duplicate detection is idempotent.
- [ ] Exact retained-CID replay remains duplicate after mutable protocol/role state changes; an unseen historical CID still receives ordinary admission.
- [ ] Permanent rejection is distinguishable from repairable incomplete state.
- [ ] Structured admission error codes map consistently to applied, duplicate, superseded, incomplete, invalid, or deferred outcomes (`ENBOX-ERR-001`).

## Dependency repair

- [ ] Missing initial/parent/protocol/grant/data dependencies can be fetched and retried when authorized.
- [ ] Checkpoints do not silently advance past unresolved repairable work.
- [ ] Repair loops are bounded and cycle-safe.

## Convergence

- [ ] Same admissible message set delivered in different orders converges.
- [ ] Cross-runtime fixtures compare winner CID, retained CID set, and normalized durable-feed membership rather than backend-local numeric positions.
- [ ] Bidirectional replication converges without endless echo.
- [ ] Reconnect from stale progress catches up fully.
- [ ] Crash/reopen preserves committed progress and does not skip accepted feed items.
