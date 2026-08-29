# Architecture Decisions

Use this directory for durable architecture decisions that are not simply restatements of the DWN specification or current implementation.

A decision should capture:

- context and problem,
- decision,
- consequences,
- alternatives considered,
- links to relevant spec sections, implementation PRs, and issues,
- whether the decision intentionally diverges from the draft or current TypeScript Enbox.

Prefer focused ADR-style documents over broad design essays.

## Accepted decisions

- [ADR 0001: Separate Spec, TypeScript Reference, Rust Implementation, and Decisions](0001-source-hierarchy.md)
- [ADR 0002: Durable Message Feed Is the Authoritative Replication Substrate](0002-durable-feed-replication.md)
- [ADR 0003: Replication Reuses Normal DWN Admission](0003-unified-admission.md)
- [ADR 0004: Latest Record State Transitions Are Store-Owned and Atomic](0004-store-owned-record-transitions.md)

## Lifecycle

Do not rewrite an accepted ADR to make history look cleaner. If a decision changes, mark the old ADR superseded and link to the replacement.

Knowledge provenance and review-date policy lives in [`maintenance/freshness.md`](../maintenance/freshness.md).
