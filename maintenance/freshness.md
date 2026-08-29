# Knowledge Freshness and Drift Policy

This repository is useful only if readers can tell what source a statement came from and when it was last checked.

## Source classes

Every substantive knowledge page belongs to one of these classes:

- **normative** — derived from the DWN draft/spec.
- **implementation** — derived from current Enbox code and behavior.
- **guide** — practical synthesis for builders or DWN engine authors, grounded in normative and implementation knowledge.
- **worked example** — an end-to-end design applying guide material to one explicit actor/authority model.
- **conformance guide** — behavior-oriented checklist material used to design tests; still subordinate to the targeted normative/implementation contract.
- **decision** — an accepted architecture decision.

Do not merge those classes into one source of truth. Guide/example/checklist content is intentionally non-normative: if it conflicts with `dwn/` semantics or a documented implementation fact, it must be corrected.

## Required metadata

### DWN/spec-derived pages

Pages under `dwn/` must include front matter with at least:

```yaml
---
domain: dwn
kind: normative
spec: https://dwn-spec.pages.dev/
spec-reviewed: YYYY-MM-DD
---
```

### Enbox implementation pages

Pages under `enbox/` must include front matter with at least:

```yaml
---
domain: enbox
kind: implementation
repositories:
  - enboxorg/enbox
  - enboxorg/enbox-rust-core
upstream-baseline: <enbox commit SHA>
reviewed: YYYY-MM-DD
---
```

### Builder guides

Pages under `builders/` use:

```yaml
---
domain: builders
kind: guide
reviewed: YYYY-MM-DD
---
```

### Worked examples

Substantive pages under `examples/` use:

```yaml
---
domain: examples
kind: guide
reviewed: YYYY-MM-DD
---
```

Examples should identify their actor/authority assumptions and distinguish illustrative protocol JSON from normative syntax. Review them when any underlying DWN semantic, Enbox behavior, or builder recommendation they rely on changes.

### DWN implementation guides

Pages under `implementation/` use:

```yaml
---
domain: implementation
kind: guide
reviewed: YYYY-MM-DD
---
```

### Conformance checklists

Pages under `conformance/` use:

```yaml
---
domain: conformance
kind: guide
reviewed: YYYY-MM-DD
---
```

Conformance pages must state which normative or documented implementation contract they target. When draft and current implementation differ, fixtures/checklists should be labelled accordingly rather than silently combining both behaviours.

### ADRs

ADRs must include a status and date near the top. If superseded, retain the historical ADR and link to the replacement.

## When knowledge must be reviewed

Review affected pages when:

1. the DWN draft changes semantics used by the page;
2. the pinned/current TypeScript parity baseline changes materially;
3. a linked parity/divergence issue closes because behaviour changed;
4. a PR changes Records ordering/retention, authorization, permissions, encryption, sync, topology, durable storage, dependency classification, or error semantics;
5. an implementation removes/replaces architecture named by a page;
6. a builder, example, implementation, or conformance guide relies on an affected assumption.

Update dates/baselines only after actually reviewing the source.

## Staleness is a signal, not proof of incorrectness

Old review dates should trigger rechecking before high-impact implementation or protocol-design decisions. Age alone does not prove a page is wrong. Metadata CI should warn on old review dates and fail on missing/malformed provenance.

## PR rule

A behaviour-changing Enbox PR should either update the affected knowledge, open/link a focused follow-up, or explicitly state why documented knowledge is unaffected.

A spec change that alters observable behavior should similarly trigger review of `dwn/`, `builders/`, `examples/`, `implementation/`, and `conformance/` pages that depend on it.

## Rebaseline procedure

When adopting a new TypeScript Enbox parity baseline:

1. update code/fixtures and parity evidence in `enbox-rust-core`;
2. find `enbox/` pages pinned to the previous baseline;
3. re-verify affected implementation claims;
4. update `upstream-baseline` and `reviewed` only after verification;
5. link new divergences to focused issues;
6. do not edit `dwn/` merely to match TypeScript if the draft did not change;
7. review affected builder/example/implementation/conformance guidance.
