---
domain: enbox
kind: implementation
repositories:
  - enboxorg/enbox
  - enboxorg/enbox-rust-core
upstream-baseline: 05b41776e92bd1f42462726d7a7d4bb2a0fcb9de
reviewed: 2026-11-27
related-issues:
  - enbox-rust-core#317
  - enbox-rust-core#308
  - enbox#1714
  - enbox#1616
  - enbox#1718
---

# did:dht in Enbox

Current TypeScript behaviour for `did:dht` creation, DNS codec, BEP44
framing, and Pkarr publication, as implemented in
`packages/dids/src/methods/` (`did-dht.ts`, `did-dht-dns.ts`,
`did-dht-pkarr.ts`) with agent creation in
`packages/agent/src/hd-identity-vault.ts`. DID-method behaviour: nothing
here is normative DWN semantics. The `upstream-baseline` is `05b41776`
(`enbox#1714`), which fixed the four codec defects documented against the
previous baseline `c63bf424`.

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

## Resolved TypeScript defects

Baseline `c63bf424` carried four codec defects: the 1000-byte BEP44 limit
was checked on the signing preimage instead of `v` (`DID-DHT-008`); TXT
values were chunked at UTF-16 code units (`DID-DHT-009`); TXT properties
split on every `=` (`DID-DHT-010`); and the gateway URI, not its host, was
emitted as NS data (`DID-DHT-011`, live in the publish fixture).
`enbox#1714` (`05b41776`) fixed all four: the limit is checked on `v`, TXT
segments are at most 255 UTF-8 bytes split at code-point boundaries, pairs
split on the first `=` only, and NS data is the normalized gateway host in
FQDN form (IP-literal gateways emit no NS record). Gateway URIs that cannot
be parsed or have no host keep the historical passthrough rather than being
rejected, with strict validation left open in `enbox#1718`. TypeScript at
`>= 05b41776` and Rust now both satisfy `DID-DHT-003` and `DID-DHT-004`;
`DID-DHT-008`–`DID-DHT-011` record the pre-`enbox#1714` behaviour only.

`enbox#1616` (`175222e6`) canonicalized JWK `alg` handling: encoding omits
`a` when a key has no algorithm or the key-type default, and decoding maps
an absent value or the legacy literal `a=undefined` to the default, so
create/encode/decode round trips stay stable (`DID-DHT-006`).

Separately, the DID DHT registry table transposes the `enc`/`sig` wire
labels while its examples preserve names; follow the examples and file a
registry correction.

## Fixtures

`fixtures/interop/did-dht-publish.json` (pinned TypeScript output) and
`crates/did-dht/tests/fixtures/rust-publish-bytes.json` (Rust output for
the pinned decoder) in enbox-rust-core.
