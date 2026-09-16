# ADR 0008: did:dht Targets External Spec with Selective Enbox Parity

- Status: Accepted
- Date: 2026-09-16

## Context

`did:dht` creation and publication is DID-method behaviour, not DWN protocol
behaviour: no DWN draft contract governs it. Three sources constrain the
implementation: DID DHT 1.0 with BEP44 and the Pkarr relay protocol
(`external-spec`), current TypeScript Enbox agent documents (`enbox-parity`),
and the deployed `enboxorg/did-dht` gateway, which validates only key,
signature, length, and sequence recency — never DNS semantics.

Current TypeScript carries four codec defects relevant here: the 1000-byte
limit is checked against the signing preimage instead of `v`
(`DID-DHT-008`); TXT values are chunked at UTF-16 code units instead of
UTF-8 bytes (`DID-DHT-009`); TXT properties split on every `=`
(`DID-DHT-010`); and the gateway URI, not its host, is emitted as NS data
(`DID-DHT-011`, evidenced live in `fixtures/interop/did-dht-publish.json`
in enbox-rust-core). The DID DHT registry, independently, transposes the
`enc`/`sig` wire labels in its table while its examples preserve names.

## Decision

Rust targets the external wire rules and observable agent-document parity,
and corrects the TypeScript defects rather than copying them. Concretely:
size is enforced on `v` alone with 1000 accepted and 1001 rejected before
signing; TXT segments are at most 255 UTF-8 bytes on character boundaries;
encoders reject delimiter-unsafe values the pinned decoder cannot parse;
NS records carry the normalized gateway host (omitted for IP literals);
and constructors emit decoder-normal documents (thumbprint kids, default
algorithms, array endpoints). Codec round trips hold the decoder fixpoint
(`DID-DHT-007`) rather than exact input-shape preservation, which the
lossy normalizations cannot support. Cross-runtime fixtures pin the repo
`.enbox-version`, not the discovery-time checkout.

## Consequences

- Rust output decodes under both the pinned and newer TypeScript decoders;
  TypeScript output decodes under Rust, including URI-valued NS records,
  which strict DNS tooling (but neither decoder) would reject.
- The four TypeScript defects stay open in their owning repository, as do
  the gateway NS-shape and registry table corrections.
- `DID-DHT-001`–`DID-DHT-005` must never be cited as normative DWN
  semantics; `DID-DHT-008`–`DID-DHT-011` must never be mistaken for
  intended behaviour — they record what current TypeScript does.

## Alternatives considered

- Byte-copying TypeScript, bugs included: rejected; it would enshrine
  wire-invalid output (split code points, truncated values) as a parity
  target and break interop with the deployed gateway's expectations.
- Exact input-shape preservation across the codec: rejected; the
  decoder's documented normalizations make it unattainable without a
  broader model change and upstream parity decisions.
- Pinning fixtures to the discovery-time checkout: rejected; the
  provenance gate requires `.enbox-version`, and the inter-pin codec
  diff is inert for explicit-alg inputs.

## Related

- `DID-DHT-001`–`DID-DHT-011`
- enboxorg/enbox-rust-core#317, #308, #314; PR #318
