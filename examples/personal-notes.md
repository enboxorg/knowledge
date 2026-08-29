---
domain: examples
kind: guide
reviewed: 2026-08-28
---

# Worked Example: Personal Notes

## Goal

Build a private notes application where one DWN owner creates, updates, deletes, tags, and queries notes across devices.

This is intentionally the smallest useful example because it isolates the basic DWN design choices before roles, delegation, or multi-party sharing are introduced.

## Actors

- **Tenant / owner** — controls the DWN and owns all note Records.
- **Owner's devices** — may sign directly as the owner or through a separately managed delegated capability; delegation is not required by this example.

## Domain model

The durable concepts are:

```text
note
```

A note has:

- a stable Record identity,
- mutable body/title data,
- queryable metadata such as category and archived state,
- a normal Records lifecycle: initial write -> updates -> optional delete.

Do not create separate Records for every UI field. A title and body that change together belong in one note payload unless they need independent authorization/lifecycle.

## Protocol tree

```text
note
```

Every note is a root Record. There is no useful parent/child context in this domain.

Protocol URI used below:

```text
https://example.com/protocols/notes
```

The URI is illustrative; production protocol URIs should be stable identifiers under the application's control.

## Data model

Example payload:

```json
{
  "title": "DWN design ideas",
  "body": "Keep authorization separate from encryption.",
  "createdByApp": "notes.example.com"
}
```

Useful query metadata:

```text
category = "work"
archived = false
```

Those values are good tag candidates because the client wants to filter on them without downloading every payload.

Do not put sensitive free-form note text into tags merely for search convenience: indexed metadata is a disclosure surface.

## Authorization matrix

| Operation | Owner | Anyone else |
|---|---:|---:|
| Create note | yes | no |
| Read note | yes | no |
| Update note | yes | no |
| Delete note | yes | no |
| Query note metadata | yes | no |

The important point is not the JSON syntax; it is that there is no domain reason to introduce recipient or role authority.

## Illustrative protocol definition

The exact accepted shape must be checked against the current DWN draft/runtime before copying into production. Conceptually:

```json
{
  "protocol": "https://example.com/protocols/notes",
  "published": false,
  "types": {
    "note": {
      "schema": "https://example.com/schemas/note",
      "dataFormats": ["application/json"]
    }
  },
  "structure": {
    "note": {
      "$tags": {
        "category": { "type": "string" },
        "archived": { "type": "boolean" }
      },
      "$actions": [
        { "who": "author", "can": ["create", "read", "update", "delete"] }
      ]
    }
  }
}
```

Treat this definition as design documentation. Validate directive/action spelling against the current spec and SDK used by the application.

## Record walkthrough

Assume Alice owns the DWN.

### 1. Initial write

Alice creates note `N1`:

```text
recordId: N1
protocol: https://example.com/protocols/notes
protocolPath: note
author: did:example:alice
dataFormat: application/json
tags.category: work
tags.archived: false
```

Payload:

```json
{
  "title": "DWN design ideas",
  "body": "Keep authorization separate from encryption."
}
```

The initial write establishes the stable Record identity and immutable lineage fields.

### 2. Update

Alice changes the body. The new RecordsWrite retains `recordId = N1` and the required immutable fields but carries a later logical version.

The application must not create a second note Record just to represent an edit unless version history itself is a first-class domain feature.

### 3. Archive

The note remains the same logical Record. Update `archived` to `true` in queryable metadata if the chosen protocol/runtime supports that mutable tag lifecycle.

### 4. Delete

Alice issues a RecordsDelete for `N1`.

The application should treat deletion as a terminal lifecycle transition for that Record identity rather than trying to "undelete" by writing a later update to the same record.

If product requirements include restore-from-trash, model that intentionally—for example with an application-level archived/trash state before terminal DWN deletion.

## Query patterns

### List active work notes

Conceptually filter on:

```text
protocol     = notes
protocolPath = note
category     = work
archived     = false
```

### Load one note

Use its stable `recordId` when the application already knows it.

### Full-text search

Do not assume DWN Record queries provide arbitrary full-text indexing over encrypted or opaque payloads. A client-side index or explicitly modeled searchable metadata may be required.

## Multi-device behavior

Suppose Alice edits the same note on laptop and phone while offline.

```text
Laptop -> W10
Phone  -> W11
```

When both updates reach the DWNs, deterministic Records conflict semantics determine the retained logical state. The application must not rely on upload arrival order.

For a note editor that needs semantic merging, DWN's Record winner selection is not a replacement for a CRDT/OT document model. Store a mergeable document format in the payload or model operations separately if true collaborative merge semantics are required.

## Failure cases

### Duplicate delivery

The same signed message may be retried. Processing must be idempotent.

### Stale update

An older valid update can arrive after a newer one. It must not become current merely because it arrived later.

### Data mismatch

If supplied bytes do not match the committed data CID/size, reject the write.

### Unauthorized writer

A write signed by a DID without authority under the protocol must be rejected even if its schema is valid.

### Deleted Record replay

Replication of historical pre-delete writes must not reopen a terminally deleted note.

## Schema evolution

Suppose v2 adds `format: "plain" | "markdown"`.

Prefer an additive payload evolution when old clients can safely ignore the field. If the schema URI is strict and changes incompatibly, introduce a new schema/protocol configuration deliberately and test old Record readability under the appropriate historical protocol configuration.

Do not reinterpret historical Records using only today's schema expectations.

## Test plan

Minimum useful tests:

```text
[ ] owner can create/read/update/delete a note
[ ] non-owner cannot write or read private notes
[ ] exact duplicate write is idempotent
[ ] two update arrival orders produce the same final state
[ ] stale update cannot replace newer state
[ ] delete remains terminal when old writes replay
[ ] invalid data CID/size is rejected
[ ] category/archive query returns only intended visible notes
[ ] protocol/schema history still admits retained historical notes correctly
```

## What this example teaches

- Model stable domain concepts, not screens.
- Use one Record lifecycle when fields share identity and authority.
- Treat tags as query/disclosure design, not free indexing.
- Deterministic conflict resolution is not semantic document merging.
- Offline delivery must preserve the same final state independent of arrival order.
