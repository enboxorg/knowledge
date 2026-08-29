---
domain: conformance
kind: guide
reviewed: 2026-08-28
---

# Protocols and Authorization Conformance

Use with `dwn/protocols.md` and `dwn/authorization.md`.

## Protocol definitions

- [ ] Protocol definition schema is validated.
- [ ] Structure paths and rule sets are resolved deterministically.
- [ ] Record writes must match the declared protocol/path structure.
- [ ] Cross-context parent/path violations are rejected.
- [ ] Unsupported or malformed protocol definitions do not become active authorization policy.

## Actor semantics

- [ ] Signer and semantic Author are distinguished when delegation is present.
- [ ] Tenant authority is checked independently from signature validity.
- [ ] Recipient-based rules apply to the intended Record relationship.
- [ ] Role-based rules require valid role state in the correct scope/context.
- [ ] Cross-protocol actor references obey their declared constraints.

## Time and mutable state

- [ ] Historical authorization uses the intended operation timestamp semantics.
- [ ] Later grant revocation does not retroactively invalidate earlier valid admission where the contract is historical.
- [ ] Live/current disclosure paths re-evaluate continuing authority where required.
- [ ] Exact replay does not accidentally become invalid solely because mutable unrelated authorization state changed after original acceptance, where idempotent replay is the intended contract.

## Negative cases

- [ ] Valid signature without authorization is rejected.
- [ ] Wrong protocol path is rejected.
- [ ] Wrong context/parent is rejected.
- [ ] Role from another context does not leak authority.
- [ ] Delegation outside its scope is rejected.
