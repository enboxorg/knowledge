---
domain: dwn
kind: normative
spec: https://dwn-spec.pages.dev/
spec-reviewed: 2026-08-28
---

# DWN Foundations

## Core model

A DWN message is a signed description of an operation. A Record is logical state derived from one or more retained Records messages.

Do not equate:

```text
message == record
```

The useful model is:

```text
signed messages
      +
deterministic validation and ordering
      =
logical DWN state
```

## Message structure

Every DWN operation has a descriptor identifying its interface, method, timestamp, and method-specific fields. Authorization JWS payloads commit to the descriptor by CID and may additionally bind operation-specific values such as Record ID, context ID, attestation CID, encryption CID, Permission Grant IDs, delegated grant ID, and protocol role.

The signature therefore authorizes a precise operation description rather than arbitrary mutable server state.

## Identity boundary

The cryptographic **Signer** and semantic **Author** are normally the same DID. Author delegation can separate them:

```text
Signer = delegate/grantee
Author = grantor/principal represented by the delegated grant
```

Authorization logic must use the resolved semantic Author where the protocol defines actor semantics, while signature verification still proves the Signer.

## Content addressing

DWN uses content-addressed commitments extensively:

- `descriptorCid` commits to an operation descriptor.
- `dataCid` commits to stored Record data bytes.
- `attestationCid` and `encryptionCid` bind top-level objects that are outside the descriptor.
- message CIDs provide stable identity for retained messages and replication.

Content addressing provides integrity and idempotent identity; it is not a consensus mechanism.

## Record identity

A Record has a stable `recordId` established by its initial write. Later updates keep that Record identity while replacing mutable state.

Protocol Records additionally participate in a context hierarchy:

```text
root Record
  contextId = recordId

child Record
  parentId  = parent recordId
  contextId = root/.../child
```

The exact context chain matters for protocol authorization, roles, cross-protocol references, and scoped Permission Grants.

## Trust model

A DWN node does not trust messages merely because another DWN stored or forwarded them. Replicated and forwarded messages pass through the same validation/admission semantics as directly submitted messages.

This is the foundation of multi-DWN convergence:

```text
same valid message set
      +
same deterministic rules
      ->
same logical state
```

## Common traps

- Do not treat `messageTimestamp` as a causal clock.
- Do not infer semantic Author solely from the JWS `kid` when delegation is present.
- Do not treat storage arrival order as state order.
- Do not assume a Permission Grant also transfers decryption capability.
- Do not treat a DWN endpoint or peer as a trusted database replica; it is another source of signed messages.
