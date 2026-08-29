---
domain: learning
kind: guide
reviewed: 2026-08-28
---

# 05 — Identity, Encryption, and Trust

## Read first

- `dwn/identity-and-signatures.md`
- `dwn/encryption.md`
- `dwn/attestations.md`
- `builders/encryption-patterns.md`

## Core model

DWN trust is layered. Signature verification proves possession of a signing key bound to a DID verification method; authorization determines whether that principal may perform the operation; encryption determines whether a party can recover plaintext; attestation lets a third party endorse a specific Record version.

Do not collapse these into one concept:

```text
signature validity
!= authorization
!= decryption capability
!= attested trust
```

A reader may be authorized but lack current decryption material. An attester may endorse a signed descriptor without receiving continuing update authority. A delegate may be authorized to act without receiving every encryption key.

## Key lifecycle

Encryption design is a lifecycle problem, not merely a cipher choice. Consider:

- record content-encryption keys;
- role/audience key material;
- grant-delivery keys;
- participant removal;
- key rotation and recovery;
- metadata that remains visible even when data is encrypted.

Revoking future access cannot erase plaintext or keys already obtained by a former participant.

## Checkpoint

You should be able to answer:

1. What does resolving a JWS `kid` actually establish?
2. Why can DID key rotation create historical-verification questions?
3. Why is an attestation version-specific?
4. Why must authorization and decryptability be tested separately?
5. Why does membership revocation not imply retroactive secrecy?

## Exercise

Alice and Bob share an encrypted workspace. Bob is removed from the member role after decrypting several existing documents.

Explain separately:

- which future operations Bob should lose authority to perform;
- which future key material Bob should stop receiving;
- why already-obtained plaintext cannot be revoked;
- what a rotation strategy can protect;
- what metadata may remain observable despite encryption.

Verify against `invariants/identity-encryption.json` and `conformance/encryption.md`.