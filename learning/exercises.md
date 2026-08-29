---
domain: learning
kind: guide
reviewed: 2026-08-28
---

# Reasoning Exercises

These exercises are deliberately scenario-based. For each answer, name the invariant that controls the result and the source class it belongs to: normative DWN, current Enbox parity behaviour, implementation contract, or builder guidance.

## 1. Duplicate delivery

A RecordsWrite has already been accepted. The exact same signed message arrives again through replication.

- What must happen to logical state?
- Should a second durable logical event be created?
- Which behaviour is externally observable?

## 2. Arrival-order convergence

Two replicas receive the same initial write, update, and terminal delete in different orders.

- Which properties must still match?
- Which arrival-order differences are allowed to remain internally?

## 3. Missing parent

A child Record arrives before its parent.

- Is the child necessarily invalid?
- How should the failure be classified for a replication engine?
- When may the source checkpoint advance?

## 4. Stale role

Bob writes while offline believing he still has a contextual role. The role was removed before the write's signed operation time.

- What should a receiving DWN do?
- Why is the source device's previous local authorization result insufficient?

## 5. Historical grant

A Permission Grant authorizes an operation at `T1`. The grant is revoked at `T2 > T1`.

- Does the revocation make the already-authorized `T1` operation invalid?
- Would a live subscription necessarily continue exposing new data after `T2`?

## 6. DID key rotation

A retained message was signed by a DID key that is no longer present in the current DID Document.

- What historical-verification question must the implementation answer?
- Why is resolving only current DID state potentially insufficient?

## 7. Authorized but undecryptable

Carol is protocol-authorized to read a Record but has not received the required key material.

- Is the authorization decision wrong?
- Which subsystem must resolve the remaining problem?

## 8. Attested update

Version V1 of a profile Record is attested by an employer. The author updates the profile to V2 without a new attestation.

- Does the V1 attestation automatically endorse V2?
- What exactly was the attester binding to?

## 9. Context isolation

Bob has a `member` role in workspace A and attempts the same member-authorized operation in workspace B.

- What should happen?
- Which Record/context relationship proves role scope?

## 10. Sync wake without pull

A client receives a `MessagesSubscribe` wake signal but crashes before running its durable query.

- How should it recover?
- Why must durable replication not depend on receiving every wake event?

## 11. Crash during latest-state transition

An implementation persists a new latest Record state but crashes before updating the durable replication feed.

- What inconsistency can result?
- Which storage invariant should prevent it?

## 12. Metadata leakage

A protocol encrypts Record data but stores `diagnosis` as a queryable plaintext tag.

- What confidentiality property has actually been achieved?
- What design change should be considered?

## 13. Delegated author versus grantee

An agent may either act semantically as Alice through author delegation or act as itself through a Permission Grant.

- How do Signer and Author differ in each case?
- Why might application attribution differ?

## 14. Protocol upgrade

Protocol configuration V2 removes an action that was allowed under V1. A historical Record signed while V1 governed arrives later through replication.

- Which configuration should govern admission?
- What history must the implementation retain/resolve?

## 15. Design exercise

Take a product you know well and model one bounded workflow as a DWN protocol. Produce only:

- context tree;
- actor matrix;
- lifecycle table;
- query plan;
- offline/revocation scenarios;
- test matrix.

Do not write protocol JSON until those artifacts are coherent.