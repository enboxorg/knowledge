---
domain: dwn
kind: normative
spec: https://dwn-spec.pages.dev/
spec-reviewed: 2026-08-28
---

# Attestations

## Core model

A RecordsWrite may carry an attestation: a third-party signature over the write's descriptor commitment.

An attestation is an endorsement of that specific write version. It is not authorization to create the Record and does not replace the author's authorization signature.

## Binding

The write author binds the attestation object through `attestationCid` in the RecordsWrite authorization payload.

The attester signs a payload that commits to the RecordsWrite descriptor. Together these commitments prevent an attacker from substituting an unrelated attestation without invalidating either the attester's signature or the author's binding.

## Multiple attesters

Attestation uses General JWS semantics, so one attestation object can contain multiple signatures. Each valid signature identifies an attester that may be indexed for query.

Implementations should derive attester identity only from verified signatures.

## Version semantics

Attestation is write-version specific:

```text
attestation over Write W1
    !=
attestation over later Write W2
```

Updating a Record does not imply that earlier attesters endorse the new descriptor or data commitment.

## Querying

Records query filters may select Records by attester. Such a filter should match verified attestation state associated with the returned write version, not unverified metadata.

## Encrypted records

An attester signs the descriptor commitment, including the Record's data CID/size commitments, but this does not necessarily imply that the attester saw or understood the plaintext. For encrypted Records, attestation and plaintext knowledge are distinct claims unless an application protocol defines additional semantics.

## Trust boundary

Attestation answers a narrow question:

```text
Did this third party cryptographically endorse this RecordsWrite descriptor?
```

It does not by itself answer whether the Record is true, whether the attester is trusted by the application, or whether the operation was authorized.

## Common traps

- Do not treat attestation as RecordsWrite authorization.
- Do not carry an old attestation forward to later updates.
- Do not index an attester before verifying the signature and descriptor commitment.
- Do not infer plaintext knowledge from attestation of an encrypted write.
