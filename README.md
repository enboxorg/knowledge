# Enbox Knowledge

Curated engineering knowledge for Decentralized Web Nodes (DWNs), the Enbox implementation, DWN engine authors, and applications built on top of DWNs.

This repository separates six kinds of knowledge:

1. **DWN model** — spec-derived semantics and invariants.
2. **Enbox implementation** — how current Enbox realizes those semantics in TypeScript and Rust.
3. **Builder guidance** — practical design guidance for applications and protocols.
4. **Implementation guides** — engine-level contracts independent of one language/storage design.
5. **Conformance checklists** — observable behaviours suitable for cross-implementation testing.
6. **Decisions** — architecture decisions and intentional divergences.

## Structure

```text
dwn/             DWN concepts, invariants, and protocol semantics
enbox/           implementation architecture and code mappings
builders/        practical guidance for designing applications and protocols
implementation/  engine-author contracts and implementation boundaries
conformance/     behavior-oriented conformance checklists
decisions/       ADR-style decisions and intentional divergences
maintenance/     freshness and provenance policy
```

Start with:

- [`dwn/foundations.md`](dwn/foundations.md)
- [`dwn/records.md`](dwn/records.md)
- [`dwn/protocols.md`](dwn/protocols.md)
- [`builders/getting-started.md`](builders/getting-started.md) when building an application/protocol
- [`implementation/README.md`](implementation/README.md) when implementing a DWN engine
- [`conformance/README.md`](conformance/README.md) when building test/compatibility suites
- [`AGENTS.md`](AGENTS.md) for coding-agent guidance
- [`glossary.md`](glossary.md) for terminology

## Source hierarchy

For implementation work, keep these distinct:

1. the DWN draft specification,
2. current `enboxorg/enbox` TypeScript behaviour,
3. current `enboxorg/enbox-rust-core` behaviour.

Where the current TypeScript implementation intentionally differs from the draft, implementation-parity work in Rust follows the documented upstream behaviour and links the relevant spec issue.

Builder, implementation, and conformance guides are synthesis, not normative authority. When they conflict with `dwn/` or a documented implementation fact, fix the guide/checklist rather than treating it as a new source of truth.

## Maintenance

Knowledge pages should be concise, evidence-oriented, and explicit about whether a statement is normative, implementation-specific, guidance, a conformance expectation, or an architectural decision. Prefer invariants, traps, code mappings, design matrices, test contracts, and issue links over tutorial prose.
