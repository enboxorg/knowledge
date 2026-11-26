---
domain: enbox
kind: implementation
repositories:
  - enboxorg/enbox
  - enboxorg/enbox-rust-core
upstream-baseline: c63bf424ac0997583db825e8a5fddf1507d30c40
reviewed: 2026-11-26
related-issues:
  - enbox-rust-core#308
  - enbox-rust-core#329
  - enbox-rust-core#330
  - enbox-rust-core#353
  - enbox#1701
---

# Agent Identity Vault

Current Enbox TypeScript behaviour in `packages/agent/src/hd-identity-vault.ts`
and `packages/agent/src/secret-store.ts`, and the `enbox-rust-core` parity
implementation in `dwn-rs-agent` (`agent/vault.rs`, `agent/vault_jwe.rs`,
`agent/derivation.rs`, `agent/secret_store.rs`, `agent/errors.rs`) surfaced by
`enbox-ffi`. This is agent/vault parity and engine-contract behaviour:
**nothing here is normative DWN semantics.** The DWN draft is silent on phrases,
vault storage, and agent-DID derivation; `enbox/did-dht.md` owns the DID-method
wire rules.

`upstream-baseline` is the fixture pin. Vault-local behaviour is unchanged
between it and the publication/reconciliation target `a359e540`; only the
agent-DID publication callsites were added upstream in between. Fixtures are
generated at the pin.

## HD derivation

BIP-39 phrase → seed with an empty passphrase, then SLIP-0010 Ed25519,
hardened segments only. Two derivation profiles exist (see
`decisions/0009-vault-hd-derivation-v2.md`): `v2` (BIP-43 namespace, default for
new vaults) and `v1` (legacy BIP-44 tree, retained for dual-derive fallback):

| Key | `v1` (legacy) | `v2` (default) |
| --- | --- | --- |
| vault | `m/44'/0'/0'/0'/0'` | `m/43'/1708523827'/0'/0'` |
| identity | `m/44'/0'/1708523827'/0'/0'` | `m/43'/1708523827'/1'/0'/0'` |
| signing | `m/44'/0'/1708523827'/0'/1'` | `m/43'/1708523827'/1'/0'/1'` |
| encryption | `m/44'/0'/1708523827'/0'/2'` | `m/43'/1708523827'/1'/0'/2'` |

The encryption key's 32 bytes are the X25519 private key. Both profiles use the
exact same HKDF inputs; only the four paths differ:

- CEK = HKDF-SHA512(empty salt, vault private key, `"vault_cek"`, 32 bytes).
- Unlock salt = HKDF-SHA512(empty salt, `0x00 ‖ vault Ed25519 public key`,
  `"vault_unlock_salt"`, 32 bytes).

The zero prefix is the parity quirk: TS `Ed25519HdKey.publicKey` returns the
33-byte SLIP-0010 serialization `0x00‖pub`, not the 32-byte compressed key, and
that value is the HKDF input. Rust deliberately reproduces it, so one phrase
yields one salt and one CEK in both runtimes. The pre-parity Rust build hashed
the 32 raw bytes and produced a different salt; the plaintext vault path was
never released, so no store depends on it.

Vectors for `abandon ×11 about`:

- **`v1` (legacy)**: CEK
  `b99ff78488da4c83cbe590b5374bfca38551eb47e65514667018cc33c91f4913`, salt
  `cf6389ce23de14b02e05413e1bcc3715f6fed4c2b0eda9412701279288f37d20`, agent DID
  `did:dht:qftx7z968xcpfy1a1diu75pg5meap3gdtg6ezagaw849wdh6oubo`.
- **`v2` (default)**: CEK
  `a19daef652efd7e05e22a9184a244d63983fd5ef2714b113b8d60dc53028fd67`, salt
  `faa7f7433146bb721fd77c7b6a1cc6dc4725886130d6f05582eabca26bde85c0`, agent DID
  `did:dht:3pcjxsbcm5py5xaffs4uppp8ywubyy9bw4erbicw7qrkue1t81uo`.

Daily operations (`unlock`, `changePassword`, `backup`, `restore`, `getDid`,
`encryptData`/`decryptData`, `VaultBackedSecretStore`) do not run HD
derivation, so existing `v1` vaults and backups continue working without forced
re-onboarding or DWN tenant migration. Only `initialize` and
`resetPasswordWithRecoveryPhrase` invoke HD derivation.

## Recovery phrase acceptance

Acceptance equals TS `validateMnemonic(phrase, englishWordlist)`: NFKD
normalize, split on a single ASCII space, 12/15/18/21/24 words, English
wordlist, valid checksum. Seed derivation is BIP-39 `mnemonicToSeed` with an
empty passphrase. Generated phrases are 12 words (128-bit).

| Input | Result |
| --- | --- |
| 12/15/18/21/24 wordlist words, single spaces, valid checksum | accepted |
| Non-ASCII space characters (U+00A0, U+3000, …) | accepted once NFKD maps them to U+0020 |
| Uppercase, non-wordlist word, bad checksum, 13 words | rejected |
| Leading/trailing whitespace, repeated separators, tab or newline separators | rejected |
| Empty or whitespace-only phrase | rejected |

Rejection is `AgentIdentityInvalidMnemonic` (TS throws a generic error) and
happens before any durable write. Passwords are separate: raw UTF-8, no
normalization, and blank after trimming Unicode whitespace is rejected.

## At-rest values

Three logical entries, one per key; the two runtimes use different key names for
the same shapes:

| Key (Rust / TS) | Value |
| --- | --- |
| `agent:vault:cekJwe` / `contentEncryptionKey` | compact JWE, `PBES2-HS512+A256KW` + `A256GCM` |
| `agent:vault:didJwe` / `did` | compact JWE, `dir` + `A256GCM`, `cty: "json"` |
| `agent:vault:status` / `vaultStatus` | UTF-8 JSON status |

**CEK entry.** Protected header
`{"alg":"PBES2-HS512+A256KW","enc":"A256GCM","cty":"text/plain","p2c":<work factor>,"p2s":"<base64url salt>"}`.
The PBES2 key is the raw password bytes; `p2s` is the derivation salt. The
plaintext is the UTF-8 JSON oct JWK `{"k":"<base64url CEK>","kty":"oct","kid":"<RFC 7638 thumbprint>"}`.

**DID entry.** `dir`/`A256GCM` under the CEK, `cty: "json"`, encrypting the
`PortableDid` JSON.

**Status entry.** `{"initialized":bool,"lastBackup":string|null,"lastRestore":string|null,"derivationVersion"?:1|2}`.
An absent entry reads as `{false,null,null}` (omitting `derivationVersion`); a
present entry must carry both timestamp keys (null or string) or every
status-reading operation fails as corrupt. When `derivationVersion` is absent it
defaults to `1` (legacy `v1`); an explicit `null` or any value other than `1` or
`2` is corrupt.

Readers accept any conforming producer: 12-byte IV, AAD = ASCII of the encoded
protected header, any `p2c ≥ 1`, any `p2s` length or content, any header member
order. Writers emit what TS's allow-lists accept. Algorithms outside the
allow-lists above are rejected, and `p2c < 1` is corrupt.

This Compact JWE is vault-at-rest material, not DWN record encryption; see
`enbox/encryption.md`.

## Lifecycle

A vault is *uninitialized* until the status says `initialized: true`; otherwise
it is *locked* or *unlocked*. Lock state is per instance, in memory, never
persisted, and operations on one instance are serialized. A fresh instance is
locked and writes nothing.

| Operation | Observable behaviour |
| --- | --- |
| `initialize(password, phrase?, endpoints?, derivationVersion?)` | Errors already-initialized, then blank password, then invalid phrase, then invalid `derivationVersion` (must be `1` or `2` when supplied). Fresh `initialize` defaults to `v2`; recovery `initialize` without an explicit version resolves `v2` on DHT and falls back to `v1` **only** on explicit `NotFound` (never on gateway/transport/malformed errors), falling through to `v2` if neither is found; explicit `derivationVersion` skips auto-fallback. Publishes/reconciles the agent DID, then commits CEK, DID, and status (with `derivationVersion`) in one atomic write. Ends unlocked; Rust returns the phrase with the `PortableDid`, TS returns the phrase. Any failure leaves the store unchanged and the vault uninitialized. |
| `unlock(password)` | Uninitialized errors. Drops any held CEK first. Auth failure is `AgentVaultInvalidPassword`; a structurally invalid CEK entry is `AgentVaultCorrupt`. Never writes; failure ends locked. |
| `lock()` | Clears the CEK and any cached DID, then errors if uninitialized. Idempotent on an initialized vault. |
| `getDid()` / `get_did()` | `AgentVaultLocked` while locked or uninitialized. A corrupt DID entry is `AgentVaultCorrupt` and leaves the vault unlocked. Returns an isolated copy. |
| `changePassword(old, new)` | Uninitialized errors; a blank `new` is `AgentVaultBlankPassword` **before** the CEK is dropped. A wrong `old` ends locked with the store byte-identical. Success re-wraps the same CEK, preserving stored `p2s` and `p2c` (emitting `cty: text/plain`); DID and status are unchanged; ends unlocked. |
| `resetPasswordWithRecoveryPhrase(phrase, password, endpoints?)` | Uninitialized, then drops the CEK, then blank password, invalid phrase, then mismatch. Derives using the stored status's `derivationVersion ?? 1`. Mismatch means the stored DID entry does not decrypt under the phrase-derived CEK or its URI differs; code is exactly `HD_IDENTITY_VAULT_RECOVERY_PHRASE_MISMATCH` and the store is byte-identical. Success writes a fresh CEK wrap (and a reconciled DID) atomically while preserving `derivationVersion`, and ends unlocked. Without endpoints (and without the crate-internal defer flag) there is no network access. |
| `backup()` | Requires initialized and unlocked. Format below. |
| `restore(backup, password)` | Semantics below. |
| `encryptData` / `decryptData` | `AgentVaultLocked` while locked; `dir`/`A256GCM` compact JWE under the CEK. A decrypt failure leaves the vault unlocked. |
| `getStatus()` / `status()` | Returns the stored status; uninitialized reads as `{false,null,null}`. |

Key hygiene: a failed unlock, password change (other than the blank-new-password
pre-check), reset, or restore leaves no CEK reachable, and gated operations fail
with `AgentVaultLocked`. Intermediate derived keys and CEKs are zeroized;
passwords, phrases, CEK bytes/JWKs, and private keys never appear in `Debug`,
`Display`, or error details. Passwords are compared as raw UTF-8, so NFC and NFD
forms differ.

## Atomic persistence

Every mutation (`initialize`, `changePassword`, reset, `backup`'s status
update, `restore`) commits its puts and deletes as one `SecretStore::apply`
batch. A backend that cannot commit atomically must fail the call rather than
fall back to sequential writes. After a kill or store error at any point, a
reopened vault observes exactly the pre- or post-mutation store; an interrupted
`initialize` reopens uninitialized and a retry succeeds. Successful mutations
survive close and reopen.

## Backup and restore

`backup()` returns `{dateCreated, size, data}`:

- `data` = unpadded base64url of UTF-8 JSON
  `{"did": <stored DID JWE>, "contentEncryptionKey": <stored CEK JWE>, "status": <status before the call>}`;
- `size` = character count of `data`;
- `dateCreated` = agent clock now in UTC ISO-8601 with millisecond precision and
  `Z` (TS `toISOString` shape).

It then persists `lastBackup = dateCreated` in the same atomic guarantee.

`restore()` requires string `dateCreated`, numeric `size`, and string `data`;
`size` is not checked against the payload. Undecodable `data`, missing or
mistyped members, or a backup whose `status.initialized` is not `true` fail with
`AgentVaultInvalidBackup` and no write. Padded base64url is accepted; unknown
outer JSON members are ignored. A wrong password fails with
`AgentVaultInvalidPassword`; a structurally invalid backup CEK entry is
`AgentVaultInvalidBackup`.

On success the backup's CEK and DID strings are stored verbatim (so the backup's
`p2c`/`p2s` persist), the status becomes
`{initialized: true, lastBackup: backup.lastBackup ?? current.lastBackup, lastRestore: now}`
with `derivationVersion` taken strictly from the backup's status (absent in a
legacy `v1` backup must never inherit `2` from a prior local vault), and the
vault ends unlocked.

Restore is allowed onto an uninitialized store, under the same rules; a failed
restore leaves it uninitialized. Every failed restore, including a malformed
blob, ends locked. A backup from another identity or password restores: the
backup's password becomes the vault's.

Rejecting `initialized: false` backups is **parity, not divergence**: TS writes
the backup status, its inner `unlock` then fails on the cached
`initialized: false`, and its revert path errors.

## Vault-backed secret store

`VaultBackedSecretStore` (Rust `CredentialStore`, with the raw `SecretStore` as
its persistence seam) encrypts agent-local credentials with the shared vault.

- Persisted value: UTF-8 JSON `{"jwe": <vault data JWE>, "expiresAt"?: <ISO-8601>}`.
  The JWE is `dir`/`A256GCM` under the identity CEK, no `cty`. An absent expiry
  is omitted, not null; decrypted payload is arbitrary bytes.
- `put`/`get` require an unlocked vault; `delete` does not and reports whether an
  entry existed. Each operation is serialized on the shared instance;
  independent instances over one backend are not coordinated.
- `put` validates a supplied expiry (RFC 3339 with an explicit offset, `T`
  separator) before mutating.
- `get`: absent → `None`; malformed JSON, wrong member types, or an invalid
  expiry → `AgentSecretInvalidEnvelope`, never plaintext; a well-formed envelope
  whose JWE fails to decrypt keeps the vault codec error
  (`AgentIdentityVaultError`) and returns nothing; `expiresAt <= now` (instant
  compare, not string compare) deletes the entry and returns `None`; otherwise
  the original bytes are returned without rewriting.
- Keys under `agent:vault:` are rejected, so credentials cannot overwrite vault
  material when both share a backend.
- Legacy plaintext values are not migrated: they stay on disk, are never
  returned as plaintext, and fail typed until deleted or overwritten.

In Rust the durable producers are `enbox:auth:registrationTokens`,
`enbox:auth:delegateDecryptionKeys`, and `enbox:auth:delegateContextKeys`.
`delegateMultiPartyProtocols` and `sessionRevocations` exist only as key
constants with no durable producer.

## Agent DID creation and publication

The agent DID is built by `DidDhtProvider` from the identity, signing, and
encryption keys: pure local construction, `published: false`, URI
`did:dht:<z-base-32 identity key>`, and the `DID-DHT-006` document shape (`#0`,
`#sig`, `#enc`, optional `#dwn`). `enbox/did-dht.md` owns the codec, BEP44, and
relay rules.

- A fresh `initialize` publishes before the first vault write: sequence from
  `next_sequence(clock now, no previous)` (`DID-DHT-004`), the configured
  gateway as authoritative NS target, and no DID types. A rejection (including 409), transport failure,
  oversize value, or signer failure fails `initialize` with nothing written.
- A recovery `initialize` resolves the DID fresh (never from cache) and
  reconciles: found and ready → adopt the resolved `#dwn` service locally
  (republish only when replacement endpoints are given and replacement is not
  deferred, which is reset's path); found but not ready → require replacement
  endpoints and republish; not found → require endpoints (reset may reuse a
  usable stored `#dwn`), then publish; resolution failure → error. A gateway
  that is unavailable, times out, or answers 2xx with an empty/malformed body
  is a failure, never not-found.
- Reconcile inputs follow the caller: recovery `initialize` always defers
  replacement, so caller endpoints are used only on the not-ready/not-found
  paths; reset reconciles only when given endpoints or the internal defer flag.
- Every republication passes the resolved sequence as `previous`, so the
  submitted sequence strictly exceeds it even after a clock rollback.
- When a document was resolved, the published document is that resolved document
  with only `#dwn` rewritten (resolved `types` preserved); the stored document is
  the locally derived document carrying the adopted or replacement service.
- Publication signs with the identity key: the vault's optional host-supplied
  signer when present, otherwise the phrase-derived identity key. A signer that
  fails or signs with the wrong key fails before transport.
- Publish-before-commit leaves one window: a published DID whose commit then
  fails. Accepted (TS has the same window); a retry reconciles against the
  published document.

## Documented Rust divergences

| Behaviour | TypeScript | Rust |
| --- | --- | --- |
| Restore onto an uninitialized store | errors (it reads current values first) | succeeds |
| Blank new password on `changePassword` | accepted | `AgentVaultBlankPassword`, lock state unchanged, no write |
| Failed reset / failed restore lock state | reset leaves the prior state; a malformed-object restore leaves it unchanged | every failure ends locked |
| Backup DID entry validation | not decrypted or validated; `getDid` fails later | must decrypt under the recovered CEK and be a usable agent DID (Ed25519 signing + X25519 key agreement), else `AgentVaultInvalidBackup` |
| PBES2 work factor | constructor option, default 210 000; vault opens any `p2c ≥ 1` | same default and opening rule, plus an FFI constructor parameter; `0` is rejected with `AgentVaultError` before any write, no upper bound |
| Pre-#308 Rust state | n/a | unsupported: no plaintext identity writer or reader remains, pre-#308 `agent:vault:*` rows are neither read nor deleted, and plaintext `enbox:auth:*` values fail as invalid envelopes. No migration path. |
| Locked `SecretStore.get` | absent → undefined and expired → purged while locked | every locked `get` fails with `AgentVaultLocked`, including absent, expired, and malformed entries |

The blank-new-password, lock-on-failure, DID-validation, work-factor, and
fresh-restore divergences are accepted and must not be "fixed" toward TS.

## Stable error codes

Codes cross `enbox-ffi` unchanged as `EnboxError::Agent { code, detail }`:

| Class | Code |
| --- | --- |
| uninitialized | `AgentVaultUninitialized` |
| already initialized | `AgentVaultAlreadyInitialized` |
| locked | `AgentVaultLocked` |
| invalid password | `AgentVaultInvalidPassword` |
| blank password | `AgentVaultBlankPassword` |
| invalid backup | `AgentVaultInvalidBackup` |
| corrupt stored vault value | `AgentVaultCorrupt` |
| phrase mismatch | `HD_IDENTITY_VAULT_RECOVERY_PHRASE_MISMATCH` |
| invalid phrase | `AgentIdentityInvalidMnemonic` |
| DID creation, resolution, publication | `AgentIdentityDidError` |
| store or work-factor failure | `AgentVaultError` |
| bad secret envelope | `AgentSecretInvalidEnvelope` |

Other agent codes (`AgentIdentityInvalidKeyMaterial`, …) pass through on the
same path. `restore_vault` reports malformed backup JSON as
`AgentVaultInvalidBackup`, not a JSON error, so the lock-on-failure rule still
runs.

## FFI boundary

Hosts drive one shared vault through `EnboxCore`: `initialize_vault`,
`unlock`, `unlock_with_reason`, `lock`, `change_password`,
`reset_password_with_recovery_phrase`, `backup_vault`, `restore_vault`,
`vault_status`, `current_agent_identity`. There is no passwordless unlock and no
shadow lock flag: every lock-gated surface reads the vault's own state, so a
freshly opened core is locked until initialized, restored, or unlocked with the
password. `vault_status` reports `{initialized, locked, lastBackup, lastRestore, derivationVersion?}`
(omitting `derivationVersion` when absent), and `initialize_vault` /
`initialize_agent_identity` accept an optional `derivationVersion` (`1` or `2`,
validated before any write or network call).
An unlock reason is recorded only after a successful password unlock and cleared
on lock or any locking failure. A malformed reset request body is a JSON error;
the vault is untouched.

One live core per database path is enforced in-process (normalized aliases
included), rejected as `AgentVaultError`; drop releases the path after store
teardown. In-memory cores are independent. Two vault instances over one store
remain unsupported, as in TS: each would hold its own CEK, and a restore in one
would leave the other unlocked with a stale key.

## Interop fixtures

- `fixtures/interop/vault-jwe.json`: pinned TS values (`p2c = 1`) for the three
  at-rest entries, a data JWE, a binary JWE, and the derived URI.
- `fixtures/interop/vault-secret-envelope.json`: pinned TS credential envelope.
- `fixtures/interop/vault-backup.json`: pinned TS `HdIdentityVault.backup()`
  payload (`p2c = 1`), restored in Rust onto both fresh and initialized stores.
- `fixtures/interop/vault-phrase-acceptance.json`: 18-row pinned TS
  `validateMnemonic(phrase, englishWordlist)` acceptance table.
- `crates/dwn-rs-agent/tests/fixtures/vault-jwe-rust-to-ts.json`,
  `vault-secret-rust-to-ts.json`, and `vault-backup-rust-to-ts.json`:
  Rust-emitted counterparts.
- Rust proves the TS→Rust direction (`tests/vault_jwe_interop.rs`,
  `tests/vault_secret_store.rs`, `tests/vault_lifecycle.rs`,
  `tests/api_conventions.rs`); TS proves the Rust→TS direction with optional
  `tools/conformance/typescript-vault-{jwe,secret,backup,phrase}.test.ts`
  runners against an `ENBOX_TS_ROOT` checkout (including `isPortableDid` and the
  agent document shape).
- Provenance is checked by `tools/conformance/check-fixture-provenance.sh`
  against `.enbox-version` in `enbox-rust-core`.
