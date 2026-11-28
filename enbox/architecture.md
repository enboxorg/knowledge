---
domain: enbox
kind: implementation
repositories:
  - enboxorg/enbox
  - enboxorg/enbox-rust-core
upstream-baseline: 1d02b19555f256ecb9f7df5a47048425c549a6d7
reviewed: 2026-11-28
---

# Enbox Architecture

## Source hierarchy

For implementation work, keep three layers separate:

1. the DWN draft defines intended protocol semantics,
2. current TypeScript Enbox is the behavioural parity target for `enbox-rust-core` where the project explicitly chooses upstream behaviour,
3. Rust is the active implementation being aligned and hardened.

Do not collapse a known draft/upstream divergence into a single statement.

## Runtime shape

The Rust core is organized around typed DWN handlers, stores, identity/signature verification, authorization, encryption, and replication primitives. The TypeScript monorepo contains the more mature agent/runtime orchestration and remains the reference for current behavioural parity.

A useful processing map is:

```text
wire message
    |
    v
DWN dispatch / schema validation
    |
    v
typed handler
    |
    +--> integrity / signature / authorization
    +--> protocol and lifecycle validation
    +--> data handling
    |
    v
store-owned durable state
    |
    +--> query indexes
    +--> durable replication feed
    +--> resumable maintenance
```

Replication feeds messages back through the same admission semantics rather than bypassing handlers with database copies.

## Major implementation boundaries

- **DWN engine**: message parsing, validation, authorization, Records/Modules/Messages handlers (using `Modules` wire vocabulary and `application/vnd.enbox.dwn-rpc` single HTTP body framing as `enbox-parity`; see `decisions/0010-protocols-to-modules-parity.md`).
- **Stores**: durable messages, data, feed metadata, resumable tasks.
- **Identity/signatures**: DID resolution and JWS verification.
- **Agent/runtime**: link planning, sync orchestration, session state, remote transport. Rust owner: `dwn-rs-agent` (agent identity/vault, `auth` registration/connect); reference: `@enbox/agent` with `@enbox/auth` above it.
- **Encryption control**: record envelope primitives plus higher-level key-distribution/control records.
- **Transport/topology**: JSON-RPC/HTTP/WS, endpoint discovery, forwarding, proxying.

## Current cross-cutting priorities

The most important remaining Rust work is concentrated in distributed invariants rather than basic type coverage:

- conformance evidence and follow-through for the implemented delete-wins Records and atomic latest-state contract (`enbox-rust-core#189`),
- one consistent Records visibility model (`#190`),
- durable-feed replication using `MessagesQuery` and `MessagesSubscribe` (`#187`, `#188`, `#192`),
- current encryption-control/key-delivery lifecycle (`#191`),
- crash/reopen evidence for durable stores (`#169`).

## Coding-agent rule

Before changing a DWN behaviour, identify whether the relevant statement is:

- normative draft semantics,
- current TypeScript behaviour,
- current Rust behaviour,
- or an intentional divergence tracked by an issue.

Then make the change against the correct authority.
