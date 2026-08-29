---
domain: builders
kind: guide
reviewed: 2026-08-28
---

# Designing a Protocol

## Design the vocabulary before the rules

Name the durable concepts first: `workspace`, `member`, `document`, `comment`, `task`, etc. Each protocol path should represent a stable application concept, not a UI screen or transport operation.

Then define which paths are roots and which are descendants. A protocol path is also an authorization and query boundary, so hierarchy should reflect real ownership/context relationships.

## Treat protocol structure as a state machine

For each path, answer:

- how is the first Record created?
- can there be many Records or one logical Record per context?
- who may update it?
- who may delete it?
- what happens when related role/membership Records change?
- what descendants remain valid after parent changes?

Protocol rules are easier to reason about when each path has a clear lifecycle.

## Keep roles explicit

Use `$role` paths for durable role assignment when authorization depends on contextual membership. Do not overload arbitrary content Records as implicit roles.

Role Records are authorization capability state. Their visibility, deletion, retention, and replication semantics therefore matter more than ordinary content.

See `builders/roles-and-membership.md` and `dwn/authorization.md`.

## Prefer narrow authority

Grant the smallest rule that matches the product requirement:

```text
specific path/context
    > whole protocol
    > unrestricted tenant authority
```

The same principle applies to Permission Grants and delegated author grants.

## Be explicit about actor relationships

A rule like "author can update" is different from "recipient can update" or "member role can update." Write an authorization matrix before the protocol definition so accidental authority expansion is visible.

## Design composition deliberately

Cross-protocol references and actor chains can create useful composition, but they couple authorization to external protocol state. Use them when the external relationship is genuinely part of the domain, not merely to avoid duplicating a small amount of state.

Consider availability: admission may depend on resolving the referenced protocol/context state.

## Avoid encoding business logic the protocol cannot enforce

DWN protocol rules constrain structural/authorization behavior. Application invariants that depend on arbitrary computation may still need client/service validation.

Do not assume a protocol can enforce every domain rule simply because the rule appears in application code.

## Review checklist

- Is every path semantically meaningful?
- Is the context tree stable under expected product growth?
- Are roles explicit and scoped correctly?
- Can a deleted/hidden Record accidentally retain authority?
- Are cross-protocol dependencies necessary?
- Are mutable and immutable fields understood?
- Can every allowed action be explained from the protocol without relying on server arrival order?