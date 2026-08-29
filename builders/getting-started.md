---
domain: builders
kind: guide
reviewed: 2026-08-28
---

# Getting Started Building on DWNs

## Mental model

Build against logical Records and protocol rules, not storage rows.

A useful application-level model is:

```text
protocol definition
      +
signed Records messages
      +
authorization rules
      +
query/read/sync behavior
      =
application state
```

Read `dwn/foundations.md`, `dwn/records.md`, and `dwn/protocols.md` before designing a non-trivial protocol.

## Start from actors and authority

List the actors in the product and the operations each needs. Distinguish:

- tenant/owner,
- record author,
- recipient,
- protocol role holder,
- Permission Grant grantee,
- delegated signer acting for another Author.

Do not collapse these into one generic `user` concept. The distinction determines what can be expressed safely in protocol rules.

## Decide what belongs in DWN state

Good candidates are data that benefits from signed provenance, portable ownership, protocol-governed sharing, multi-device access, or replication across DWNs.

Not every transient UI state, cache, derived aggregate, or server-internal coordination record needs to become a DWN Record.

Prefer storing durable source facts and deriving ephemeral views where practical.

## Choose a protocol boundary

Use a protocol when a set of Records shares a stable vocabulary, hierarchy, lifecycle, and authorization model.

Avoid one giant application protocol containing unrelated domains merely because one product owns them. Protocol boundaries are also evolution, authorization, and interoperability boundaries.

## Design the context tree

Sketch the Record hierarchy before writing JSON:

```text
workspace
├── membership
├── document
│   ├── revision metadata
│   └── comment
└── task
```

Ask which descendants should inherit contextual authority and which need independent roots. Context shape affects roles, grants, queries, and cross-protocol composition.

## Decide queryable metadata deliberately

Record data is not the same as indexed metadata. Put values in tags only when clients need to filter/sort on them and exposing them is acceptable.

Do not duplicate sensitive payload fields into plaintext tags merely for convenience.

## Design for offline operation from day one

Assume:

- clients can write while disconnected,
- multiple DWNs can receive the same messages in different orders,
- subscription wakes can be missed,
- dependencies may arrive after dependent messages.

If correctness depends on one server seeing operations in a particular wall-clock arrival order, the model is wrong.

## Minimum design review

Before implementation, be able to show:

1. protocol/context tree,
2. actor/authorization matrix,
3. lifecycle for each Record type,
4. query patterns,
5. sharing/encryption model,
6. offline/convergence expectations,
7. representative failure cases.

The worked examples under `examples/` should eventually serve as reference designs for this process.