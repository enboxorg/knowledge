---
domain: builders
kind: guide
reviewed: 2026-08-28
---

# Data Modeling

## Model durable facts, not UI projections

Use Records for durable application facts that need provenance, portability, sharing, or replication. Derived counters, denormalized lists, view state, and transient workflow state should usually be recomputed or cached unless they are independently meaningful records.

## Record identity versus version

A logical Record keeps one `recordId` across updates. Treat later writes as versions of the same logical object, not new objects that happen to share fields.

If the domain requires immutable historical events, model those as separate Records rather than repeatedly updating one Record and expecting all versions to behave like an append-only event stream.

## Contexts are domain structure

Use parent/context relationships when children genuinely belong to a durable parent scope.

Good examples:

- comments under a document,
- tasks under a workspace,
- messages under a conversation.

Avoid deep hierarchies just to mimic nested JSON. Context affects authorization and query scope, so every level should have semantic value.

## Data versus tags

Put content in Record data when it is payload. Use tags for values that must participate in discovery/filtering and are acceptable as query-visible metadata.

A useful test:

```text
Would a server need this value to select the Record without reading its data?
```

If no, keep it in the payload.

## Stable identifiers

Prefer Record IDs and protocol contexts as durable references over mutable human-readable names. Names/slugs may change; authorization and referential integrity should not depend on them unless the protocol explicitly intends that behavior.

## Relationships

For relationships between Records, distinguish:

- structural parent/child relationship,
- protocol/context relationship,
- application-level reference stored in data/tags,
- cross-protocol `$ref` semantics.

Do not use a structural context edge merely because two application objects reference one another.

## Mutation strategy

Choose intentionally between:

- update-in-place logical Records,
- immutable child/event Records,
- tombstone/delete lifecycle.

For audit-heavy domains, an immutable event Record plus a separately derived/current-state Record is often easier to reason about than relying on old retained versions as an application event API.

## Metadata leakage review

Before adding tags, recipients, protocol roles, or encryption-control metadata, assume that authorization metadata may remain visible even when payload data is encrypted. Minimize metadata that reveals sensitive categories, relationships, or workflow state.