---
domain: dwn
kind: normative
spec: https://dwn-spec.pages.dev/
spec-reviewed: 2026-08-28
divergences:
  - enboxorg/dwn-spec#66
---

# Identity and Signatures

## Verification chain

A DWN authorization signature is verified through the JWS `kid` and the signer's DID Document:

```text
JWS protected header
      -> kid
      -> DID resolution
      -> verification method
      -> public key
      -> signature verification
```

The resulting cryptographic Signer is an input to authorization, not the final authorization result.

## Signed commitments

DWN signatures bind content-addressed components rather than mutable server state. Common authorization payload fields include `descriptorCid` plus operation-specific commitments such as `recordId`, `contextId`, `attestationCid`, `encryptionCid`, Permission Grant IDs, delegated grant IDs, and protocol roles.

The exact payload shape is method-specific.

## Signer and Author

Without delegation:

```text
Signer == Author
```

With author delegation:

```text
Signer = delegate
Author = grantor represented by delegated authority
```

Protocol actor rules must use the semantic Author where appropriate while cryptographic verification still proves the Signer.

## DID service endpoints are separate

DID verification methods answer "which key verifies this signature?" DID service entries answer "where can this identity's DWN be reached?"

Do not make endpoint discovery part of JWS verification or treat endpoint ownership as signature authority.

## Key rotation and historical messages

DWN messages can remain relevant long after signing. Mutable DID methods can rotate or remove verification methods, which raises the question of how a new replica verifies an old message for the first time.

The draft does not yet define a universal historical-resolution contract. See `enboxorg/dwn-spec#66`.

Implementations should therefore avoid assuming that resolving the current DID Document is always sufficient for indefinite validation of historical messages.

## Trust boundaries

Signature verification establishes integrity and signer identity. It does not establish:

- tenant authority,
- protocol permission,
- Permission Grant validity,
- role membership,
- plaintext correctness of encrypted data,
- trust in a forwarding or replication peer.

Those are evaluated by their own layers.

## Common traps

- Do not equate Signer with Author under delegation.
- Do not treat the current DID Document as guaranteed historical verification state.
- Do not infer DWN endpoints from verification methods.
- Do not treat valid signatures as sufficient authorization.
- Do not cache DID resolution as if the cache itself were durable identity history.
