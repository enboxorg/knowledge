# Worked DWN Protocol Examples

These examples apply the builder guidance end-to-end. They are deliberately more complete than snippets: each one starts from a product problem and works through protocol shape, actors, authorization, record hierarchy, data and tags, query patterns, lifecycle, offline behavior, failure cases, and tests.

They are **illustrative designs**, not normative protocol definitions. The DWN semantics in `dwn/` remain authoritative, and current implementation behavior belongs in `enbox/`.

## Progression

1. [`personal-notes.md`](personal-notes.md) — owner-centric data, simple lifecycle, tags, queries.
2. [`shared-document.md`](shared-document.md) — explicit recipient sharing, comments, revocation boundaries.
3. [`team-workspace.md`](team-workspace.md) — contextual roles, membership lifecycle, tasks and documents.
4. [`conversation-thread.md`](conversation-thread.md) — participant role, append-heavy messaging, offline delivery.
5. [`attested-profile.md`](attested-profile.md) — third-party attestations and version-specific endorsement.
6. [`encrypted-agent-workspace.md`](encrypted-agent-workspace.md) — encrypted collaborative data plus delegated agent authority.

## How to read an example

Each example follows roughly the same sequence:

```text
problem and actors
    -> domain model
    -> protocol tree
    -> authorization matrix
    -> illustrative protocol definition
    -> record/message walkthrough
    -> queries
    -> lifecycle and evolution
    -> offline/sync behavior
    -> security/failure analysis
    -> test plan
```

The protocol JSON is intentionally secondary. The important part is the reasoning that makes the structure and authority model coherent.
