# ADR 0001: Separate Spec, TypeScript Reference, Rust Implementation, and Decisions

- Status: Accepted
- Date: 2026-08-28

## Context

The DWN draft, current TypeScript Enbox behavior, and current `enbox-rust-core` behavior can differ. During the implementation review, several real divergences were identified, including `$recordLimit`, live sync, encryption-control records, and DID-as-Service-Endpoint support.

If these sources are blended together, documentation can accidentally present an implementation choice as normative, or an obsolete implementation as current architecture.

## Decision

The knowledge base keeps four source classes explicit:

1. `dwn/` — spec-derived semantics and invariants.
2. `enbox/` — current implementation architecture and parity state.
3. `decisions/` — accepted architecture decisions, including intentional divergences.
4. GitHub issues — unresolved gaps, divergences, and active design questions.

Implementation pages must identify the upstream reference baseline they were reviewed against. Spec pages must identify the spec URL and review date. Where current Enbox intentionally differs from the draft, the difference must be linked to an issue or ADR rather than silently reconciled.

## Consequences

- Readers can tell what is normative versus implementation-specific.
- Coding agents have an explicit source precedence model.
- Rebaselining current Enbox can update implementation knowledge without rewriting the spec-derived layer.
- A page may become stale without making the entire knowledge corpus ambiguous: its metadata and linked issues identify the affected source boundary.

## Alternatives considered

### One unified set of DWN documents

Rejected because it hides disagreements between the draft and current implementations.

### Treat current TypeScript Enbox as the specification

Rejected. TypeScript is the behavioral parity target for Rust where documented, but it is not automatically normative DWN semantics.
