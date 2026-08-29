---
domain: enbox
kind: implementation
repositories:
  - enboxorg/enbox
  - enboxorg/enbox-rust-core
upstream-baseline: c63bf424ac0997583db825e8a5fddf1507d30c40
reviewed: 2026-08-28
---

# Package Map

## TypeScript reference

Relevant current Enbox packages include:

- `@enbox/dwn-sdk-js`: DWN interfaces, handlers, authorization, storage controller, encryption control, schemas.
- `@enbox/agent`: identity/runtime state, durable-feed sync orchestration, endpoint resolution, sessions and caches.
- `@enbox/dwn-clients`: JSON-RPC/HTTP/WS client framing and transport behaviour.
- `@enbox/dwn-server`: server transport, replicated apply, subscriptions, delivery service and rate limiting.
- `@enbox/protocols`: standard protocol definitions consumed by agent/runtime features.
- `@enbox/connect`, `@enbox/auth`, `@enbox/dids`, `@enbox/local-node`: adjacent identity/session/discovery surfaces.

## Rust workspace

`enbox-rust-core` is split roughly into:

```text
crates/
  dwn-rs-core/
    auth/
    dwn/
    encryption/
    events/
    filters/
    handlers/
    identity/
    interfaces/
    permissions/
    runtime/
    stores/
    sync/

  dwn-rs-stores/
    sqlite-backed stores
    native node assembly

  dwn-rs-remote/
    legacy/remote transport pieces

  enbox-ffi/
    native/mobile bindings
```

The core handlers are grouped by interface:

```text
handlers/
  messages/
  protocols/
  records/
```

## Important ownership boundaries

- `handlers/records/common.rs` currently carries substantial shared Records validation/admission logic.
- `permissions/mod.rs` carries a large portion of Permission Grant authorization.
- store traits live in core; SQLite implementations live in `dwn-rs-stores`.
- durable feed ownership belongs to the message store; the event-log adapter observes that feed rather than maintaining a second authoritative history.
- sync orchestration should move toward the durable-feed model owned by `MessagesQuery`/`MessagesSubscribe`, not legacy `MessagesSync`/`StateIndex`.

## Refactoring caution

Large modules are a maintainability concern, but behavioural parity and conformance tests should be pinned first. Refactors should preserve the same externally observable invariants rather than combine structural cleanup with protocol changes.