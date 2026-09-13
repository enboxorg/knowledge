---
domain: conformance
kind: guide
reviewed: 2026-09-13
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

### Admission

- [ ] The reserved control namespace cannot be declared by a protocol, at the root or nested, through either definition construction or message parsing.
- [ ] Control Records are immutable and undeletable, including by the tenant; an update and a delete are each refused on their own terms rather than as a duplicate.
- [ ] A control Record with no data is refused and not retained, so a retry is not answered as a conflict.
- [ ] A delivery resolves its audience by the exact full identity, superseded keys included, and its ciphertext is never decrypted or parsed to admit it.
- [ ] The role a control Record names is resolved against the configuration governing that Record's own timestamp, and must be a role carrying key agreement.
- [ ] A context shallower than the role's declared depth resolves to nothing rather than being widened to a region.

### Visibility

- [ ] No control Record has an anonymous route.
- [ ] An audience is readable by an exact reference and not by sweeping; enumerating a role's audiences requires authority over the role.
- [ ] Naming a Record by id is not a licence to enumerate: it opens a directory entry through a direct read without widening a collection's candidate population.
- [ ] A delivery is unreachable by exact reference alone; only its parties, or a grant joining the reader to that recipient and covering the delivered role, reach it.
- [ ] A grant that is valid but unconnected to the recipient reaches nothing, however broadly scoped.
- [ ] Recipient access to an already-delivered key survives revocation of the role it was delivered for.

### Current audience and repair

- [ ] Current-audience selection is deterministic under arrival permutations, and delegated mints and countersigned mints carry no tenant priority.
- [ ] A configuration change destroys only retained control state the configuration contradicts; unavailable stores, unparseable payloads and absent configurations all retain.
- [ ] A configuration learned late still governs the Records whose timestamps it covers.
- [ ] A role that survives a configuration change but loses its key agreement keeps custody of material already sealed under it.
- [ ] The obligation to re-examine retained control state survives a crash at any point after the configuration is accepted, and repeating it is safe.

### Grant-key delivery

- [ ] Deliveries use exactly the two immutable core types: encrypted `grantKey` and plaintext `wrappedGrantKey`, with create/anyone and recipient-of-path actions that confer no public readability.
- [ ] Delivery tags carry string `grantId`, `protocol` and 43-character base64url `keyId` plus optional string `protocolPath`, and nothing else; oversized or malformed wrapped envelopes fail closed with stable identities.
- [ ] Admission checks representation, tags, grant, activity at the signed timestamp, grantor authorship, grantee recipientship, and directional scope, re-checked against the historical configuration when role evidence is needed.
- [ ] A delivery without a data stream is retained but not validated and never becomes latest state.
- [ ] Missing grants and missing history stay distinguishable from scope denial so dependency repair can retry.
- [ ] Directional coverage holds: protocol-wide Read covers protocol key and paths; path Read covers its subtree plus keyed local roles its subtree reads through; Write covers only keyed local roles, subtree-restricted when path-scoped; a path grant never covers a protocol key; prefix collisions do not cover.
- [ ] Resolution re-checks current activity, any revocation, tag and payload agreement, coverage under the current configuration, target coverage, derivation path, and both key thumbprints; expiry or revocation refuses the key without deleting the delivery or erasing held keys.

Where draft and current Enbox encryption models differ, label fixtures explicitly and link the relevant divergence issue rather than treating both as one contract.
