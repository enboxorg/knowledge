# ADR 0006: RecordsDelete Carries a Grant Invocation Per Current Enbox Parity

- Status: Accepted for current Enbox parity
- Date: 2026-09-12

## Context

The DWN draft requires the descriptor and author-signature-payload grant
invocation fields to match exactly, and lists `permissionGrantId` on the
Read, Query, Subscribe, Count, and Write descriptor sections — but the
Delete descriptor section omits the field. Current TypeScript Enbox carries
it on Delete uniformly: the descriptor type, the JSON schema,
`RecordsDelete.create` (which spreads the invocation into both descriptor
and payload), and the descriptor/payload cross-check all include it. Rust
previously had no Delete descriptor field at all, so every grant-bearing
Delete was rejected as a signature mismatch (`enbox-rust-core#283`).

## Decision

Rust targets current Enbox parity and accepts optional `permissionGrantId`
on RecordsDelete, keeping the descriptor/payload exact-match check
(`DWN-AUTH-008`, normative) for all direct Records methods. This is recorded
as an `enbox-parity` extension, not normative DWN behaviour: the draft text
does not document the Delete field, and this ADR must not be read as claiming
it does. `DWN-AUTH-007` (implementation-contract) already requires agreement
wherever both copies exist; after this fix its payload-only clause has no
remaining direct Records/Protocols instances, since every such descriptor now
carries the copy.

## Consequences

- Grant-authorized Deletes validate like any other direct grant invocation:
  equal descriptor/payload ids proceed to scope, lifetime, and revocation
  checks; any disagreement rejects as a signature mismatch.
- Read, Write, Query, Count, and Subscribe behaviour is unchanged; they
  already carried the field under the draft's exact-match rule.
- If the draft later documents Delete either way, revisit this ADR
  deliberately rather than silently promoting or demoting the parity rule.

## Alternatives considered

- Payload-only trust for Delete (no descriptor cross-check): rejected
  because it diverges from the parity target and drops substitution
  protection the draft's exact-match rule provides everywhere else.
- Treating the draft omission as an intentional prohibition: rejected;
  the generic exact-match rule plus uniform TypeScript behaviour reads as a
  spec omission, but that reading is recorded here rather than assumed.

## Related

- `enbox-rust-core#283` — grant invocation on Query/Count/Subscribe/Delete (PR #285)
- `DWN-AUTH-008` (normative exact-match), `DWN-AUTH-007` (invocation coverage), `DWN-AUTH-003`
- `dwn/authorization.md`, `dwn/permissions.md`, `conformance/permissions.md`
