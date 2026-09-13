---
domain: enbox
kind: implementation
repositories:
  - enboxorg/enbox
  - enboxorg/enbox-rust-core
upstream-baseline: c63bf424ac0997583db825e8a5fddf1507d30c40
reviewed: 2026-09-13
related-issues:
  - enbox-rust-core#191
  - enbox-rust-core#207
  - enbox-rust-core#241
  - dwn-spec#64
---

# Encryption Implementation

## Record encryption mechanics

Both implementations share the record-encryption mechanics:

- A256CTR content encryption,
- X25519-HKDF-SHA256+A256KW key agreement/wrapping,
- protocolPath and roleAudience derivation shapes,
- encryption envelope validation.

There is one record-encryption format. The older JWE record shape — a
flattened serialization carrying `recipients[]` and `derivationScheme`
headers — is rejected rather than read: it was never deployed, so no stored
ciphertext depends on it, and keeping a decrypt path for it would keep a second
format alive in every reader for no custody benefit. This is a record-format
decision only; Compact JWE remains in use for the connect envelope and for
vault-at-rest material, which are different formats with different key
management.

The gap was never basic cryptography.

## Encryption control plane

Key material becomes governed DWN state through reserved virtual paths inside
the source protocol: `$encryption/audience` publishes a role's key, and
`$encryption/delivery` hands that key to a role holder. `$encryption` is
reserved — a protocol may not declare it at any depth.

The relevant invariant is:

```text
Permission Grant = authorization capability
key delivery      = cryptographic capability
```

Delivered key scope must never exceed authorized grant/protocol scope.

### Admission

Control records are admitted against a fixed contract rather than a protocol's
type and rule map, because they sit where no application rule set exists. They
are immutable, unpublished, small enough to validate inline, initial-write
only, and carry their identity in tags. They cannot be updated, and cannot be
deleted even by the tenant: key material recipients already hold cannot be
recalled by removing the record that described it, so allowing the delete would
only destroy the node's own account of what was distributed.

An audience is identified by `{protocol, rolePath, contextId}` together with
its `keyId`. The three-field form names a role's directory; the four-field form
names one stored key. A delivery references a stored audience by the exact
four-field identity, superseded keys included, and its ciphertext is never
decrypted or parsed during admission.

The role a control record names is resolved against the configuration governing
that record's own timestamp, never the newest one — see `DWN-PROTO-004`. The
path must be a role carrying `$keyAgreement`: a role without one has no key to
distribute, and a non-role path has no membership to key.

### Visibility

An audience and a delivery are reached by different routes, and the asymmetry
is the point. An audience is a directory entry: anyone who can already name it
exactly may read it, because naming a specific stored key is not the same as
enumerating a role's keys. Enumerating needs authority over the role itself —
a read grant covering it, or the authority to create it, since whoever could
mint a role's keys can hardly be kept from reading them. A delivery is
addressed key material and is not reachable by naming it at all: only its
parties, or a grant joining the reader to that recipient and covering the
delivered role. Recipient access survives role revocation, because the key was
already delivered.

Nothing here has an anonymous route, since control records are unpublished.

### Current audience

A role may hold several valid audiences at once — rotation, or two writers —
so collection surfaces project one current audience per
`{protocol, rolePath, contextId}`. Selection prefers a real tenant signature,
then the oldest creation, then the lowest record id. Oldest rather than newest
is deliberate: it makes a later flood of non-tenant audiences inert instead of
letting the most recent writer take over a role. An author-delegated tenant
mint and an owner countersignature get no tenant priority, which is what stops
a delegate installing a current key the tenant never signed for.

Superseded audiences remain valid delivery references. A caller that names a
record by id, or pins the whole four-field identity, is asking for a
particular stored key and receives it rather than whichever is current.

### Repair after configuration change

Accepting a configuration re-examines the control records it governs, because
the same record can mean something different under a history learned later.
Only a contradiction the configuration itself owns licenses removal: an
invalid role, a governing seal-key mismatch, missing action rules, a
disallowed static action. Everything undetermined — an unavailable store, a
payload that will not parse, a configuration that has not arrived — is
retained. The asymmetry is deliberate: a record wrongly kept can be removed
later, while one wrongly destroyed is custody material nobody can reconstruct.

The newest configuration is asked only whether the role still exists, and
deliberately not whether it still carries `$keyAgreement`. Dropping a key
agreement stops new material being minted; it does not invalidate material
already sealed under it.

Replaying whether a retained record was ever admissible consults nothing
mutable. A record standing on its writer's own position — countersigned by the
owner, authored by the tenant, signed by a delegate, or invoking a grant — is
preserved without re-fetching that grant or re-resolving that DID, because
their absence today says nothing about what was authorized then.

## Grant-key delivery records

Separately-identified clients and agents receive decryption keys through two
immutable record types under the fixed core protocol
`https://identity.foundation/dwn/protocols/encryption`, which is resolved by
lookup precedence and never installed: `grantKey` carries an encrypted
(`encryptionRequired`) payload the node never decrypts, and `wrappedGrantKey`
carries a plaintext wrapped envelope validated against the vendored
`wrapped-grant-key-envelope.json` schema. Both are created by anyone, readable
only by the delivery recipient, tagged with `grantId`, `protocol`, `keyId`
(43-character base64url thumbprint shape) and optional `protocolPath`, and
limited to 30,000 inline bytes.

Admission checks a delivery at its signed timestamp: representation, tags,
the referenced grant, grant activity (`dateGranted <= messageTimestamp <
dateExpires`, revoked only when the oldest revocation is at or before that
timestamp), grantor authorship, grantee recipientship, and directional scope
coverage, re-checked against the historical configuration when role evidence
is needed. A delivery without a data stream is retained but not validated and
never becomes latest state. Admission errors carry stable identities, with
missing grants and missing history kept distinct from scope denial so
dependency repair can retry.

Coverage (`ENBOX-ENC-003`) is directional: a protocol-wide Read grant covers
the protocol key and every path; a path Read grant covers its subtree plus
keyed local roles its subtree reads through; Write grants cover only keyed
local roles, restricted to the grant subtree when path-scoped. A path-scoped
grant never covers a protocol-scoped key.

Resolution re-checks at the current time before a key is used: current grant
activity, any revocation, tag and payload agreement (including an absent
`protocolPath` on both sides), coverage under the current configuration,
target coverage, the scope-derived derivation path, and the public and
derived-public thumbprints against the delivered key id. Expiry or revocation
refuses the key without deleting the admitted delivery, and already-held keys
are never erased (`DWN-ENC-003`).

## RecordsWrite binding

The author signature commits to `encryptionCid`, preventing substitution of the
top-level encryption object after signing. Record admission can validate the
encryption envelope structurally without possessing recipient private keys or
plaintext.

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

The DWN draft encryption-control vocabulary and current TypeScript Enbox have
evolved differently. Implementation work should follow the explicit parity
decision rather than silently mixing draft `audienceEpoch` terminology with
`$encryption/audience` / `$encryption/delivery` and grant-key behaviour.

`dwn-spec#64` tracks broader encryption design questions.
`enbox-rust-core#191` owns current parity.

## Remaining work

The control-record lifecycle, audience and delivery management, read
visibility, current-audience projection and configuration repair are settled
across both implementations. What remains is system-level:

- grant-key / wrapped-key delivery records,
- key-agreement recipient selection from resolved DID documents,
- replication/dependency closure for encryption control,
- encryption-domain fingerprint contribution,
- cross-protocol audience resolution.

## Coding-agent rule

Treat cryptographic primitives and key-distribution policy as separate layers.
A successful AES/X25519 round trip is not evidence that DWN encryption
authorization, lifecycle, rotation or replication semantics are correct.
