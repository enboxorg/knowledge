---
domain: implementation
kind: guide
reviewed: 2026-08-28
---

# Message Processing Pipeline

A DWN engine should make admission stages explicit enough that validation order and failure classes are reviewable.

A useful conceptual pipeline is:

```text
parse / decode
→ message-kind recognition
→ structural/schema validation
→ content-addressed integrity checks
→ signature verification / identity resolution
→ referential dependency resolution
→ semantic authorization
→ state-relative validation
→ deterministic state transition decision
→ atomic persistence
→ durable replication-feed publication
```

The exact function boundaries may differ. The semantic ordering must not create acceptance results that depend on incidental storage state or delivery path.

## Requirements

- Direct, replicated, forwarded, and replayed messages use the same state-aware admission semantics.
- Cryptographic validation is distinct from semantic authorization.
- Dependency absence is distinguishable from invalidity where repair is possible.
- Record winner selection is deterministic and not based on arrival order.
- Persistence must not expose a new logical state without its corresponding durable replication history.
- Exact duplicate handling must be idempotent and must not mutate unrelated state.

## Review questions

For every handler ask:

1. What fields are integrity-bound?
2. Which dependencies must already be available?
3. Which authorization state is historical versus current?
4. What existing state can affect admission?
5. What is the deterministic conflict rule?
6. Which writes must be committed atomically?

See `dwn/foundations.md`, `dwn/authorization.md`, `dwn/distributed-semantics.md`, and `implementation/storage-contracts.md`.
