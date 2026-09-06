# ADR 0005: Read-Time Record-Limit Occupancy Follows Current Enbox Parity

- Status: Accepted for current Enbox parity
- Date: 2026-09-06

## Context

The DWN draft describes `$recordLimit` as an admission-time strategy (`reject` or `purgeOldest`): over-limit writes are refused or displace the oldest record at write time. Current TypeScript Enbox instead admits over-limit writes and hides non-occupants at read time through a deterministic occupant projection resolved per request. Rust admission likewise does not enforce limits at write time, so following the draft text would make Rust diverge from the parity target it actually serves.

## Decision

Rust implements the current Enbox read-time occupancy model for `enbox-rust-core#190` (PR #262) and records it as `ENBOX-REC-002`, explicitly classified `enbox-parity` rather than normative DWN behaviour. The draft's admission-time strategy is not implemented and must not be inferred from the invariant ID alone.

## Consequences

- Over-limit writes admit (202) and stay invisible to Read/Query/Count/Subscribe snapshots until a reconfiguration or squash changes the occupant population.
- Occupancy policy resolves from the protocol definition governing the signed request timestamp; a missing protocol or absent rule means no restriction, while any other resolution or projection failure is an error.
- If the draft and Enbox converge later, update the contract/source references deliberately while keeping the stable ID when the statement itself remains equivalent.

## Alternatives considered

- Admission-time enforcement per the draft text: rejected because it contradicts observable upstream behaviour and would break parity with current Enbox clients.
- Collapsing the parity rule into a normative invariant: rejected; normativity belongs to the draft layer, and this ADR exists precisely to keep the distinction visible.

## Related

- `enbox-rust-core#190` — read-time visibility alignment (PR #262)
- `ENBOX-REC-002`, `DWN-REC-007`
- `enbox/records.md`, `conformance/queries-and-visibility.md`
- DWN draft `$recordLimit` (admission-time strategies)
