# ADR 0002: Durable Message Feed Is the Authoritative Replication Substrate

- Status: Accepted
- Date: 2026-08-28

## Context

Current Enbox replication no longer treats `MessagesSync`, `StateIndex`, or sparse Merkle roots as the parity architecture. Replication is driven from a durable message feed exposed through `MessagesQuery`, with `MessagesSubscribe` used as a low-latency wake/notification layer.

Rust already has a durable feed substrate and a read-only EventLog adapter over it. The remaining work is agent/reconciliation migration and removal of the legacy path.

## Decision

Use the durable retained-message feed as the single authoritative replication substrate.

- `MessagesQuery` is the durable catch-up and reconciliation interface.
- `MessagesSubscribe` may reduce latency, but must not become a second authoritative delivery/progress path.
- EventLog-style subscription adapters read from the same durable feed; they are not a second persisted history.
- Progress is checkpointed from durable feed cursors/tokens after admission work settles.
- `MessagesSync`, `StateIndex`, and SMT reconciliation are legacy compatibility/migration surfaces and must not be reintroduced as current architecture.

## Consequences

- Lost or coalesced subscription wakes do not lose replicated messages.
- Restart recovery comes from durable checkpoints rather than transient event delivery.
- Sync, replay, and live catch-up share the same retained-message source of truth.
- Durable feed semantics and Records retained-state semantics must be updated atomically enough that replication cannot observe contradictory state.

## Related

- `enbox-rust-core#187` — durable feed and `MessagesQuery`
- `enbox-rust-core#188` — migrate reconciliation to durable feeds
- `enbox-rust-core#192` — live sync/subscription lifecycle
- `enbox-rust-core#211` — remove legacy sync state
- `dwn-spec#67` — live-sync spec divergence
