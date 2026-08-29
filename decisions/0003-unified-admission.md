# ADR 0003: Replication Reuses Normal DWN Admission

- Status: Accepted
- Date: 2026-08-28

## Context

A replicated message is still an untrusted signed operation. Copying retained database state directly between nodes would bypass signature verification, protocol authorization, Permission Grant evaluation, dependency checks, Records ordering, and current implementation invariants.

Current Enbox instead treats replication as message delivery plus dependency repair. The destination determines whether the operation can be admitted and reports structured outcomes such as applied, duplicate, superseded, incomplete, invalid, or deferred.

## Decision

Locally submitted, replayed, forwarded, and replicated DWN messages must converge on the same state-aware validation/admission semantics.

Replication orchestration may optimize ordering and fetch missing dependencies, but it must not create a privileged database-copy path that bypasses normal message processing.

Dependency closure is receiver-driven: the destination identifies missing protocol configurations, initial writes, parents/ancestors, roles, grants, encryption-control records, cross-protocol references, or record data required to evaluate the message.

## Consequences

- A peer cannot cause invalid state merely because it already stored that state itself.
- Sync correctness depends on idempotent and deterministic admission behavior.
- Dependency repair is part of replication orchestration, not an alternative authorization path.
- Direct processing and replicated processing need shared conformance tests.

## Related

- `enbox-rust-core#188` — durable-feed reconciliation and dependency closure
- `enbox-rust-core#189` — unified Records admission/latest-state semantics
- `enbox-rust-core#219` — scope-closure validation
- `enbox-rust-core#221` — cross-protocol dependencies
