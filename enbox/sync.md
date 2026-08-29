---
domain: enbox
kind: implementation
repositories:
  - enboxorg/enbox
  - enboxorg/enbox-rust-core
upstream-baseline: c63bf424ac0997583db825e8a5fddf1507d30c40
reviewed: 2026-08-28
related-issues:
  - enbox-rust-core#187
  - enbox-rust-core#188
  - enbox-rust-core#192
  - enbox-rust-core#211
  - dwn-spec#67
---

# Sync Architecture

## Current model

Current Enbox synchronization is durable-feed based:

```text
baseline / catch-up -> MessagesQuery
live notification   -> MessagesSubscribe
exact fetch          -> MessagesRead
application          -> normal DWN admission
progress             -> durable per-link checkpoints
verification         -> scoped fingerprints
```

Legacy Rust `MessagesSync`/`StateIndex`/SMT is not the current parity target and is being retired after migration.

## MessagesQuery is authoritative

A sync direction starts from its durable checkpoint and reads ordered retained-message feed pages. The returned cursor is the source scan high-water mark, not necessarily the sequence of the last returned entry.

Checkpoint advancement happens only after the relevant page/work below that cursor has settled.

## Replicated admission

The destination does not trust source storage. Pulled or pushed messages pass through ordinary validation/admission and produce structured outcomes such as applied, duplicate/superseded success, incomplete dependency state, invalid input or deferred processing.

Dependency closure can include protocol configurations, initial writes, parent/ancestor records, roles, grants, encryption control, cross-protocol references and required record data.

## Live sync

Current TypeScript treats `MessagesSubscribe` as a wake mechanism rather than a second authoritative delivery channel:

```text
subscription wake
    -> MessagesQuery(last durable checkpoint)
    -> normal reconciliation
```

Lost, duplicated or coalesced wakes are therefore harmless to correctness. This differs from the current draft description and is tracked by `dwn-spec#67`.

## Push and pull

A replication link has independent directional progress:

```text
pull checkpoint
push checkpoint
```

A progress gap on one direction does not invalidate the other. Push transport success is not equivalent to remote admission success; quota and retry classification remain part of sync state.

## Fingerprints

Fingerprints are post-reconciliation evidence that canonical retained sets match. They do not replace feed reconciliation or identify missing CIDs.

## Current Rust status

Rust has the underlying `MessagesQuery`, `MessagesRead`, `MessagesSubscribe`, durable feed/progress/fingerprint primitives substantially in place. The main remaining gap is agent-level reconciliation/lifecycle migration from the old sync engine to the current durable-feed architecture (`#188`, `#192`).

## Coding-agent rule

Do not introduce a second source of replication truth. Durable feed + checkpoint state is authoritative; transient wake/event delivery only accelerates discovery of new durable work.