---
domain: implementation
kind: guide
reviewed: 2026-08-28
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
