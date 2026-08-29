---
domain: builders
kind: guide
reviewed: 2026-08-28
---

# Querying and Indexing

## Design queries before finalizing the schema

List the screens/services that need to discover Records and write the intended filters before adding tags or hierarchy.

Typical dimensions include:

- protocol and protocol path,
- context/parent,
- author or recipient,
- schema/data format,
- tags,
- timestamps and pagination.

If a product-critical view cannot be expressed without downloading every Record, revisit the data model.

## Tags are an index contract

Tags should be:

- stable enough to query over time,
- intentionally exposed as metadata,
- bounded in cardinality/size,
- semantically meaningful rather than UI-specific.

Do not mirror large payload objects into tags.

## Query visibility is authorization

A query is not only an index operation. The result set must respect the same disclosure rules as direct reads.

Design and test Read, Query, Count, and Subscribe together. A system that hides a Record from Query but exposes it through another discovery path has a visibility bug.

## Context-scoped querying

Use context IDs when the application naturally operates within a workspace/conversation/project. Context filters are often a better primary partition than broad protocol-wide queries followed by client-side filtering.

## Pagination and ordering

Do not assume query pagination is a global event log. Query ordering serves discovery of logical Records; durable replication uses the message feed/`MessagesQuery` model described in `dwn/queries-and-sync.md`.

Keep these concerns separate:

```text
RecordsQuery -> application discovery/current visible state
MessagesQuery -> durable message replication/reconciliation
```

## Indexed metadata and encryption

Encrypting Record data does not hide index metadata required for query authorization/discovery. Treat protocol, path, recipient, tags, and other visible metadata as part of the privacy model.

If a sensitive field is only needed after opening a Record, keep it encrypted in payload data rather than indexing it.

## Derived views

Applications may keep local caches/search indexes for richer UI queries. Those are projections, not authoritative DWN state.

They must be rebuildable from the accepted Record/message state and should tolerate invalidation after sync or authorization changes.

## Review checklist

- Can each important product view be expressed with bounded queries?
- Are tags carrying only necessary queryable metadata?
- Are sensitive categories leaking through tags or paths?
- Do Read/Query/Count/Subscribe agree on visibility?
- Is application pagination being confused with replication progress?
- Can local derived indexes be rebuilt after loss?