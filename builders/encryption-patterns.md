---
domain: builders
kind: guide
reviewed: 2026-08-28
---

# Encryption Patterns

## Authorization and decryptability are separate

A DWN can admit and expose a Record according to authorization rules while a client still lacks the key material required to decrypt the payload.

Design both planes:

```text
authorization -> may discover/read ciphertext
key distribution -> can recover plaintext
```

Do not assume a Permission Grant or role assignment automatically transfers decryption capability.

## Encrypt payloads, review metadata separately

Encryption protects Record data, not every piece of surrounding metadata. Protocol/path, recipient relationships, tags, and key-control records can still reveal information.

Before shipping an encrypted protocol, perform a metadata-leakage review independent of payload encryption.

## Shared-role data

For role/group audiences, use the current Enbox encryption-control model rather than inventing per-record ad hoc key exchange. Follow `enbox/encryption.md` for current implementation behavior and `dwn/encryption.md` for draft semantics/divergences.

Treat membership changes as key-lifecycle events for future data. Removing a member from a role does not retract keys or plaintext already delivered.

## Direct sharing

For a small known recipient set, direct recipient key wrapping may be simpler than maintaining group key state. Choose based on expected membership churn and fan-out.

## Rotation

Key rotation should answer:

- which future Records use the new key?
- can delayed/offline writers still encrypt successfully?
- must old data remain decryptable?
- who is responsible for distributing replacement key material?
- how does a recovering device obtain historical keys?

Do not equate identity signing-key rotation with application encryption-key rotation; they solve different problems.

## Recovery and multi-device access

Plan key recovery before encrypting durable user data. A system that can replicate ciphertext perfectly but cannot restore decryption capability after device loss has not achieved durable user ownership.

## Application behavior on missing keys

Missing key material is not the same as invalid ciphertext. Clients should be able to distinguish:

- unauthorized,
- authorized but key unavailable,
- malformed/tampered encryption metadata,
- successfully decrypted.

That distinction matters for sync repair and user-facing recovery flows.

## Review checklist

- Who can authorize reads?
- Who can actually decrypt?
- What metadata remains visible?
- What happens when membership changes?
- What happens to old data after rotation?
- Can a new/recovered device obtain the required historical keys?
- Are cryptographic primitives being reused from Enbox rather than reimplemented in application code?