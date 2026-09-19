---
domain: enbox
kind: implementation
repositories:
  - enboxorg/enbox
  - enboxorg/enbox-rust-core
upstream-baseline: c63bf424ac0997583db825e8a5fddf1507d30c40
reviewed: 2026-09-16
related-issues:
  - enbox-rust-core#317
  - enbox-rust-core#308
---

# did:dht in Enbox

Current TypeScript behaviour for `did:dht` creation, DNS codec, BEP44
framing, and Pkarr publication, as implemented in
`packages/dids/src/methods/` (`did-dht.ts`, `did-dht-dns.ts`,
`did-dht-pkarr.ts`) with agent creation in
`packages/agent/src/hd-identity-vault.ts`. DID-method behaviour: nothing
here is normative DWN semantics.

## DID format

The suffix is the z-base-32 Ed25519 identity key
(`DID-DHT-001`). The identity verification method takes fragment `0`;
its JWK `kid` is the RFC 7638 thumbprint.

## Agent document shape

The vault builds `#0` (identity; authentication, assertionMethod,
capabilityInvocation, capabilityDelegation), `#sig` (signing;
authentication, assertionMethod), `#enc` (X25519; keyAgreement), and an
optional `#dwn` `DecentralizedWebNode` service. Creation fills default
`alg` values so create/encode/decode round trips are stable
(`DID-DHT-006`).

## DNS mapping

Documents map to authoritative response packets (ID 0, TTL 7200,
compressed names). Root (`_did.<ID>.`), verification-method (`_kN`),
service (`_sN`), `alsoKnownAs` (`_aka`), controller (`_cnt`), type-index
(`_typ`), and gateway (`NS`) records follow the v0 property mapping;
defaults (`JsonWebKey`, key-type algorithms, thumbprint ids, single
controllers) are omitted where decoding restores them (`DID-DHT-002`).
A TXT character string holds at most 255 bytes, so a longer logical value
spans segments, split on UTF-8 byte boundaries rather than inside a
sequence (`DID-DHT-003`).

## Decoder normalizations

Decoding sets method type `JsonWebKey`, fills default algorithms and
thumbprint kids, coerces endpoints to arrays, and collapses singleton
controller and custom-property arrays to strings.

## BEP44 and Pkarr

The preimage signs the raw compressed DNS bytes exactly; `v` is at most
1000 bytes; sequences are Unix-second ceilings raised past any previous
value. Relay bodies are `signature || sequence_be || v` PUT as
`application/octet-stream` to the gateway identity URL
(`DID-DHT-004`, `DID-DHT-005`). The deployed gateway checks key,
signature, length, and recency only.

## Known TypeScript divergences

`DID-DHT-008` (preimage-length limit), `DID-DHT-009` (UTF-16 chunking),
`DID-DHT-010` (`split('=')` parsing), `DID-DHT-011` (URI-valued NS data,
live in the publish fixture). Rust corrects rather than copies all four.
Separately, the DID DHT registry table transposes the `enc`/`sig` wire
labels while its examples preserve names; follow the examples and file a
registry correction.

## Fixtures

`fixtures/interop/did-dht-publish.json` (pinned TypeScript output) and
`crates/did-dht/tests/fixtures/rust-publish-bytes.json` (Rust output for
the pinned decoder) in enbox-rust-core.
