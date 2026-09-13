# ADR 0007: Structural Parent Ancestry Uses Retained Writes; Only Prune Removes Ancestry

- Status: Accepted (2026-09-13); Enbox parity divergence tracked upstream
- Date: 2026-09-13

## Context

Protocol authorization requires a parent Record to exist for a parent-bearing
write, and resolves it against current state (a latest-base-state filter plus a
tombstone check), matching current Enbox. A `RecordsDelete` is a terminal
tombstone and a soft delete does not cascade to children.

As a result, admission of a parent-bearing child depends on delivery order: a
child delivered before its parent's delete is admitted; the same child delivered
after is rejected permanently. Two replicas holding the same valid message set
can converge to different Record state, conflicting with `DWN-REC-004` read as a
global admission guarantee. Role revocation has the same shape.

`enboxorg/enbox#991` (closed) classified this case as an exclusive/convergence
"3b (negative/absence)" item: absence is not provable by signed closure, so it is
enforced against local state at apply time, with the constraining record's
arrival triggering convergent repair. Two candidate resolutions follow from that,
and both are structurally costly:

- **Convergent repair to "child absent"** turns a soft delete into a cascade and
  retracts records that were validly admitted.
- **Governing-timestamp validity to "child present"** relies on the
  author-supplied `messageTimestamp` (a child can be backdated past the parent's
  delete) and still diverges when an older-timestamped tombstone arrives late.

The engine already treats ancestry as retained immutable state elsewhere: the
record chain and `of` actor checks walk parents by `recordId` with no deletion
filter (`constructRecordChain` resolves the retained initial write). Only the
immediate-parent existence check uses liveness — an inconsistency, not a
deliberate rule. The draft says cross-protocol parents "MUST exist", and that the
initial write is always retained with `isLatestBaseState=false`.

Retention is confirmed in both implementations:

- Rust `handlers/records/delete.rs::prepare_records_delete_transition` retains the
  message for which `is_initial_write(existing, own_author)` is true, reindexed
  with `isLatestBaseState = false`; intermediate updates are deleted.
- TypeScript `store/storage-controller.ts::commitLatestStateTransition` retains a
  displaced message when it `isInitialWrite` or is the passed
  `newestPreDeleteWrite`; on delete both the initial and the newest pre-delete
  write are kept.

## Decision

Separate structural ancestry from liveness:

- A parent-bearing child requires the parent's **retained initial write** in the
  expected protocol. The parent's **current liveness is not consulted** for
  ancestry.
- A soft `RecordsDelete` tombstone does **not** affect ancestry. A child may be
  written under a soft-deleted parent. Path and context must extend the parent
  exactly, and every authorization rule, role, and grant still applies unchanged.
- **A soft delete does not seal or hide a parent's children.** Children remain
  queryable and readable. Sealing or removing a subtree is the job of `prune`.
- A **`prune: true` delete removes ancestry**: the parent is no longer usable as a
  structural ancestor, because prune is the explicit subtree-removal operation. A
  child of a pruned parent is **terminal and unrepairable**.
- Replication classification: missing parent write -> `Incomplete` (retryable);
  pruned parent -> terminal; soft-deleted parent -> admitted.
- Disclosure: a soft-deleted parent and a live parent are indistinguishable in a
  client-facing reply. A pruned parent is terminal, because prune is an explicit
  hard removal. Terminality is surfaced to the receiver's replication/repair
  logic; the recommended wire shape keeps the reply generic and classifies prune
  locally, so no error code becomes a tombstone-existence oracle. (A distinct
  terminal code is an acceptable alternative if explicit disclosure is preferred.)
- Roles and grants remain current-state: revocation must win. Only structural
  ancestry is decoupled.

## Consequences

- `DWN-REC-004` holds for parent-bearing children: the same valid message set
  yields the same admission on every replica, with no retraction, no trusted
  timestamp, and no permanent dead letter.
- **Orphaned-but-addressable children.** A soft-deleted parent's children remain
  queryable and readable. They are reached by their own protocol/path/context
  filter or by `recordId`; they are not reached by navigating from the parent,
  because a direct read of the parent returns 404. Their record chain still
  resolves through the retained initial write, so `of` and role authorization are
  unchanged. A soft delete never revoked that authority.
- **Soft delete does not seal.** Existing children already survive a soft delete;
  this makes the rule consistent. To remove a subtree, use `prune`, which purges
  it. This is a divergence from current Enbox parity and requires a `dwn-spec`
  clarification ("exist"/ancestry = retained write) and an upstream Enbox
  proposal. Until Enbox agrees, a Rust implementation is an intentional,
  documented divergence, not parity.
- The interim receiver-local terminal classification for soft-deleted parents is
  superseded. The mechanism remains for pruned parents and for roles.

## Alternatives considered

- **Governing-timestamp parent validity.** Rejected: `messageTimestamp` is
  author-controlled, so a child can be backdated past the parent's delete; a
  late-arriving older tombstone still diverges without repair.
- **Convergent repair to "child absent".** Rejected: it redefines soft delete as
  a cascade and retracts validly admitted records, requiring a new repair
  mechanism and changing observable deletion semantics.
- **Current state (latest-base-state + tombstone).** Rejected: order-dependent,
  conflicts with `DWN-REC-004`, and produces permanent dead letters.
- **A distinct wire error code for a soft-deleted parent.** Rejected: it turns the
  error code into a tombstone-existence oracle for any submitter.

## Open questions

None.

## Related

- `enboxorg/enbox#991` — closure-based admission model (closed; 3b absence rule)
- `enboxorg/enbox#1679`, `enboxorg/enbox#1680` — interim terminal classification
- `enboxorg/enbox#1684` — TypeScript retained-ancestry implementation
- `enboxorg/enbox-rust-core#303` — Rust parent verification and classification
- `enboxorg/enbox-rust-core#304` — Rust retained-ancestry implementation
- `enboxorg/enbox-rust-core#188` — durable feed substrate and reconciliation
- `DWN-REC-004` (implementation-contract), `DWN-PROTO-001`, `DWN-PROTO-004`, `DWN-PROTO-005`
- `implementation/dependency-resolution.md`, `dwn/protocols.md`
- `enboxorg/dwn-spec` issue — clarify that "exist" means retained, and that prune removes ancestry
