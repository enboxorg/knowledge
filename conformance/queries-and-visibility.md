---
domain: conformance
kind: guide
reviewed: 2026-09-12
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
- [ ] Live subscription delivery rechecks mutable grant/role authority and occupant status; terminal failures close the stream with a defined error.

## Unified visibility

- [ ] Read, Query, Count, and Subscribe apply the same visibility/occupancy semantics when they expose the same logical Record population.
- [ ] Any record-limit behaviour is exercised consistently across those surfaces for the targeted spec/parity contract.
- [ ] Occupancy winners are deterministic per protocol path and direct-parent group (`dateCreated`, then `recordId`), independent of insertion and replication order.
- [ ] Nested `contextId` selections cannot escape the authorized context boundary (`a/b` never matches `a/bc`).
- [ ] The encryption-control current-audience projection is the documented exception to unified visibility: the collection surfaces apply it, direct Read does not, and a fixture asserts that difference rather than reconciling it (`DWN-REC-008`, `ENBOX-ENC-004`).
- [ ] A broad Count over a population that may contain projected Records counts what Query would return, rather than counting through the store.
- [ ] Both snapshot entry points — the ordinary subscribe reply and any event-log snapshot — agree with Query at the same durable head.

## Pages versus storage pages

A reply page is not a storage page: projection and per-Record authorization
both remove candidates after the store has answered.

- [ ] A page that loses candidates to projection or authorization refills rather than coming back short, including when the whole first storage page is removed.
- [ ] Each refill requests only the capacity still unfilled, so no candidate is fetched, discarded, and left behind a cursor that has already advanced past it.
- [ ] Paging a mixed population returns every visible Record exactly once across pages, and never more than the requested limit in one page.

## Stability

- [ ] Identical retained message sets produce identical query-visible populations regardless of arrival order.
- [ ] Index rebuild/reopen reproduces the same logical results.
