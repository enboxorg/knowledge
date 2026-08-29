---
domain: implementation
kind: guide
reviewed: 2026-08-28
---

# Conformance Testing Strategy

Conformance tests should assert externally observable DWN behaviour rather than internal class structure or database schema.

## Test dimensions

Every semantic area should include:

- valid-path fixtures,
- malformed/integrity failures,
- authorization failures,
- duplicate delivery,
- state-relative conflicts,
- different arrival orders,
- missing dependency repair,
- persistent crash/reopen where storage semantics matter,
- cross-runtime fixtures when more than one implementation exists.

## Fixture design

Prefer small canonical message sets with explicit expected outcomes. Keep signed fixtures immutable so implementations can consume exactly the same bytes/CIDs.

For distributed semantics, generate permutations of the same message set and assert convergence of:

- visible logical state,
- retained tombstones/history where normative,
- query results,
- feed-set identity/progress invariants.

## Separate suites

Useful layers are:

1. message-level validation,
2. state-machine/admission,
3. query/visibility,
4. authorization/permissions,
5. replication/dependency repair,
6. encryption/control semantics,
7. topology/endpoint behaviour.

## Reference implementations

A reference implementation is evidence, not the definition of conformance. Where the draft and a reference implementation diverge, tests should identify which contract they exercise and link the tracked divergence.

See `conformance/README.md` for checklists.
