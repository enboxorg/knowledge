---
domain: examples
kind: guide
reviewed: 2026-08-28
---

# Worked Example: Shared Document

## Goal

Model a document owned by one person and explicitly shared with another person, including comments and the practical limits of revocation.

This example introduces `recipient` authority without introducing contextual roles.

## Actors

- **Owner / author** — creates and controls the document.
- **Recipient / collaborator** — receives access to the document and may comment.
- **Other DIDs** — have no access unless separately authorized.

Assume Alice owns the DWN and shares a document with Bob.

## Domain model

```text
document
  comment
```

The document is the root of a context. Comments belong to that document context.

Why comments are separate Records:

- independent authorship,
- append-oriented lifecycle,
- separate queryability,
- different update/delete policy from the document body.

## Protocol tree

```text
document
└── comment
```

Protocol URI:

```text
https://example.com/protocols/shared-doc
```

## Data model

Document payload:

```json
{
  "title": "Project brief",
  "body": "Initial draft..."
}
```

Document metadata:

```text
status = "draft"
```

Comment payload:

```json
{
  "body": "Could we clarify the rollout section?"
}
```

The document recipient is represented using the Record's recipient semantics rather than duplicating the collaborator DID in arbitrary payload JSON.

## Authorization matrix

| Operation | Document author | Document recipient | Other |
|---|---:|---:|---:|
| Create document | yes | no | no |
| Read document | yes | yes | no |
| Update document | yes | no in this design | no |
| Delete document | yes | no | no |
| Create comment | yes | yes | no |
| Read comments | yes | yes | no |
| Update own comment | yes, if author | yes, if author | no |
| Delete own comment | yes, if author | yes, if author | no |

This design intentionally makes collaboration asymmetric: Bob can review/comment but cannot edit Alice's document.

If co-editing is required, use the appropriate protocol co-update semantics or model collaboration differently; do not casually broaden `recipient` to every operation.

## Illustrative protocol definition

Conceptually:

```json
{
  "protocol": "https://example.com/protocols/shared-doc",
  "published": false,
  "types": {
    "document": {
      "schema": "https://example.com/schemas/document",
      "dataFormats": ["application/json"]
    },
    "comment": {
      "schema": "https://example.com/schemas/comment",
      "dataFormats": ["application/json"]
    }
  },
  "structure": {
    "document": {
      "$actions": [
        { "who": "author", "can": ["create", "read", "update", "delete"] },
        { "who": "recipient", "can": ["read"] }
      ],
      "comment": {
        "$actions": [
          { "who": "recipient", "of": "document", "can": ["create", "read"] },
          { "who": "author", "of": "document", "can": ["create", "read"] },
          { "who": "author", "can": ["update", "delete"] }
        ]
      }
    }
  }
}
```

The exact `who/of/can` syntax and available action names should be validated against the current draft and SDK before production use. The design intent is the important part: descendant comment authority derives from the parent document relationship.

## Record walkthrough

### 1. Alice creates the document

```text
recordId: D1
protocolPath: document
author: Alice
recipient: Bob
contextId: D1
```

### 2. Bob reads it

Bob's read authority comes from being the document recipient.

### 3. Bob creates comment C1

```text
recordId: C1
protocolPath: document/comment
parentId: D1
contextId: D1/.../C1
author: Bob
```

Authorization resolves Bob's relationship to the parent document rather than treating any Bob-authored comment as valid globally.

### 4. Alice updates the document

The root Record keeps `recordId = D1`; comments remain descendants of the same logical document context.

### 5. Alice removes Bob's future access

This is where product language matters.

Changing future DWN authorization does **not** erase bytes Bob already downloaded. If Bob has already received plaintext or decryption material, revoking future reads cannot make him forget it.

A product should say:

```text
"remove future access"
```

not:

```text
"erase all copies from Bob"
```

## Sharing design alternatives

### Recipient-based sharing

Best when:

- one explicit principal receives a Record,
- the relationship is naturally attached to the Record,
- membership/group semantics are unnecessary.

### Permission Grant

Better when Bob needs a capability spanning multiple Records, paths, or operations that should be managed separately from one Record's recipient field.

### Role

Better when access is contextual membership, such as "reviewer in workspace W" rather than "recipient of document D1."

## Query patterns

Alice's document list:

```text
protocol = shared-doc
protocolPath = document
author = Alice
```

Bob's received document list:

```text
protocol = shared-doc
protocolPath = document
recipient = Bob
```

Comments for document D1:

```text
protocol = shared-doc
protocolPath = document/comment
contextId scoped to D1
```

Do not query comments solely by author if the application needs document scoping; context is part of the authorization/data model.

## Offline and sync behavior

Bob may create a comment offline while Alice edits the document elsewhere. When Bob's signed comment reaches the DWN, authorization must evaluate the relevant governing protocol and relationship state according to DWN temporal rules.

A sync engine must not bypass normal admission just because the message came from Bob's local replica.

If access was removed before Bob's offline action according to the relevant authorization semantics, the application must be prepared for the pending operation to be rejected on sync.

UX should distinguish:

- pending local operation,
- durably admitted operation,
- rejected operation that must be surfaced to the user.

## Revocation and encryption

This example does not require encryption to explain sharing semantics.

If document content is encrypted, there are two separate questions:

```text
May Bob read according to DWN authorization?
Does Bob possess the decryption material?
```

Both must be satisfied for useful access. Removing authorization and rotating/discontinuing key distribution may prevent future access to newly encrypted material, but cannot revoke plaintext Bob already learned.

## Failure cases

### Bob attempts document update

Rejected in this design, even though Bob can read and comment.

### Carol creates a comment under D1

Rejected because she has no qualifying relationship to the document.

### Bob creates comment under unrelated D2

Bob's authority for D1 must not leak into D2's context.

### Parent dependency missing during replication

A replica that receives C1 before D1 may be unable to establish the parent relationship. Treat this as a repairable dependency condition rather than silently admitting the child or permanently declaring it invalid without attempting dependency repair.

### Alice deletes D1

The application must define what comment visibility/lifecycle means after parent deletion. Do not assume deleting a parent physically deletes all descendants unless the protocol operation explicitly has pruning semantics.

## Schema/protocol evolution

A later version might add `suggestion` descendants or co-edit authority. Install a new protocol configuration deliberately and preserve historical configuration resolution for old messages.

Do not reinterpret Bob's historical comment using only the newest protocol policy.

## Test plan

```text
[ ] Alice can create/read/update/delete D1
[ ] Bob can read D1
[ ] Carol cannot read D1
[ ] Bob can create/read comments under D1
[ ] Carol cannot create comment under D1
[ ] Bob cannot update D1 in this design
[ ] Bob's D1 authority does not authorize D2
[ ] child-before-parent replication is repairable and converges
[ ] duplicate comment delivery is idempotent
[ ] offline Bob operation is re-admitted normally on sync
[ ] removal of future access does not claim erasure of previously disclosed data
[ ] historical messages resolve against the correct protocol configuration
```

## What this example teaches

- Use recipient when the relationship is truly Record-specific.
- Descendant authority should be scoped through the parent/context relationship.
- Read authorization and decryption possession are distinct.
- Revocation controls future authority, not information already disclosed.
- Offline-created operations are proposals until normal DWN admission succeeds.
