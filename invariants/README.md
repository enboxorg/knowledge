# DWN and Enbox Invariants

`invariants/` is a machine-readable index of high-value rules that humans and agents should be able to cite while reasoning about DWN behaviour.

The files are JSON arrays. Every invariant has:

- `id` — stable identifier; do not recycle it for a different meaning;
- `statement` — compact assertion;
- `contract` — the source class the assertion belongs to;
- `sources` — knowledge pages that explain/support it;
- `related` — optional tests, implementation pages, ADRs, or tracked issues.

## Contract classes

- `normative` — derived from the DWN draft/spec knowledge layer.
- `enbox-parity` — current TypeScript Enbox behaviour used as the Rust parity target where documented.
- `implementation-contract` — architecture-neutral property required of a correct engine implementation.

An `enbox-parity` invariant must not be silently promoted to normative DWN behaviour. If draft and current Enbox semantics converge later, update the contract/source references deliberately while keeping the stable ID when the statement itself remains equivalent.

## Files

- `records.json`
- `errors.json`
- `authorization.json`
- `protocols.json`
- `sync.json`
- `identity-encryption.json`

## Usage

When reviewing code or answering a design question, prefer statements like:

> `DWN-AUTH-002`: protocol authorization evaluates the semantic Author, which may differ from the Signer when valid author delegation is used.

rather than relying on a vague memory of a long document.

The metadata validator checks JSON syntax, required fields, allowed contract classes, and global ID uniqueness.
