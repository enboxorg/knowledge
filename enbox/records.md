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

Physical retained state and application-visible state are separate concerns. Current TypeScript routes Records Read/Query/Count/Subscribe through a shared visibility model including read-time record limits, context boundaries, published selection and initial-write attachment. Rust alignment is tracked by `#190`.

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