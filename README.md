# Enbox Knowledge

Curated engineering knowledge for Decentralized Web Nodes (DWNs) and the Enbox implementation.

This repository separates three kinds of knowledge:

1. **DWN model** — spec-derived semantics and invariants.
2. **Enbox implementation** — how current Enbox realizes those semantics in TypeScript and Rust.
3. **Decisions** — architecture decisions and intentional divergences.

## Structure

```text
dwn/        DWN concepts, invariants, and protocol semantics
enbox/      implementation architecture and code mappings
decisions/  ADR-style decisions and intentional divergences
```

Start with:

- [`dwn/foundations.md`](dwn/foundations.md)
- [`dwn/records.md`](dwn/records.md)
- [`dwn/protocols.md`](dwn/protocols.md)
- [`AGENTS.md`](AGENTS.md) for coding-agent guidance
- [`glossary.md`](glossary.md) for terminology

## Source hierarchy

For implementation work, keep these distinct:

1. the DWN draft specification,
2. current `enboxorg/enbox` TypeScript behaviour,
3. current `enboxorg/enbox-rust-core` behaviour.

Where the current TypeScript implementation intentionally differs from the draft, implementation-parity work in Rust follows the documented upstream behaviour and links the relevant spec issue.

## Maintenance

Knowledge pages should be concise, evidence-oriented, and explicit about whether a statement is normative, implementation-specific, or an architectural interpretation. Prefer invariants, traps, code mappings, and issue links over tutorial prose.
