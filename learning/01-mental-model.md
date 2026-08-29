---
domain: learning
kind: guide
reviewed: 2026-08-28
---

# 01 — Mental Model

## Read first

- `dwn/foundations.md`
- `dwn/identity-and-signatures.md`
- `glossary.md`

## Core model

A DWN is not primarily a mutable row store. It receives signed messages that describe operations, validates them, retains the messages required by protocol/state rules, and derives logical Record state from those accepted messages.

Keep these layers separate:

```text
identity / signing authority
        ↓
signed DWN message
        ↓
admission and authorization
        ↓
retained messages
        ↓
derived logical Record state
        ↓
reads / queries / replication
```

A message and a Record are therefore not interchangeable concepts. A Record can have multiple accepted writes over its lifetime, while each write remains a distinct signed message.

## Identity roles

Do not collapse these terms:

- **tenant** — whose DWN is processing the message;
- **Signer** — DID whose key produced the signature;
- **Author** — semantic principal on whose authority the operation acts;
- **recipient** — application-level recipient encoded by the Record;
- **delegate/grantee** — principal exercising bounded authority granted by another principal.

Delegation is the clearest reason Signer and Author must remain separate.

## Checkpoint

You should be able to answer:

1. Why can two DWNs retain the same messages but receive them in different orders?
2. Why is a Record not simply the last message received for a `recordId`?
3. Why is signature validity necessary but insufficient for admission?
4. How can Signer and Author differ without falsifying the signature?

## Exercise

Alice delegates bounded RecordsWrite authority to an agent DID. The agent signs a write that acts semantically as Alice.

Describe, separately:

- who signs;
- who is Author;
- what must be verified cryptographically;
- what must be verified semantically;
- why storing only `signer == author` would break the model.

Then identify the relevant invariants in `invariants/authorization.json`.