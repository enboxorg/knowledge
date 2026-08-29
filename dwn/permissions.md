---
domain: dwn
kind: normative
spec: https://dwn-spec.pages.dev/
spec-reviewed: 2026-08-28
---

# Permissions

## Core model

The Permissions Protocol represents delegated authority as DWN Records. Its main lifecycle objects are Permission Requests, Permission Grants, and Permission Revocations.

## Grant scope

A Grant constrains what its grantee may do. Scope is method-specific and may include interface, method, protocol, protocol path, context, and additional conditions. An operation must remain inside those selectors.

## Temporal semantics

Grant validity is evaluated at the operation's authorization time. A later Revocation does not automatically invalidate an earlier operation that was valid at its signed timestamp.

Long-lived disclosure such as a live subscription can require current authority to be checked again while delivery continues.

## Discovery

Permission Records are normal DWN Records governed by the Permissions Protocol. They are discovered through Records query semantics rather than through a separate Permissions query interface.

Protocol-targeted permission state may be indexed so implementations can discover the Grants and Revocations associated with an application protocol.

## Direct grants and author delegation

A direct Grant authorizes the grantee while the grantee remains the semantic Author. An author-delegated Grant lets a delegate sign while representing the grantor as the effective Author. Protocol actor rules must preserve this distinction.

## Replication

A destination independently evaluates a replicated operation. If its decision depends on a Permission Grant or Revocation, those Records are part of the dependency closure needed for deterministic admission.

## Permissions and encryption

Authorization and decryption are separate capabilities. A Records.Read Grant does not itself transfer cryptographic key material, and possession of historical key material does not by itself authorize future operations.

## Common traps

- Do not treat a Permission Grant as a cryptographic key.
- Do not make later revocation retroactive unless the governing rules explicitly require it.
- Do not infer scope from intent; use the actual typed selectors and conditions.
- Do not omit permission state when reasoning about protocol-scoped replication and convergence.
- Do not confuse a direct Grant with author delegation.
