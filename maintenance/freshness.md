# Knowledge Freshness and Drift Policy

This repository is useful only if readers can tell what source a statement came from and when it was last checked.

## Source classes

Substantive knowledge belongs to one of these classes:

- **normative** — derived from the DWN draft/spec;
- **implementation** — derived from current Enbox code/behaviour;
- **guide** — practical synthesis for learners, builders, engine authors, or agent workflows;
- **worked example** — an end-to-end design applying guide material to one explicit actor/authority model;
- **conformance guide** — behaviour-oriented checklist material;
- **invariant registry** — compact machine-readable assertions that preserve the source contract of the underlying rule;
- **decision** — an accepted architecture decision.

Do not merge those classes into one source of truth. Invariant IDs improve retrieval and traceability; they do not change a rule's normative status. Agent workflows define process, not protocol semantics.

## Required metadata

Pages under `dwn/` use `domain: dwn`, `kind: normative`, a spec URL, and `spec-reviewed` date. Pages under `enbox/` use `domain: enbox`, `kind: implementation`, repository/baseline provenance, and `reviewed` date.

Substantive Markdown guides under `learning/`, `builders/`, `examples/`, `implementation/`, `conformance/`, and `agents/` use:

```yaml
---
domain: <directory>
kind: guide
reviewed: YYYY-MM-DD
---
```

Section `README.md` files and files under `agents/templates/` are navigation/task templates and are exempt from guide front matter.

## Invariants

JSON files under `invariants/` must be machine-readable arrays whose entries include:

- unique stable `id`;
- non-empty `statement`;
- `contract` in `normative`, `enbox-parity`, `implementation-contract`, or `external-spec`;
- non-empty `sources` list of existing knowledge pages.

Statement changes fall into three cases:

- **rewording** — the assertion is equivalent; preserve the ID;
- **refinement** — the same rule gains or loses a condition, exception, scope limit, or ordering detail; preserve the ID and append a `revisions` entry (`date`, `previous` statement, `summary` of the change) so code citing the ID can tell its meaning moved;
- **different rule** — create a new ID rather than silently reusing the old one.

If only provenance/status changes while the assertion remains equivalent, preserve the ID and deliberately update its contract/source links.

An optional `source_notes` object maps a source path to why it is cited when that source does not itself state the invariant (for example, a draft page an `enbox-parity` invariant diverges from, or background context).

`tools/check_invariant_semantics.py` runs in CI as an advisory check. It judges whether each changed statement is a rewording, refinement, or different rule, and whether the sources of changed invariants — and of invariants citing changed pages — support their statements. A refinement is acknowledged by its `revisions` entry; a doubtful source verdict is acknowledged by a `source_notes` entry or fixed at the source.

The check reports a contradiction, and an invariant no source supports. It stays quiet about a source that merely does not state the rule once another source states it, because a `sources` list may carry context as well as the page the statement came from. Two further cases are expected rather than reported: a `dwn/` page contradicting an `enbox-parity` invariant, and a page that names a non-normative invariant's ID instead of restating it, which is the page deferring to the registry.

## Agent workflows

The canonical tool-neutral workflows live under `agents/`. Tool-specific skills/commands for Claude, Codex, OpenCode, or other harnesses should remain thin adapters to those workflows.

Review an agent workflow when:

- the source hierarchy changes;
- invariant contract classes change;
- the expected semantic-change lifecycle changes;
- implementation/conformance policy changes in a way that alters required workflow outputs;
- tool wrappers begin depending on behaviour no longer described by the canonical workflow.

Do not fork workflow semantics into tool-specific copies unless a tool requires a narrowly scoped adapter. The canonical process belongs here.

## When knowledge must be reviewed

Review affected material when:

1. the DWN draft changes a depended-on semantic;
2. the TypeScript parity baseline changes materially;
3. a linked parity/divergence issue closes because behaviour changed;
4. a PR changes Records ordering/retention, authorization, permissions, encryption, sync, topology, durable storage, dependency classification, or error semantics;
5. architecture named by a page is removed/replaced;
6. a guide/example/learning module depends on the changed assumption;
7. an invariant's statement, contract class, or source provenance is affected;
8. an agent workflow's required evidence, output contract, or source hierarchy is affected.

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
8. review dependent learning/builder/example/implementation/conformance/agent guidance.