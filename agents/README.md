# Agent Engineering Workflows

`agents/` defines tool-neutral engineering playbooks for AI-assisted work on DWNs and Enbox.

These files are the canonical workflow definitions. Claude Code skills, Codex skills/instructions, OpenCode commands, and other tool-specific wrappers should be thin adapters that invoke these playbooks rather than copying and evolving their logic independently.

## Workflows

- [`contract-discovery.md`](contract-discovery.md) — gather the relevant semantic, parity, implementation, and issue context before code changes and produce a Behavioural Contract Packet.
- [`implement-contract.md`](implement-contract.md) — implement an approved behavioural contract without silently changing its semantics.
- [`review-change.md`](review-change.md) — independently review a completed change against the approved contract, controlling invariants, and conformance expectations.

## Templates

- [`templates/contract-packet.md`](templates/contract-packet.md)
- [`templates/semantic-review.md`](templates/semantic-review.md)

## Core workflow

```text
issue / task
    ↓
contract discovery
    ↓
Behavioural Contract Packet
    ↓
human approval / correction
    ↓
implementation
    ↓
diff / PR
    ↓
independent semantic review
```

The human approval boundary is intentional. Agents may gather evidence and propose the behavioural contract, but a non-trivial semantic change should not silently move from investigation to implementation when the intended behaviour remains ambiguous.

## Source hierarchy

All workflows must preserve the repository source hierarchy:

1. `dwn/` — DWN draft/spec-derived semantics.
2. `enbox/` — current Enbox implementation mapping and parity facts.
3. `implementation/` — architecture-neutral engine contracts.
4. `conformance/` — observable test expectations.
5. `invariants/` — stable IDs and explicit contract class.
6. `decisions/` — accepted architecture decisions.
7. linked GitHub issues — unresolved gaps/divergences and implementation ownership.

When needed, inspect the actual current TypeScript and Rust source rather than relying only on summaries.

An invariant ID is a traceability anchor, not proof that a statement is normative. Always preserve its `contract` class (`normative`, `enbox-parity`, or `implementation-contract`).

## Local workspace expectation

For agent-heavy development, a useful workspace is:

```text
work/
├── enbox-rust-core/
├── enbox/
├── dwn-spec/
└── knowledge/
```

Tool wrappers should prefer these local sibling repositories when available because they allow cheap search and source comparison. Remote GitHub/spec access is a fallback when local sources are unavailable or freshness must be verified.

## Task artifacts

Behavioural Contract Packets and semantic review reports are task artifacts, not permanent normative knowledge. They may live in a gitignored path such as `.agent/contracts/` during development and be summarized in the final PR description.
