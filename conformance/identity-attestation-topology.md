---
domain: conformance
kind: guide
reviewed: 2026-08-28
---

# Identity, Attestation, and Topology Conformance

Use with `dwn/identity-and-signatures.md`, `dwn/attestations.md`, and `dwn/topology.md`.

## DID/signature verification

- [ ] Supported DID methods resolve to usable verification material.
- [ ] `kid` must resolve to the intended verification method/controller relationship.
- [ ] Invalid signature, wrong `kid`, and mismatched DID are rejected.
- [ ] DID resolution failures are distinguishable from invalid signatures.
- [ ] Historical-message verification behaviour is tested according to the targeted contract; unresolved mutable-key history is not silently treated as current-key success.

## Attestation

- [ ] Attestation payload is bound to the intended descriptor/message.
- [ ] Invalid attester signatures are rejected.
- [ ] Multiple attesters are handled deterministically where supported.
- [ ] Query by attester returns only matching Records/messages.
- [ ] Updated Records do not accidentally inherit stale attestation semantics unless the targeted contract says they should.

## Endpoint/topology

- [ ] DID service endpoint discovery handles multiple endpoints deterministically.
- [ ] Unresolvable endpoints are skipped/fail according to the targeted contract without corrupting state.
- [ ] DID-as-Service-Endpoint recursion/depth behaviour is tested where supported.
- [ ] Failover between endpoints does not change message semantics or bypass admission.
- [ ] Replicas behind different endpoints converge on the same admissible message set.
