---
domain: enbox
kind: implementation
repositories:
  - enboxorg/enbox
  - enboxorg/enbox-rust-core
upstream-baseline: c63bf424ac0997583db825e8a5fddf1507d30c40
reviewed: 2026-08-28
related-issues:
  - enbox-rust-core#191
  - enbox-rust-core#207
  - enbox-rust-core#241
  - dwn-spec#64
---

# Encryption Implementation

## Rust primitives

Rust already implements substantial record-encryption mechanics:

- A256CTR content encryption,
- X25519-HKDF-SHA256+A256KW key agreement/wrapping,
- protocolPath and roleAudience derivation shapes,
- encryption envelope validation,
- legacy-read compatibility while rejecting legacy-JWE writes.

The gap is therefore not basic cryptography.

## Current TypeScript control plane

Current Enbox adds the lifecycle that turns key material into governed DWN state. This includes encryption-control records, audience/delivery state, grant-key delivery, scope checks and key-recipient selection.

The relevant invariant is:

```text
Permission Grant = authorization capability
key delivery      = cryptographic capability
```

The implementation must not allow delivered key scope to exceed authorized grant/protocol scope.

## RecordsWrite binding

The author signature commits to `encryptionCid`, preventing substitution of the top-level encryption object after signing. Record admission can validate the encryption envelope structurally without possessing recipient private keys or plaintext.

`dataCid` commits to the stored ciphertext bytes, not plaintext.

## Identity separation

Signing identity and encryption identity are separate:

```text
DID verification key
    !=
protocol/role/grant encryption key material
```

Do not derive encryption authority from the fact that a DID signed a message.

## Current divergence

The DWN draft encryption-control vocabulary and current TypeScript Enbox have evolved differently. Current implementation work should follow the explicit parity decision/issue rather than silently mixing draft `audienceEpoch` terminology with upstream `$encryption/audience` / `$encryption/delivery` and grant-key behavior.

`dwn-spec#64` tracks broader encryption design questions. `enbox-rust-core#191` owns current upstream parity.

## Rust priorities

The important missing Rust work is system-level:

- control-record lifecycle and authorization,
- audience/delivery management,
- grant-key / wrapped-key flows,
- key-agreement recipient selection from resolved DID documents,
- replication/dependency closure for encryption control,
- encryption-domain fingerprint contribution.

## Coding-agent rule

Treat cryptographic primitives and key-distribution policy as separate layers. A successful AES/X25519 round trip is not evidence that DWN encryption authorization, lifecycle, rotation or replication semantics are correct.