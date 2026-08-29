---
domain: conformance
kind: guide
reviewed: 2026-08-28
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
- [ ] Permanent rejection is distinguishable from repairable incomplete state.

## Dependency repair

- [ ] Missing initial/parent/protocol/grant/data dependencies can be fetched and retried when authorized.
- [ ] Checkpoints do not silently advance past unresolved repairable work.
- [ ] Repair loops are bounded and cycle-safe.

## Convergence

- [ ] Same admissible message set delivered in different orders converges.
- [ ] Bidirectional replication converges without endless echo.
- [ ] Reconnect from stale progress catches up fully.
- [ ] Crash/reopen preserves committed progress and does not skip accepted feed items.
