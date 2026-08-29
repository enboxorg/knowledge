---
domain: conformance
kind: guide
reviewed: 2026-08-28
---

# DWN Conformance Checklists

These checklists translate DWN semantics into observable behaviours suitable for implementation test plans.

They are not a replacement for the specification. Each checklist should be read with the relevant page under `dwn/` and the current spec.

## Areas

- `records.md`
- `protocols-and-authorization.md`
- `permissions.md`
- `queries-and-visibility.md`
- `replication.md`
- `encryption.md`
- `identity-attestation-topology.md`

## How to use

For each item, maintain one or more canonical fixtures and assert the same outcome across implementations. Where current Enbox intentionally differs from the draft, label the fixture as implementation-parity rather than normative conformance and link the divergence issue.

Conformance should focus on externally visible behaviour, deterministic state, and stable error classes—not matching internal APIs or storage layouts.
