---
domain: builders
kind: guide
reviewed: 2026-08-28
---

# Roles and Membership

## Treat role Records as capability state

A role Record is not just profile data. If protocol rules authorize actions based on holding that role, creating/deleting/updating the role changes authority.

That means role lifecycle deserves the same care as grants and credentials.

## Scope roles to the smallest useful context

Prefer:

```text
workspace A / editor
```

over a protocol-wide editor role when the application only needs workspace-local authority.

Context-scoped roles reduce accidental authority bleed between otherwise unrelated records.

## Membership versus role

Membership answers "is this identity part of this context?" A role answers "what authority does this identity have here?"

They may be represented by the same role Record if the protocol meaning is simple, but do not assume every member should carry identical authority.

## Removal semantics

When membership ends, ask separately:

- may the identity create new Records?
- may it update old Records it authored?
- may it read historical content?
- may it continue receiving encrypted keys?
- should previously delivered plaintext/key material remain usable?

Authorization revocation cannot erase information already learned. Encryption/key rotation controls future decryptability, not retroactive memory.

## Avoid hidden live capabilities

Do not use visibility policies that can hide a role Record while the authorization engine still treats the role as active. This is why authority-bearing Records need stricter lifecycle rules than ordinary content.

## Administrative roles

For admin-style roles, explicitly define who can create and remove administrators. Avoid circular rules where possession of a role is sufficient to mint unlimited equivalent roles unless that is the intended governance model.

## Role changes while offline

Offline clients can operate with stale membership knowledge. Design for eventual rejection/reconciliation rather than assuming clients always know the latest role state.

A client should treat server/DWN admission as authoritative for whether an operation is currently valid.

## Useful tests

- member can perform exactly the intended methods,
- same DID with role in context A cannot act in B,
- role deletion blocks future role-authorized operations,
- stale offline operation is rejected or reconciled predictably,
- duplicate role messages do not create duplicate capability,
- role visibility rules never leave hidden authority active,
- encryption delivery stops appropriately after removal.