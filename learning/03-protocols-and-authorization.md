---
domain: learning
kind: guide
reviewed: 2026-08-28
---

# 03 — Protocols and Authorization

## Read first

- `dwn/protocols.md`
- `dwn/authorization.md`
- `dwn/permissions.md`
- `builders/authorization-patterns.md`
- `builders/roles-and-membership.md`

## Core model

A protocol is both a structural schema for Records and an authorization program over a context tree.

For any operation, reason about:

```text
protocol path
+ context
+ effective Author
+ invoked role/grant/delegation
+ governing protocol configuration
+ operation timestamp
```

Protocol roles represent capability state. Permission Grants represent explicit bounded authority. Author delegation changes who the operation is semantically attributed to. These mechanisms overlap in purpose but are not interchangeable.

## Temporal authorization

Authorization is not simply evaluated against whatever state is newest now. Historical admission must use the authority/protocol state relevant to the signed operation time where the contract requires it.

That is why a grant revoked tomorrow does not automatically invalidate an operation that was validly authorized today. Continuing disclosure mechanisms such as live subscriptions can still require current authority.

## Checkpoint

You should be able to answer:

1. When should a product relationship be represented as a protocol role rather than a Permission Grant?
2. Why is role scope contextual rather than global?
3. What changes when a delegate acts as the grantor versus a grantee acting as itself?
4. Why must a replicated historical message resolve the governing protocol configuration rather than only the latest configuration?

## Exercise

A workspace has Alice as owner and Bob as a contextual `member`. Bob creates a document while his membership Record is valid. Bob then goes offline. Alice removes Bob's membership. Bob creates another document while offline and later syncs both messages.

For each document write, identify:

- the required role/dependency state;
- the relevant operation time;
- whether current membership removal should retroactively invalidate already-authorized history;
- why a receiving replica must independently run normal admission.

Verify the governing rules in `invariants/authorization.json`, `invariants/protocols.json`, and `conformance/protocols-and-authorization.md`.