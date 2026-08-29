# Enbox Knowledge

Curated engineering knowledge for Decentralized Web Nodes (DWNs), the Enbox implementation, DWN engine authors, and applications built on top of DWNs.

This repository separates ten kinds of knowledge:

1. **DWN model** — spec-derived semantics and invariants.
2. **Enbox implementation** — how current Enbox realizes those semantics in TypeScript and Rust.
3. **Learning path** — a deliberate progression and reasoning exercises for experienced engineers.
4. **Invariant registry** — stable machine-readable rules with source classes and links.
5. **Builder guidance** — practical design guidance for applications and protocols.
6. **Worked examples** — complete protocol/application designs that apply the builder process end-to-end.
7. **Implementation guides** — engine-level contracts independent of one language/storage design.
8. **Conformance checklists** — observable behaviours suitable for cross-implementation testing.
9. **Agent workflows** — tool-neutral playbooks for contract discovery, implementation, and semantic review.
10. **Decisions** — architecture decisions and intentional divergences.

## Structure

```text
dwn/             DWN concepts, invariants, and protocol semantics
enbox/           implementation architecture and code mappings
learning/        guided learning path and reasoning exercises
invariants/      stable machine-readable DWN/Enbox invariant registry
builders/        practical guidance for designing applications and protocols
examples/        fully worked protocol/application designs
implementation/  engine-author contracts and implementation boundaries
conformance/     behavior-oriented conformance checklists
agents/          tool-neutral AI engineering workflows and task templates
decisions/       ADR-style decisions and intentional divergences
maintenance/     freshness and provenance policy
```

Start with:

- [`learning/README.md`](learning/README.md) for a guided route through the corpus
- [`dwn/foundations.md`](dwn/foundations.md) for canonical concepts
- [`invariants/README.md`](invariants/README.md) for compact stable rules
- [`builders/getting-started.md`](builders/getting-started.md) when building an application/protocol
- [`examples/README.md`](examples/README.md) for end-to-end worked designs
- [`implementation/README.md`](implementation/README.md) when implementing a DWN engine
- [`conformance/README.md`](conformance/README.md) when building test/compatibility suites
- [`agents/README.md`](agents/README.md) for AI-assisted engineering workflows
- [`AGENTS.md`](AGENTS.md) for coding-agent guidance
- [`glossary.md`](glossary.md) for terminology

## Source hierarchy

For implementation work, keep these distinct:

1. the DWN draft specification,
2. current `enboxorg/enbox` TypeScript behaviour,
3. current `enboxorg/enbox-rust-core` behaviour.

Where current TypeScript intentionally differs from the draft, Rust parity work follows the documented upstream behaviour and links the relevant spec issue.

Learning, invariant summaries, builder/example/implementation/conformance guides, and agent workflows are aids to reasoning, not independent protocol authority. Every invariant records its contract class so Enbox parity behaviour is not silently promoted to normative DWN behaviour.

## Maintenance

Keep pages concise, evidence-oriented, and explicit about source class. Prefer stable invariants, traps, code mappings, design matrices, test contracts, and issue links over unsupported assumptions.