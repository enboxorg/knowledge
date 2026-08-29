---
domain: examples
kind: guide
reviewed: 2026-08-28
---

# Worked Example: Attested Profile

## Goal

Model a user-controlled profile Record that can be endorsed by independent third parties without giving those third parties ownership of the profile itself.

This example focuses on DWN attestations: signatures that bind third-party endorsement to a specific RecordsWrite version.

## Actors

- **Profile owner** — creates and updates the profile.
- **Attester** — independently signs an attestation over a specific RecordsWrite descriptor.
- **Reader** — queries the profile and may require one or more trusted attesters before accepting a claim.

Assume Alice owns a profile and Acme University attests one version of it.

## Domain model

```text
profile
```

The attestation is attached to a RecordsWrite version; it is not modeled as a child Record merely to represent endorsement.

Example profile payload:

```json
{
  "displayName": "Alice Example",
  "credential": {
    "type": "alumni",
    "institution": "Acme University",
    "graduationYear": 2020
  }
}
```

## Trust model

An attestation proves something like:

```text
Attester X signed the descriptor commitment for this specific write.
```

It does **not** automatically prove that the attester is trustworthy for the application's business purpose.

The reader still needs a trust policy, for example:

```text
accept alumni claim only if attester DID is in trusted-universities set
```

That trust policy is application logic, not something a generic DWN node can infer.

## Authorization matrix

| Operation | Profile owner | Attester | Reader |
|---|---:|---:|---:|
| Create profile | yes | no | no |
| Update profile | yes | no | no |
| Delete profile | yes | no | no |
| Sign attestation for a write | no special DWN ownership required; attester signs independently | yes | no |
| Query by attester | yes if authorized to query/read | n/a | depends on access policy |

The attester does not gain update authority over the Record simply because it attests one write.

## Protocol shape

```text
profile
```

Protocol URI:

```text
https://example.com/protocols/attested-profile
```

Illustrative protocol definition:

```json
{
  "protocol": "https://example.com/protocols/attested-profile",
  "published": false,
  "types": {
    "profile": {
      "schema": "https://example.com/schemas/profile",
      "dataFormats": ["application/json"]
    }
  },
  "structure": {
    "profile": {
      "$actions": [
        { "who": "author", "can": ["create", "read", "update", "delete"] }
      ]
    }
  }
}
```

Whether readers other than the owner can read the profile depends on the intended product. Public or recipient/role-based visibility can be layered on separately.

## Attestation lifecycle

### 1. Alice prepares RecordsWrite W1

W1 contains the descriptor for profile version 1.

The descriptor is content-addressed by `descriptorCid`.

### 2. Acme University signs an attestation

Conceptually:

```text
attestation payload -> commits to W1 descriptorCid
attestation JWS     -> signed by Acme University's DID key
```

Multiple attesters may sign within the supported General JWS structure.

### 3. Alice's RecordsWrite binds the attestation object

The RecordsWrite authorization commits to `attestationCid`, preventing an attacker from substituting a different attestation object without invalidating Alice's signed write authorization.

The binding chain is conceptually:

```text
Alice authorization
  -> attestationCid
     -> attestation object
        -> attester signature(s)
           -> descriptorCid
              -> W1 descriptor
```

Every link matters.

## Why attestation is version-specific

Suppose Alice later changes the profile:

```text
W1: graduationYear = 2020   [attested by Acme]
W2: graduationYear = 2018   [not attested]
```

The attestation over W1 must not silently carry forward to W2.

An attestation says the attester endorsed the specific signed descriptor commitment, not the eternal logical `recordId` irrespective of future contents.

If Acme wants to endorse W2, it must produce a new valid attestation for W2.

## Query patterns

A reader may want:

```text
profiles attested by did:example:acme-university
```

The implementation must derive/index attester identities from **verified** signatures, not from untrusted user-provided metadata.

A query result matching `attester = Acme` should therefore mean the retained write has a valid attestation signature attributable to Acme under the implemented semantics.

## Multi-attester case

Suppose a professional profile requires two independent endorsements:

- university attests education,
- licensing body attests licence status.

A single General JWS attestation object may contain multiple signatures when supported by the current protocol/runtime.

The application must decide whether it requires:

```text
any trusted attester
all required attesters
N-of-M trusted attesters
```

DWN signature validity and application trust policy remain separate.

## DID rotation problem

Years later, Acme rotates the key used for the original attestation.

A replica receiving W1 for the first time still needs a way to verify the historical signature. This is a known specification-level concern: current-DID-state resolution alone may not be sufficient when old verification methods disappear.

Do not hide this issue in the application layer. See the tracked historical DID verification work in `enboxorg/dwn-spec#66`.

## Offline and replication behavior

A replica may receive:

```text
W1 + attestation
```

long after the original admission.

Normal admission should verify:

- Alice's authorization signature,
- descriptor commitments,
- `attestationCid` binding,
- each attestation signature,
- the attestation payload's descriptor commitment,
- protocol/schema authorization.

Replication does not turn an attestation into trusted data merely because another DWN previously accepted it.

## Failure cases

### Invalid attester signature

Reject the attested write according to the protocol's attestation validation requirements; do not index the claimed attester.

### Attestation commits to different descriptor

Reject.

### Valid attestation object substituted after Alice signs

Alice's `attestationCid` commitment must prevent this.

### Old attestation copied to new write

Reject or treat the new write as unattested unless it contains an independently valid attestation committing to the new descriptor.

### Unknown but cryptographically valid attester

The DWN may accept the cryptographic structure, while the application can still decline to trust the attester for business purposes.

### Multiple signatures, one invalid

Follow the exact current attestation validation semantics; do not invent partial-validity policy at query time. Tests should establish parity across implementations.

## Privacy considerations

Attester identity is queryable metadata in many designs and can reveal relationships:

```text
"this profile was endorsed by organisation X"
```

Do not assume attestations are private simply because payload data is encrypted. Metadata exposure should be part of protocol design.

## Protocol/schema evolution

If the profile schema changes materially, an old attestation remains evidence about the old version it actually signed.

Do not transform old endorsements into endorsements of semantically different fields during migration.

A migration process may:

1. create a new profile version,
2. request fresh attestations,
3. preserve old attested versions for audit/history if product policy requires it.

## Test plan

```text
[ ] owner can create W1 with one valid attestation
[ ] invalid attestation signature is rejected
[ ] descriptor commitment mismatch is rejected
[ ] attestation substitution breaks attestationCid binding
[ ] query by verified attester returns W1
[ ] unverified claimed attester cannot match query
[ ] multiple attester signatures are handled according to current semantics
[ ] W1 attestation does not carry forward to W2
[ ] replicated W1 re-verifies through normal admission
[ ] historical DID/key-rotation behavior is explicitly tested/documented
[ ] application trust policy can reject a cryptographically valid untrusted attester
```

## What this example teaches

- Attestation is third-party endorsement, not ownership delegation.
- Attestations bind to a specific RecordsWrite version.
- `attestationCid` prevents substitution of the attestation object.
- Cryptographic validity and application trust are separate decisions.
- Historical DID verification is a durability concern for long-lived attestations.
