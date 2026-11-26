# ADR 0009: Agent Vault HD Derivation Moves to BIP-43 v2 with Dual-Derive Fallback

- Status: Accepted
- Date: 2026-11-26

## Context

`HdIdentityVault` in `enboxorg/enbox` (`packages/agent/src/hd-identity-vault.ts`) and its parity counterpart in `enboxorg/enbox-rust-core` (`crates/dwn-rs-agent/src/agent/derivation.rs`) currently derive vault and agent-DID keys via SLIP-0010 Ed25519 under the BIP-44 Bitcoin coin-type tree (`ENBOX-AGENT-001`):

- vault: `m/44'/0'/0'/0'/0'`
- identity: `m/44'/0'/1708523827'/0'/0'`
- signing: `m/44'/0'/1708523827'/0'/1'`
- encryption: `m/44'/0'/1708523827'/0'/2'`

The vault is not cryptocurrency-related, yet the vault path is string-identical to Bitcoin's first mainnet receiving-address path, and `1708523827'` sits in an unregistered account slot under BTC coin type `0'`. While SLIP-0010 (`"ed25519 seed"`) and BIP-32 (`"Bitcoin seed"`) keep derived bytes distinct today, reusing `m/44'/0'/…` is misleading and creates a future collision class if secp256k1 keys are ever derived at the same path.

Daily vault operations (`unlock`, `changePassword`, `backup`, `restore`, `getDid`, `encryptData`, `decryptData`, and `VaultBackedSecretStore`) do not run HD derivation; they rely solely on the persisted `contentEncryptionKey` JWE (whose `p2s` salt is embedded in the protected header) and the persisted `did` JWE. Only two operations invoke HD derivation: `initialize` and `resetPasswordWithRecoveryPhrase`.

This is agent/vault parity and engine-contract architecture, not normative DWN protocol semantics.

## Decision

Introduce a `v2` SLIP-0010 Ed25519 derivation tree under an explicit BIP-43 namespace prefix (`m/43'/1708523827'/…`, all hardened segments) and migrate both TypeScript and Rust in lockstep using **versioned dual-derive fallback (`v2` default, `v1` fallback)**:

| Key | `v1` (legacy) | `v2` (default) |
| --- | --- | --- |
| Vault | `m/44'/0'/0'/0'/0'` | `m/43'/1708523827'/0'/0'` |
| Identity | `m/44'/0'/1708523827'/0'/0'` | `m/43'/1708523827'/1'/0'/0'` |
| Signing | `m/44'/0'/1708523827'/0'/1'` | `m/43'/1708523827'/1'/0'/1'` |
| Encryption | `m/44'/0'/1708523827'/0'/2'` | `m/43'/1708523827'/1'/0'/2'` |

- **HKDF inputs remain unchanged**: `CEK = HKDF-SHA512(empty, vault_priv_32, "vault_cek", 32)` and `unlock_salt = HKDF-SHA512(empty, 0x00 || vault_pub_32, "vault_unlock_salt", 32)`. Keeping the 33-byte `0x00 || pub` SLIP-0010 serialization means `v1` and `v2` differ only in their four derivation paths and require no `Ed25519HdKey` changes.
- **Version metadata**: `IdentityVaultStatus` gains an optional `derivationVersion?: 1 | 2` field. An absent field defaults to `1` so existing `v1` stores and backups remain valid without migration. `backup()` and `restore()` preserve `derivationVersion` verbatim in `status`.
- **Fresh `initialize()`** (no `recoveryPhrase`): derives `v2` (or an explicitly supplied `derivationVersion`) and persists `derivationVersion` in `vaultStatus`.
- **Recovery `initialize({ recoveryPhrase, derivationVersion? })`**:
  - When `derivationVersion` is explicitly provided, derive and reconcile that version directly (supporting offline or expired-DHT `v1` recovery).
  - Otherwise, derive `v2` and resolve its `did:dht` URI. If found, reconcile and store `v2`. Only if resolution returns an explicit `notFound` (never on gateway or transport errors), derive `v1` and resolve its `did:dht` URI; if found, reconcile and store `v1`. If neither is found, fall through to `v2`.
- **`resetPasswordWithRecoveryPhrase()`**: derive using the vault's stored `derivationVersion` (absent = `1`), verify against the stored `did` JWE and URI, and re-wrap the CEK.

## Consequences

- Existing `v1` vaults, backups, agent DIDs, DWN tenants, and `VaultBackedSecretStore` envelopes continue working without forced re-onboarding or tenant migration.
- All newly initialized vaults use `v2` and no longer share path strings with BIP-44 Bitcoin wallets.
- Recovering a `v1` phrase on a new device performs two DHT lookups (one-time recovery cost); recovering a `v1` phrase whose `did:dht` record expired from the DHT requires either a vault backup or passing `derivationVersion: 1`.
- Both TypeScript (`enboxorg/enbox`) and Rust (`enboxorg/enbox-rust-core`) must implement identical `v2 → v1` fallback semantics and maintain both `v1` and `v2` golden vectors and interop fixtures.
- Once TypeScript lands and `enbox-rust-core` pins the updated commit, `enbox/agent-vault.md` and `ENBOX-AGENT-001` will be updated to reflect both `v1` and `v2` profiles.

## Alternatives considered

- **Clean break (drop `v1` paths immediately)**: rejected; while existing vaults would still unlock by password, `resetPasswordWithRecoveryPhrase` would fail for all pre-migration vaults and new-device phrase recovery would silently derive a different `did:dht` and orphan existing DWN tenants.
- **Active in-place `v1 → v2` tenant migration**: rejected; rotating an existing agent DID requires DWN re-registration, record/grant migration, and secret re-encryption, which is disproportionate because `v1` keys are not cryptographically compromised.
- **Accept `m/44'/0'/…` permanently**: rejected; leaves permanent BIP-44 Bitcoin path reuse in new vaults.
- **Change `vault_unlock_salt` to raw 32-byte pubkey in `v2`**: rejected; provides no security improvement while coupling `v2` to an `Ed25519HdKey` change and adding a second axis of divergence between `v1` and `v2`.

## Related

- `ENBOX-AGENT-001`, `ENBOX-AGENT-005`, `ENBOX-AGENT-006`, `ENBOX-AGENT-009`
- `enbox/agent-vault.md`
- `enboxorg/enbox#1701`
- `enboxorg/enbox-rust-core#308`, `enboxorg/enbox-rust-core#330`
