# Building on DWNs

This section is practical design guidance for people building applications and protocols on top of DWNs.

It is **not** a fourth source of normative truth. Builder guidance synthesizes the invariants in `dwn/`, the implementation realities in `enbox/`, and accepted decisions in `decisions/` into application-design advice.

Use these pages when the question is not only "what does the DWN model mean?" but "how should I model this product?"

## Start here

1. [`getting-started.md`](getting-started.md)
2. [`designing-a-protocol.md`](designing-a-protocol.md)
3. [`data-modeling.md`](data-modeling.md)
4. [`authorization-patterns.md`](authorization-patterns.md)
5. [`roles-and-membership.md`](roles-and-membership.md)
6. [`querying-and-indexing.md`](querying-and-indexing.md)
7. [`sharing-and-delegation.md`](sharing-and-delegation.md)
8. [`encryption-patterns.md`](encryption-patterns.md)
9. [`sync-and-offline.md`](sync-and-offline.md)
10. [`schema-evolution.md`](schema-evolution.md)
11. [`testing-and-failure-modes.md`](testing-and-failure-modes.md)

## Builder rule of thumb

Design from **authority and lifecycle** first, then data shape.

Before writing a protocol definition, answer:

- Who creates each kind of Record?
- Who may read/update/delete it?
- Which authority is contextual, delegated, or role-based?
- What survives membership/revocation changes?
- Which data must be queryable without fetching payloads?
- Which metadata is acceptable to expose?
- How should offline replicas converge after different arrival orders?

If those answers are unclear, the protocol structure is not ready.