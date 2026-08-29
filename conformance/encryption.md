---
domain: conformance
kind: guide
reviewed: 2026-08-28
---

# Encryption Conformance

Use with `dwn/encryption.md` and the currently targeted encryption contract.

## Binding and integrity

- [ ] Encryption metadata is integrity-bound to the signed message according to the targeted contract.
- [ ] Decryption is not attempted until message authorization/integrity checks required by the contract have passed.
- [ ] Wrong or tampered encryption metadata is rejected.

## Key agreement and wrapping

- [ ] Supported key-agreement algorithms interoperate on canonical fixtures.
- [ ] Wrapped keys decrypt only for intended recipients/audiences.
- [ ] Wrong key identifiers, algorithms, or recipient material fail safely.
- [ ] Small-order/all-zero shared-secret edge cases are rejected where required.

## Authorization versus decryptability

- [ ] A Record can be valid DWN state even when a particular reader lacks decryption material where the protocol allows that distinction.
- [ ] Permission to read/query a Record does not implicitly create decryption authority.
- [ ] Revocation/removal affects future key delivery according to the targeted model but does not pretend already-delivered plaintext/key material can be erased.

## Control-plane behaviour

- [ ] Audience/role/grant key-control Records obey the targeted spec or documented implementation contract.
- [ ] Missing admission dependencies and missing decryption-only dependencies are classified distinctly when applicable.
- [ ] Rotation/key-delivery fixtures cover old and new ciphertext across membership changes.

Where draft and current Enbox encryption models differ, label fixtures explicitly and link the relevant divergence issue rather than treating both as one contract.
