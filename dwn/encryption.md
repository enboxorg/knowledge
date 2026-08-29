---
domain: dwn
kind: normative
spec: https://dwn-spec.pages.dev/
spec-reviewed: 2026-08-28
divergences:
  - enboxorg/dwn-spec#64
---

# Encryption

## Core model

DWN encryption separates record admission from plaintext access. A node can validate and retain an encrypted RecordsWrite without possessing a recipient's decryption keys.

The important commitments are:

```text
ciphertext bytes
   -> dataCid / dataSize

encryption metadata
   -> encryptionCid

author signature
   -> binds descriptor + encryptionCid
```

This prevents substitution of the encryption envelope without invalidating the author's signed operation.

## Record encryption

The current DWN encryption model uses a per-record content-encryption key (CEK) to encrypt payload bytes, then wraps that CEK for one or more authorized cryptographic audiences.

The current envelope family uses:

- AES-256-CTR for content encryption,
- X25519 key agreement,
- HKDF-SHA256 key derivation,
- AES Key Wrap for the CEK.

Key-encryption entries identify the derivation scheme and audience-specific metadata needed to derive or locate the wrapping key.

## Protocol-derived audiences

Protocols may define encryption policy and key-agreement material at protocol/path boundaries. A recipient's ability to decrypt is derived from the relevant protocol path, role audience, or other defined key-delivery mechanism rather than from the DWN signing key itself.

Do not conflate:

```text
DID signing key
protocol encryption key
role audience key
grant-delivery key
```

They serve different purposes and have different rotation/custody semantics.

## Authorization versus decryptability

A principal can be authorized to read but still lack key material. Conversely, historical key material may remain cryptographically usable after authorization changes.

Therefore:

```text
authorization capability != decryption capability
```

Key-delivery protocols should bind delivered cryptographic scope to the logical authority that justifies it, but they remain separate layers.

## Rotation

Encryption key rotation is generally forward-looking. Removing or revoking access does not erase key material already delivered to a recipient and cannot make previously learned plaintext secret again.

Protocol design should distinguish future-record confidentiality from retroactive secrecy.

## Admission closure and decryption closure

A Record can be admissible while not yet decryptable by the reader. Some dependencies are required to validate the encrypted message; others exist only to obtain the keys needed for plaintext access.

The draft's exact boundary and retrieval model remains an active design topic; see `enboxorg/dwn-spec#64`.

## Implementation divergence

Current TypeScript Enbox encryption-control behaviour has evolved beyond parts of the draft model. The knowledge repository records the draft here; current shipping control paths and grant-key delivery belong under `enbox/` implementation documentation.

## Common traps

- Do not require plaintext access to admit an encrypted record.
- Do not use DID signing keys as an implicit encryption-key hierarchy.
- Do not equate a Permission Grant with delivered key material.
- Do not assume revocation destroys keys already distributed.
- Do not silently mix current Enbox encryption-control behaviour with draft-only audience-epoch semantics.
