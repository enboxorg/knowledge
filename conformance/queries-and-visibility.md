---
domain: conformance
kind: guide
reviewed: 2026-08-28
---

# Queries and Visibility Conformance

Use with `dwn/queries-and-sync.md`, `dwn/records.md`, and `dwn/protocols.md`.

## Query correctness

- [ ] Filters use logical Record/message semantics rather than incidental storage layout.
- [ ] Pagination/cursor results are deterministic for the targeted contract.
- [ ] Query results do not expose superseded Record versions as current Records.
- [ ] Deleted Records follow the expected visibility rules.
- [ ] Protocol/context/path filters match only the intended scope.
- [ ] Attester, recipient, author, schema, tags, and other supported filters have positive and negative fixtures.

## Authorization and disclosure

- [ ] Query authorization is evaluated independently from write admission.
- [ ] Unauthorized callers cannot infer hidden Records through counts, pagination gaps, errors, or timing-sensitive existence checks beyond the allowed contract.
- [ ] Live subscriptions re-evaluate continuing disclosure authority where required.

## Unified visibility

- [ ] Read, Query, Count, and Subscribe apply the same visibility/occupancy semantics when they expose the same logical Record population.
- [ ] Any record-limit behaviour is exercised consistently across those surfaces for the targeted spec/upstream contract.

## Stability

- [ ] Identical retained message sets produce identical query-visible populations regardless of arrival order.
- [ ] Index rebuild/reopen reproduces the same logical results.
