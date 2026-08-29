# Knowledge Freshness and Drift Policy

This repository is useful only if readers can tell what source a statement came from and when it was last checked.

## Source classes

Substantive knowledge belongs to one of these classes:

- **normative** — derived from the DWN draft/spec;
- **implementation** — derived from current Enbox code/behaviour;
- **guide** — practical synthesis for learners, builders, or engine authors;
- **worked example** — an end-to-end design applying guide material to one explicit actor/authority model;
- **conformance guide** — behaviour-oriented checklist material;
- **invariant registry** — compact machine-readable assertions that preserve the source contract of the underlying rule;
- **decision** — an accepted architecture decision.

Do not merge those classes into one source of truth. Invariant IDs improve retrieval and traceability; they do not change a rule's normative status.

## Required metadata

Pages under `dwn/` use `domain: dwn`, `kind: normative`, a spec URL, and `spec-reviewed` date. Pages under `enbox/` use `domain: enbox`, `kind: implementation`, repository/baseline provenance, and `reviewed` date.

Substantive Markdown guides under `learning/`, `builders/`, `examples/`, `implementation/`, and `conformance/` use:

```yaml
---
domain: <directory>
kind: guide
reviewed: YYYY-MM-DD
---
```

Section `README.md` files are navigation documents and are exempt from guide front matter.

## Invariants

JSON files under `invariants/` must be machine-readable arrays whose entries include:

- unique stable `id`;
- non-empty `statement`;
- `contract` in `normative`, `enbox-parity`, or `implementation-contract`;
- non-empty `sources` list.

If the statement changes meaning, create a new ID rather than silently reusing the old one. If only provenance/status changes while the assertion remains equivalent, preserve the ID and deliberately update its contract/source links.

## When knowledge must be reviewed

Review affected material when:

1. the DWN draft changes a depended-on semantic;
2. the TypeScript parity baseline changes materially;
3. a linked parity/divergence issue closes because behaviour changed;
4. a PR changes Records ordering/retention, authorization, permissions, encryption, sync, topology, durable storage, dependency classification, or error semantics;
5. architecture named by a page is removed/replaced;
6. a guide/example/learning module depends on the changed assumption;
7. an invariant's statement, contract class, or source provenance is affected.

Update dates/baselines only after source review.

## Staleness is a signal, not proof

Old review dates should trigger rechecking before high-impact decisions. Age alone does not prove a page is wrong. Metadata CI warns on age and fails on malformed/missing provenance or malformed invariant entries.

## PR rule

A behaviour-changing Enbox PR should update affected knowledge, open/link a focused follow-up, or explicitly state why documentation/invariants are unaffected. Spec changes should similarly trigger review across dependent layers.

## Rebaseline procedure

When adopting a new TypeScript Enbox parity baseline:

1. update code/fixtures and parity evidence in `enbox-rust-core`;
2. find `enbox/` pages pinned to the previous baseline;
3. re-verify affected implementation claims;
4. update `upstream-baseline` and `reviewed` only after verification;
5. update affected `enbox-parity` invariants deliberately;
6. link new divergences to focused issues;
7. do not edit normative `dwn/` semantics merely to match TypeScript;
8. review dependent learning/builder/example/implementation/conformance guidance.