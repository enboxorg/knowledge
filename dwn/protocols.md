---
domain: dwn
kind: normative
spec: https://dwn-spec.pages.dev/
spec-reviewed: 2026-08-28
---

# Protocols

## Purpose

A DWN Protocol defines application-specific Record structure, type constraints, authorization rules, roles, delivery behaviour, and encryption policy.

A protocol definition is installed through `ProtocolsConfigure` and governs Records that declare its protocol URI.

## Structure and types

Protocol definitions describe:

- `types` — schemas/data formats and type-level constraints,
- `structure` — allowed protocol paths and nested Records,
- rule directives such as `$actions`, `$role`, `$size`, `$tags`, `$immutable`, `$squash`, `$delivery`, `$recordLimit`, `$keyAgreement`, and encryption requirements,
- `uses` / `$ref` for cross-protocol composition.

A Record at a protocol path must satisfy both the type definition and the structural/rule-set constraints that govern that path.

## Authorization rules

`$actions` define which semantic actors may perform operations such as create, update, co-update, delete, co-delete, prune, read, or squash.

Actor selectors may refer to:

- the Record author,
- the Record recipient,
- anyone,
- protocol roles,
- an actor associated with another Record path through `of`.

Protocol authorization evaluates the effective **Author**, not merely the cryptographic Signer. Author delegation can therefore make a delegate act semantically as the grantor where delegation permits it.

## Roles

A `$role` path represents role-assignment Records. Role invocation is context-sensitive: possessing a role outside the relevant protocol context must not authorize unrelated Records.

Role records are authorization capabilities and must be handled carefully by visibility/retention features. Current Enbox, for example, forbids `$recordLimit` on `$role` paths; see the linked spec convergence work rather than assuming draft and implementation semantics are identical.

## Temporal governance

Protocol configuration is temporal state. A Record is validated against the protocol configuration that governs the relevant Record timestamp, not blindly against whatever protocol version is newest today.

This matters for:

- replicated historical Records,
- updates to long-lived Records,
- protocol migrations,
- cross-protocol references,
- encryption policy.

Implementations must retain enough protocol configuration history to resolve the governing version deterministically.

## Cross-protocol composition

`uses` maps an alias to another protocol URI. `$ref` allows a position in one protocol to refer to structure/types from another protocol.

Composition turns protocol resolution into a graph rather than one self-contained tree. Runtime code may need to resolve:

- parent Records that belong to another protocol,
- cross-protocol roles,
- `of` actor references,
- encryption audiences/key agreements,
- replication dependencies.

Namespaces do not simply merge across a `$ref`; the referenced position and children can have different governing protocol/type sources.

## Encryption policy

Protocols can require encryption and define key-agreement policy. Encryption policy belongs to protocol semantics, while actual decryption key distribution is a separate capability lifecycle.

Do not equate:

```text
protocol authorizes read
```

with:

```text
reader possesses decryption material
```

Both may be required for useful access.

## Delivery and limits

Protocol directives can affect how Records are delivered or selected for visibility. Current TypeScript Enbox and the draft have known divergences around some directives, particularly `$recordLimit`; implementation docs must link the corresponding `dwn-spec` issue instead of presenting one behaviour as universally normative.

## Common traps

- Do not evaluate historical Records only against the newest protocol configuration.
- Do not treat a protocol role as globally valid outside its context.
- Do not resolve cross-protocol parents using a same-protocol-only query.
- Do not assume draft directive semantics exactly match current Enbox without checking known divergence issues.
- Do not merge authorization policy and encryption key possession into one concept.
