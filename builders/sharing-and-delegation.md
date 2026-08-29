---
domain: builders
kind: guide
reviewed: 2026-08-28
---

# Sharing and Delegation

## Separate access from representation

Sharing answers "who may access or act on this resource?"
Delegation answers "who may act as another principal?"

Do not use delegated author grants for ordinary sharing unless the delegate truly needs to act as the principal/Author.

## Directed sharing

For one-to-one or known-recipient workflows, recipient-based rules are often the simplest model. Define whether the recipient can only read or may also update/delete.

Recipient identity should remain explicit in the Record model rather than inferred from payload contents.

## Group sharing

For durable group/workspace access, protocol roles usually model contextual authority better than issuing many independent grants. Role assignment becomes the membership/capability state for that context.

Use Permission Grants when the authority is administrative, external to the protocol, or needs a scope that protocol roles do not naturally express.

## Delegated agents and services

A delegate may sign while exercising the grantor's semantic authority. Keep the principal/delegate relationship visible in logs and UI so users can understand whose authority produced an operation.

Scope delegated grants narrowly and consider:

- allowed interface/method,
- protocol/context,
- expiry,
- revocation,
- whether further delegation is permitted.

## Revocation is not erasure

Revoking access prevents future authorized actions according to the relevant semantics; it does not erase data or keys already received.

For confidential group data, pair authorization changes with an encryption/key-distribution strategy for future records.

## Sharing across DWNs

Do not assume a recipient uses the same physical DWN. Discovery, endpoint resolution, delivery/replication, and authorization are distinct layers.

Applications should tolerate multiple endpoints and retry/failover without treating endpoint identity as user identity.

## Common mistakes

- using payload fields as the only source of access authority,
- making grants tenant-wide when one protocol/context would suffice,
- confusing a signer with the principal they represent,
- assuming grant revocation retroactively invalidates historical writes,
- assuming revoked readers forget previously decrypted content,
- coupling application identity to one server URL.