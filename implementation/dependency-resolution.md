---
domain: implementation
kind: guide
reviewed: 2026-09-13
---

# Dependency Resolution

Some valid DWN messages cannot be admitted until referenced state is available. Implementations should distinguish this from permanent invalidity.

## Dependency classes

Examples include:

- parent or initial Records messages,
- protocol definitions,
- Permission Grants and delegated grants,
- role Records,
- data referenced by CID,
- encryption-control material where required for admission or decryption.

## Required distinction

A processing result should be able to represent at least:

```text
accepted
permanently invalid / unauthorized
repairable incomplete
transient infrastructure failure
```

Collapsing `Incomplete` into generic rejection makes reliable replication difficult because the caller cannot know whether fetching a missing dependency can make progress.

## Repair loop

```text
candidate
→ identify missing dependency
→ fetch exact dependency from an authorized source
→ admit dependency through normal processing
→ retry candidate
```

Set bounds on recursion, repeated failures, and dependency fan-out. Detect cycles where dependency graphs permit them.

## Admission closure versus usability

Not every missing decryption key is necessarily an admission dependency. Keep "can this message become valid DWN state?" separate from "can this reader decrypt/use the payload?" where the protocol defines those separately.

See `dwn/queries-and-sync.md`, `dwn/encryption.md`, and `implementation/error-model.md`.

## Known parity caveat: a deleted parent (and role revocation) is not repairable

Current Enbox resolves a parent Record by its current, not-deleted state (a
latest-base-state filter plus a tombstone check), and a delete is terminal.
Together these make admission of a parent-bearing child depend on delivery order:

- If the child is admitted while the parent still exists, it is accepted; a later
  soft delete does not cascade to it.
- If the parent's delete is already the latest state, the child is rejected. The
  parent can never return, so the write can never be repaired.

Two replicas holding the same valid message set can therefore converge to
different Record state, which conflicts with `DWN-REC-004` read as a global
admission guarantee. Role revocation has the same shape: role lookups also use the
latest-base-state filter, so a role-invoking write delivered after the role delete
is rejected even if it was authored before.

### Why the timestamp-relative alternative is rejected

Evaluating parent existence at the child's governing timestamp is draft-faithful
in spirit but unsafe: `messageTimestamp` is author-controlled, so an author can
backdate a child past the parent's delete and have it admitted. It also does not
converge on its own, because a tombstone whose timestamp precedes the child's can
arrive after the child was admitted; full convergence would require the parent's
tombstones to be part of the child's dependency closure (or retraction), which is
a larger change.

### Resolution: retained ancestry (ADR 0007)

Structural parent existence is evaluated against the parent's **retained initial
write**, not its current liveness. A soft delete does not remove ancestry (and
does not seal or hide children); a `prune` removes ancestry and is terminal. See
`decisions/0007-retained-parent-ancestry.md`.

This restores `DWN-REC-004` for parent-bearing children without retraction or
trusted timestamps. The interim receiver-local terminal classification for soft
deletes (`enboxorg/enbox#1679` / `#1680`, `enboxorg/enbox-rust-core#303`) is
superseded. Current Enbox and Rust both resolve parent ancestry from the retained
initial write (`enboxorg/enbox#1685`, `enboxorg/enbox-rust-core#304`); a `prune`
tombstone remains the terminal case.
