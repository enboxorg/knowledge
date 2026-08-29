---
domain: enbox
kind: implementation
repositories:
  - enboxorg/enbox
  - enboxorg/enbox-rust-core
upstream-baseline: c63bf424ac0997583db825e8a5fddf1507d30c40
reviewed: 2026-08-28
related-issues:
  - enbox-rust-core#186
  - enbox-rust-core#177
  - enbox-rust-core#213
---

# Authorization Implementation

## Effective principal model

Rust's `AuthorizationContext` separates:

- `signer`: the DID/key that produced the cryptographic signature,
- `author`: the semantic principal whose authority is being exercised,
- signed payload commitments,
- invoked Permission Grant,
- optional author-delegated grant.

Without delegation, Author and Signer are the same. With author delegation, the delegate signs while the grantor remains the semantic Author.

This distinction must survive all protocol actor checks.

## Authorization cascade

The Records authorization path is effectively:

```text
validate signature
    |
    +--> delegated-author resolution, if present
    |
    +--> tenant-owner authority
    |
    +--> invoked Permission Grant
    |
    `--> Protocol authorization
```

A successful earlier branch establishes authority for the operation; cryptographic validity alone is never authorization.

## Delegated grants

The embedded delegated grant is itself a signed DWN capability artifact. Rust binds it by CID in the outer signed payload and verifies the embedded grant signature without recursively allowing unbounded delegation.

The important result is:

```text
Signer = delegate
Author = grantor
```

Protocol rules such as `who: author` therefore evaluate against the effective Author rather than the raw signing key.

## Permission Grant time semantics

Ordinary message admission evaluates the grant against the incoming message's signed timestamp, including grant start/expiry and revocation-as-of that time.

A later revocation does not retroactively invalidate an already-valid historical operation. Live disclosure/subscription authorization is different and may be re-evaluated against current time/state.

## Protocol actions

Protocol authorization derives actions from operation type and Record authorship. Updates and deletes by the original semantic Author differ from co-update/co-delete operations by another principal.

Role-based authorization is live state: a role record must currently satisfy the role/path/context requirements when a new operation invokes it.

## Implementation caution

Do not collapse authorization into a generic `is_signed_by(DID)` helper. Any refactor must preserve:

- Signer vs Author,
- delegated grant binding,
- historical grant-time checks,
- current role/protocol state,
- Records scope/path/context conditions.

Rust typing/refactoring work is tracked separately from semantic parity so architecture cleanup does not silently change capability behavior.