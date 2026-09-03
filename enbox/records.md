---
domain: enbox
kind: implementation
repositories:
  - enboxorg/enbox
  - enboxorg/enbox-rust-core
upstream-baseline: c63bf424ac0997583db825e8a5fddf1507d30c40
reviewed: 2026-09-03
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

## Convergent winner lattice

Current TypeScript and Rust use the same delete-wins Records lattice:

1. prune delete;
2. plain delete;
3. write.

Within one class, canonical message timestamp and then message CID determine the winner. A winning delete is terminal, so neither stale nor newer writes resurrect the Record. This is current-Enbox parity (`ENBOX-REC-001`), not a claim that the stronger class ordering is normative DWN draft behaviour.

The required invariant is:

```text
same valid message set
+ any arrival permutation
-> same retained/visible Record state
```

Tracked by `enbox-rust-core#189`.

Rust implemented this ordering and store-owned atomic latest-state transitions under `enbox-rust-core#189`.

## Visibility gap

Physical retained state and application-visible state are separate concerns. Current TypeScript routes Records Read/Query/Count/Subscribe through a shared visibility model including read-time record limits, context boundaries, published selection and initial-write attachment. Rust alignment is tracked by `#190`.

## Exact replay

Current TypeScript recognizes an already-retained exact message CID before mutable admission state can reject historical replay. This matters for protocol-role and other mutable authorization context. Historical grant revocation is different: grant authorization evaluates against the signed message time and is not retroactively revoked.

Replacing the stored representation or indexes of that exact CID—for example, completing an initial write with data—preserves its durable feed identity and membership contribution (`DWN-REC-007`). It does not allocate a second logical feed event.

## Permission Records and failures

The built-in permissions protocol makes permission request, grant, and revocation Records immutable after their initial write (`ENBOX-REC-002`). A changed permission is represented by a distinct Record or the defined revocation/reissue lifecycle.

Covered admission failures expose current-Enbox structured error codes and associated information at the public reply boundary (`ENBOX-ERR-001`). Storage and unexpected internal failures remain internal classes rather than being relabeled as client validation errors.

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
