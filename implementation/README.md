---
domain: implementation
kind: guide
reviewed: 2026-08-28
---

# DWN Implementation Guides

This section is for authors of DWN engines.

It translates the semantic invariants in `dwn/` into implementation contracts without prescribing a language, database, framework, or Enbox-specific code structure.

Use it with:

- `dwn/` for normative/spec-derived semantics,
- `conformance/` for observable behaviour checklists,
- `enbox/` for one concrete implementation architecture.

## Guides

- `message-processing-pipeline.md`
- `records-state-machine.md`
- `authorization-evaluation.md`
- `storage-contracts.md`
- `replication-contract.md`
- `dependency-resolution.md`
- `error-model.md`
- `conformance-testing.md`

## Principle

An implementation is correct because it preserves DWN semantics and externally observable behaviour, not because it copies another implementation's internal structure.
