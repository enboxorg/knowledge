---
domain: enbox
kind: implementation
repositories:
  - enboxorg/enbox
  - enboxorg/enbox-rust-core
upstream-baseline: c63bf424ac0997583db825e8a5fddf1507d30c40
reviewed: 2026-08-28
related-issues:
  - enbox-rust-core#189
  - enbox-rust-core#190
  - enbox-rust-core#245
---

# Records Admission and Lifecycle

## Current Rust pipeline

The Rust `RecordsWrite` handler performs integrity, referential, authorization, lifecycle, data and store work in one handler-oriented flow. Important checks include:

- authorization signature validation,
- RecordsWrite integrity and record/context identity,
- parent/protocol referential integrity,
- tenant/grant/protocol/delegated authorization,
- immutable-field validation for updates,
- newest-message comparison,
- terminal delete handling,
- data CID/size validation,
- protocol preprocess/postprocess hooks,
- index construction and durable storage.

## Current TypeScript reference

Current TypeScript has moved more of the latest-state transition into store-owned atomic operations. Its storage controller computes one state transition containing the new put, retained writes that must be reindexed, and displaced messages that must be removed.

The key invariant is:

```text
handler decides the valid transition
store commits the transition atomically
```

not a sequence of independently visible mutations.

## Convergence gap

Current Rust still needs the TypeScript delete-wins tombstone lattice. Generic timestamp/CID ordering is insufficient because a later-arriving older delete can lose on one replica while a write arriving after a delete is rejected on another.

The required invariant is:

```text
same valid message set
+ any arrival permutation
-> same retained/visible Record state
```

Tracked by `enbox-rust-core#189`.

## Visibility gap

Physical retained state and application-visible state are separate concerns. Current TypeScript routes Records Read/Query/Count/Subscribe through a shared visibility model including read-time record limits, context boundaries, published selection and initial-write attachment. Rust alignment landed under `enbox-rust-core#190` (PR #262) and is pinned by `ENBOX-REC-002` and `DWN-REC-007`.

### Read-time record-limit occupancy (`ENBOX-REC-002`)

For one concrete protocol path, matching latest live writes partition by direct-parent group (records without a parent form the root group; an explicitly selected parent list spans only those groups). Each group ranks by `dateCreated` ascending then `recordId` ascending and admits the first `max` before caller filters, sort, and pagination; counts run over the same admitted set. Message CID and update timestamps do not participate. A missing protocol definition or absent rule means no restriction; any other resolution or projection failure is an error, never unrestricted visibility.

This is explicitly *not* the draft's admission-time `reject`/`purgeOldest` strategy; see `decisions/0005-read-time-record-limit-occupancy.md` for the recorded divergence.

### Nested-scope selection

`protocolPath` matches exactly. `contextId = X` matches only `X` or `X + "/" + suffix`, never a sibling sharing a lexical prefix. Collection filters over a nested protocol path must pin a direct parent (`parentId`), the target path, or an ancestor context; only an explicitly bounded Subscribe initial page may omit that scope. Outstanding `$recordLimit` policy derivation follows the same scoping: root paths carry no scope, `parentId` passes through, and a `contextId` at target depth contributes its direct parent while deeper selections scope the subtree itself.

## Exact replay

Current TypeScript recognizes an already-retained exact message CID before mutable admission state can reject historical replay. This matters for protocol-role and other mutable authorization context. Historical grant revocation is different: grant authorization evaluates against the signed message time and is not retroactively revoked.

## Attestation

Rust already contains attestation payload/binding/query surfaces, but complete verification/index parity is being audited under `#245`. Do not assume attester filters are trustworthy until the attestation signatures and descriptor commitment are known to have been verified and indexed.

## Agent checklist

When modifying Records admission, test at least:

- direct vs replicated admission,
- every relevant arrival permutation,
- exact duplicate replay,
- delete/write competition,
- crash/reopen around the state transition,
- visibility through Read/Query/Count/Subscribe.