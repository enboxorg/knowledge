# ADR 0010: Adopt Enbox `Modules` Wire Vocabulary as Enbox Parity

- Status: Accepted (2026-11-27)
- Date: 2026-11-27

## Context

In `enboxorg/enbox#1826` (`6c99fa16`), `#1839` (`3347d418`), and `#1840` (`24ad6cff`), upstream TypeScript Enbox cut over its DWN wire vocabulary, JSON schemas, built-in encryption URI, path-encryption KDF derivation label, storage indexes, and structured error codes from `Protocols` to `Modules`, and removed all legacy compatibility shims:

- Interface name: `Protocols` -> `Modules` (`ModulesConfigure`, `ModulesQuery`).
- Descriptor, filter, permission-scope, and signature-payload fields: `protocol` -> `module`, `protocolPath` -> `modulePath`, `protocolPathPrefix` -> `modulePathPrefix`, `protocolRole` -> `moduleRole` (plus `MessagesFilter.modulePath`, mutually exclusive with `modulePathPrefix`).
- Built-in encryption module URI: `https://identity.foundation/dwn/protocols/encryption` -> `https://identity.foundation/dwn/modules/encryption` (`PERMISSIONS_MODULE_URI` remains `https://identity.foundation/dwn/permissions`).
- Path-derived key encryption: `derivationScheme: "modulePath"` on the wire and `"modulePath"` in the HKDF KEK info JSON array (`[KEY_AGREEMENT_ALGORITHM, "modulePath", keyId]`) and grant-key derivation path; `roleAudience` retains its scheme name and `rolePath` with a `module` namespace.
- Structured error codes: `ProtocolAuthorization*` -> `ModuleAuthorization*`, `ProtocolsConfigure*` -> `ModulesConfigure*`, `ProtocolsGrantAuthorization*` -> `ModulesGrantAuthorization*`, `ProtocolsQueryUnauthorized` -> `ModulesQueryUnauthorized`, `PermissionsProtocol*` -> `PermissionsModule*`, `EncryptionProtocol*` -> `EncryptionModule*`, and `*Protocol*` -> `*Module*` in `Messages`/`Records`/`Url` error codes.
- Hard cutover: no dual-reading of `protocol`/`protocolPath`/`protocolRole`, no `Protocols` interface alias, and no in-place relabeling of signed messages or migration of pre-cutover stores (relabeling a signed message breaks its JWS signature, CID, and derived keys).

Meanwhile, the DWN draft specification (`enboxorg/dwn-spec@e3f6491`) still uses the `Protocols` vocabulary (`ProtocolsConfigure`, `ProtocolsQuery`, `protocol`, `protocolPath`, `protocolRole`). Per ADR 0001 (`0001-source-hierarchy.md`), this is an explicit `TS != Spec` divergence and must not be silently promoted to normative DWN semantics.

Additionally, `enboxorg/enbox#1837` (`30fd691b`) standardized HTTP DWN RPC transport onto a single body-framed format (`Content-Type: application/vnd.enbox.dwn-rpc` with a 5-byte `[flags: u8, envelope_len: u32]` prefix), removing legacy `dwn-request` header framing.

## Decision

1. **Classify `Protocols -> Modules` as `enbox-parity`, not normative DWN semantics.** `enbox-rust-core` adopts the `enbox@1d02b195` `Modules` wire vocabulary, JSON schemas, `ENCRYPTION_MODULE_URI`, `modulePath` KDF label, `Module*`/`Modules*` error codes, and `application/vnd.enbox.dwn-rpc` single HTTP body framing so Rust engines, agents, and FFI hosts interoperate directly with current Enbox TypeScript peers and servers.
2. **Hard cutover without wire shims or in-place store translation.** Matching `enbox/docs/MODULE-CUTOVER.md` and `DWN-REC-001`, Rust rejects `interface: "Protocols"` at schema validation, provides no dual readers or field aliases, and does not translate pre-cutover SQLite stores in place. Existing stores must be reinitialized cleanly.
3. **Preserve normative DWN semantic invariants.** The `dwn/` layer and `DWN-PROTO-*`, `DWN-REC-*`, and `DWN-AUTH-*` invariants remain anchored to `dwn-spec` and describe protocol/module semantics independently of the `enbox-parity` wire spelling. If `dwn-spec` later adopts `Modules`, this ADR can be updated or superseded to reflect convergence.

## Consequences

- `enbox-rust-core` can advance `.enbox-version` from `c63bf424` to `>= 1d02b195`, refresh all 21 TS-parity fixtures, and implement `#199` DWN-backed agent stores directly on the `Modules` vocabulary without rework.
- Any Rust consumer or host app upgrading across the cutover must initialize fresh DWN and agent stores rather than migrating pre-cutover signed messages.
- Conformance and parity tests referencing `Modules` wire fields or `Module*` error codes remain classified as `enbox-parity` (e.g., `ENBOX-ERR-001`), never mislabeled as `normative` DWN spec requirements.

## Alternatives considered

- **Keep Rust on `Protocols` until `dwn-spec` adopts `Modules`**: Rejected. It would freeze `.enbox-version` at `c63bf424`, break interoperability with `enbox@1d02b195` servers/peers, and force `#199` agent stores to be written twice.
- **Support dual `Protocols` + `Modules` wire readers in Rust**: Rejected. Upstream explicitly removed compatibility shims (`#1839`, `#1840`), and dual-reading introduces signature/CID/KDF ambiguity across two incompatible wire formats.

## Related

- `decisions/0001-source-hierarchy.md`
- `dwn/protocols.md`, `enbox/architecture.md`
- `DWN-PROTO-001`–`DWN-PROTO-006`, `DWN-REC-001`, `ENBOX-ERR-001`
- `enboxorg/enbox#1826`, `enboxorg/enbox#1837`, `enboxorg/enbox#1839`, `enboxorg/enbox#1840`
- `enboxorg/enbox-rust-core#355`, `enboxorg/enbox-rust-core#356`, `enboxorg/enbox-rust-core#357`
