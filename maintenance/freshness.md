# Knowledge Freshness and Drift Policy

This repository is useful only if readers can tell what source a statement came from and when it was last checked.

## Source classes

Every substantive knowledge page belongs to one of these classes:

- **normative** — derived from the DWN draft/spec.
- **implementation** — derived from current Enbox code and behavior.
- **decision** — an accepted architecture decision.

Do not merge those classes into one source of truth.

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

If the page depends on a known unresolved divergence, link the corresponding `enboxorg/dwn-spec` issue in the body.

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

If a claim is true only for TypeScript or only for Rust, say so explicitly. An open parity issue is not evidence that a behavior is already implemented.

### ADRs

ADRs must include a status and date near the top of the document. If an ADR is superseded, keep the old ADR and link to its replacement rather than rewriting history.

## When knowledge must be reviewed

Review the affected pages when any of the following occurs:

1. the DWN draft changes semantics used by the page;
2. the pinned/current Enbox TypeScript baseline changes materially;
3. a linked parity or divergence issue closes because behavior changed;
4. a PR changes Records ordering/retention, authorization, permissions, encryption, sync, topology, or durable storage semantics;
5. an implementation removes or replaces an architecture named in the page.

A review does not require changing prose if the content remains correct; update the review date/baseline only after actually checking the source.

## Staleness is a signal, not proof of incorrectness

Review dates are intentionally visible. A page with an old date should be rechecked before being used to make a high-impact implementation decision, but age alone does not mean the page is wrong.

The metadata check may report old review dates as warnings. It should fail only on malformed or missing provenance metadata.

## PR rule

A behavior-changing PR in an Enbox repository should do one of the following:

- update the relevant knowledge page in the same change;
- open a focused knowledge follow-up and link it;
- state explicitly why the behavior change does not affect documented knowledge.

The goal is to make documentation drift an explicit engineering decision rather than an accidental side effect.

## Rebaseline procedure

When adopting a new TypeScript Enbox parity baseline:

1. update code/fixtures and the parity matrix in `enbox-rust-core`;
2. search `enbox/` pages for the previous baseline SHA;
3. re-verify each affected implementation claim against the new baseline;
4. update `upstream-baseline` and `reviewed` only after verification;
5. link new divergences to focused GitHub issues;
6. do not edit `dwn/` pages merely to match TypeScript if the draft itself did not change.
