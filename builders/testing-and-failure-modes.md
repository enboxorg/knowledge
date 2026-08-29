---
domain: builders
kind: guide
reviewed: 2026-08-28
---

# Testing and Failure Modes

## Test semantics, not only happy-path API calls

A DWN-backed application should prove behavior across authorization changes, replication disorder, duplicate delivery, and offline recovery.

For each protocol path, cover create/read/query/update/delete plus the actors who should be denied each operation.

## Authorization matrix tests

Turn the protocol's actor matrix into tests. Include:

- tenant/owner,
- author,
- recipient,
- each protocol role,
- grantee,
- delegate,
- unrelated DID.

Test both allowed and denied operations. Negative authorization fixtures are as important as success cases.

## Lifecycle tests

For each logical Record type, test:

- initial write,
- valid update,
- immutable-field mutation attempt,
- stale update,
- delete,
- write after delete,
- exact duplicate replay.

Application code should not depend on a stale write being accepted merely because it arrived later.

## Arrival-order permutation tests

For operations that can race, apply the same signed message set in multiple orders and assert the same final logical state.

Examples:

```text
W0 -> W2 -> W1
W0 -> W1 -> W2
```

and update/delete permutations.

This catches assumptions about server arrival order that ordinary integration tests miss.

## Offline and dependency tests

Simulate:

- missing parent/context records,
- missing grants/roles,
- delayed encryption-control records,
- stale protocol state,
- reconnect from an old checkpoint,
- lost and duplicated subscription wakes.

Distinguish retryable incomplete state from permanently invalid state.

## Revocation tests

Test the temporal boundary explicitly:

- operation valid before revocation,
- new operation after revocation rejected,
- historical admitted operation remains historical state,
- live subscriptions/current disclosure re-evaluate authority where required.

## Encryption tests

Cover authorization and decryptability separately:

- authorized + key available,
- authorized + key unavailable,
- unauthorized even if ciphertext is present,
- corrupted encryption metadata,
- member removal/rotation,
- recovered/new device obtaining historical keys where intended.

## Query consistency tests

The same visibility policy should hold across Read, Query, Count, and Subscribe. Test that a Record hidden from one discovery mechanism is not accidentally exposed through another.

## Failure categories for UX

Applications should avoid collapsing every failure into "sync failed." Useful categories include:

- authentication/signature failure,
- authorization denial,
- invalid protocol/schema state,
- missing dependency/incomplete,
- conflict/stale operation,
- unavailable endpoint/transport,
- missing decryption capability.

Preserving these distinctions makes recovery behavior far easier to design and debug.