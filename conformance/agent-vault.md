---
domain: conformance
kind: guide
reviewed: 2026-11-25
---

# Agent Identity Vault Conformance

Use with `enbox/agent-vault.md`, `enbox/did-dht.md`, and `dwn/encryption.md`.
Every item here is **implementation-parity** Enbox behaviour, not normative DWN
conformance: the DWN draft says nothing about phrases, vault storage, or agent
DID derivation. Cite `ENBOX-AGENT-*` for vault contracts and `DID-DHT-*` for
DID-method wire rules.

Items marked *Rust contract* are stronger than current TypeScript and must not
be relaxed toward it.

## Derivation and phrase acceptance

- [ ] The pinned phrase derives the same CEK, unlock salt, and `did:dht` URI in
      both runtimes (`ENBOX-AGENT-001`).
- [ ] The unlock-salt input is the 33-byte `0x00 || vault public key`, not the
      32-byte compressed key; a 32-byte-input implementation produces a
      different salt and fails the vector.
- [ ] Accepted: 12/15/18/21/24 English wordlist words separated by exactly one
      space with a valid checksum; non-ASCII spaces are accepted after NFKD.
- [ ] Rejected without writes: uppercase, leading/trailing whitespace, repeated
      separators, tab/newline separators, bad checksum, non-wordlist word,
      13 words, empty/whitespace-only phrase (`ENBOX-AGENT-002`).
- [ ] `initialize` without a phrase generates 12 words whose re-derivation
      yields the same DID.
- [ ] `derive_agent_keys_from_phrase` stays pure and works while locked or
      uninitialized.

## At-rest JWE

- [ ] The CEK entry header is exactly `alg`, `enc`, `cty: text/plain`, `p2c`,
      `p2s`; its plaintext is the oct JWK for the CEK (`ENBOX-AGENT-003`).
- [ ] The DID entry header is `dir`/`A256GCM`/`cty: json`; the data JWE header
      has no `cty`.
- [ ] `p2s` equals the derivation salt; `p2c` equals the configured work factor
      on initialize and reset, and is preserved by `changePassword`.
- [ ] Rust opens a TS-produced entry with 12-byte IV, AAD equal to the encoded
      protected header, any `p2c >= 1`, any salt, and any member order; TS opens
      Rust output (`ENBOX-AGENT-004`).
- [ ] Swapping the CEK entry to `dir` or the DID entry to `A128GCM` is rejected;
      `p2c = 0` is corrupt.
- [ ] A present status entry missing `lastBackup` or `lastRestore`, or with wrong
      types, fails every status-reading operation as corrupt and writes nothing.

## Lifecycle and lock gates

- [ ] Fresh store: `{initialized: false, null, null}`, locked, no writes.
- [ ] `initialize` precedence is already-initialized → blank password → invalid
      phrase; failures leave the store byte-identical (`ENBOX-AGENT-005`).
- [ ] `unlock` with a wrong password, from locked or unlocked, ends locked with
      a byte-identical store; success never writes.
- [ ] Locked and uninitialized gates: `getDid`/`encryptData`/`decryptData`/
      `backup`/credential `put`/`get` fail; credential `delete` still works.
- [ ] `changePassword` preserves `p2s`/`p2c` (emitting `cty: text/plain`) and
      the DID/status bytes; a wrong old password ends locked; a blank new
      password is rejected before the in-memory key is dropped.
- [ ] Reset with a mismatched phrase returns
      `HD_IDENTITY_VAULT_RECOVERY_PHRASE_MISMATCH`, leaves the store unchanged,
      and ends locked.
- [ ] A corrupt DID entry fails `getDid` as `AgentVaultCorrupt` while the vault
      stays unlocked and `encryptData` still works.
- [ ] `getDid` returns an isolated copy; mutating it does not affect later
      reads.

## Backup and restore

- [ ] Decoded backup `data` holds `{did, contentEncryptionKey, status}` equal to
      the stored strings and the pre-call status; `size` is the character count;
      `dateCreated` matches `^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$`
      (`ENBOX-AGENT-006`).
- [ ] `lastBackup` equals the returned `dateCreated`; a failing status write
      leaves the status unchanged.
- [ ] Round trip: initialize → backup → `changePassword` → `restore`; the old
      password unlocks and the new one does not.
- [ ] Restore onto a fresh store succeeds and ends unlocked (Rust divergence);
      a failed restore onto a fresh store leaves it uninitialized.
- [ ] Rejected with no write: malformed object, missing/mistyped fields,
      undecodable `data`, status without `initialized: true`, wrong password,
      corrupt backup CEK entry, and a DID entry that does not decrypt or is not
      a usable agent DID (`ENBOX-AGENT-007`).
- [ ] A wrong `size` is accepted; padded base64url is accepted; unknown outer
      JSON members are ignored.
- [ ] After restoring a backup whose `lastBackup` is null, the vault keeps its
      current `lastBackup` value.

## Vault-backed secrets

- [ ] Persisted value is UTF-8 JSON `{jwe, expiresAt?}` with no plaintext and no
      null expiry (`ENBOX-AGENT-008`).
- [ ] TS-produced envelopes decrypt in Rust and Rust-produced envelopes decrypt
      in TS to the recorded plaintext; Rust round trips empty and non-UTF-8
      payloads and preserves or omits `expiresAt` exactly.
- [ ] Locked `put` and `get` fail for absent, live, expired, malformed, and
      legacy keys (Rust contract, `ENBOX-AGENT-013`); locked `delete` reports
      presence without decrypting.
- [ ] Expiry is an instant comparison: `expiresAt - 1ms` returns bytes, equal or
      later purges and returns `None`; an expired entry with a corrupt JWE is
      purged without decrypting; no expiry survives clock advance.
- [ ] Legacy plaintext, invalid UTF-8/JSON, wrong member types, and invalid
      expiry all fail as `AgentSecretInvalidEnvelope` and leave stored bytes
      unchanged; an invalid `put` expiry mutates nothing.
- [ ] `agent:vault:` keys are rejected through the credential seam.
- [ ] Registration-token and delegate-key helpers persist envelopes, not
      plaintext, and propagate lock/legacy errors instead of empty collections.

## Agent DID wiring and publication

- [ ] A production `initialize` yields the `did:dht` vector URI and the
      `DID-DHT-006` document; no production path yields `did:jwk`
      (`ENBOX-AGENT-009`).
- [ ] A fresh `initialize` issues the relay PUT before any store commit; 2xx
      success is the returned sequence, and 409, other non-2xx, transport
      failure, oversize value, or signer failure leave the vault uninitialized.
- [ ] The captured request: gateway identity URL, `application/octet-stream`,
      body `signature || sequence_be || value`, no DID types, gateway as NS
      target, identity key `#0` signature.
- [ ] Reconciliation matrix: ready (with/without replacement, deferred/not),
      not-ready, not-found (with/without endpoints), and resolution failure.
      Only a definitive absent record is not-found; 408/429/5xx, transport
      failure, and an empty or short 2xx body are failures that publish nothing.
- [ ] Reset without endpoints performs no resolution or publication.
- [ ] A republication after resolving sequence N submits strictly more than N,
      including with the clock rolled back behind N.
- [ ] A stale cached document is ignored in favour of a fresh resolution.
- [ ] Non-`#dwn` remote content survives republication; only `#dwn` is
      rewritten.
- [ ] A `PortableDid` written by either runtime imports and is usable for
      signing and key agreement in the other.

## Crash, reopen, and hygiene

- [ ] Fault-inject the commit for initialize, `changePassword`, reset, backup,
      and restore; reopen observes exactly the pre-state; retries succeed
      (`ENBOX-AGENT-010`).
- [ ] A store whose atomic commit is unsupported fails the mutation with no
      partial writes.
- [ ] Every successful mutation survives close and reopen.
- [ ] After a failed unlock, change, reset, or restore: `getDid` and
      `encryptData` fail as locked, and credential `get` fails
      (`ENBOX-AGENT-011`).
- [ ] `Debug`/`Display` of the vault, initialization result, backup, and every
      error from this checklist expose no password, phrase, CEK, salt, or
      private-key bytes.
- [ ] Concurrent unlock/lock/change operations on one shared vault produce a
      coherent final state with no panic, and the store opens with the last
      committed password.
- [ ] A second live core on the same database path (including normalized
      aliases) is rejected; reopening after drop succeeds; in-memory cores are
      independent (`ENBOX-AGENT-012`).
- [ ] `vault_status` reports `{initialized, locked, lastBackup, lastRestore}`
      and `current_agent_identity` is `None` uninitialized, `AgentVaultLocked`
      locked, and the `PortableDid` JSON unlocked.
- [ ] `initialize_vault` output contains no CEK or unlock salt.
- [ ] Every stable code from `enbox/agent-vault.md` is reachable through the FFI
      verbatim, and a malformed `restore_vault` body reports
      `AgentVaultInvalidBackup`, not a JSON error.

## Cross-runtime vectors

- [ ] `fixtures/interop/vault-jwe.json` is generated at `.enbox-version` and
      passes `tools/conformance/check-fixture-provenance.sh`; Rust reads its
      CEK, DID, status, data, and binary values.
- [ ] `crates/dwn-rs-agent/tests/fixtures/vault-jwe-rust-to-ts.json` is opened by
      the pinned TypeScript implementation, including `BearerDid.import` of the
      decrypted `PortableDid`.
- [ ] `fixtures/interop/vault-secret-envelope.json` and
      `crates/dwn-rs-agent/tests/fixtures/vault-secret-rust-to-ts.json` decrypt
      to the recorded plaintext in the opposite runtime.
- [ ] The TS vault values restore on both a fresh and an initialized store with
      the fixture password, and the stored `p2c` matches the fixture.
- [ ] A Rust backup decodes to the TS `IdentityVaultBackupData` shape.
- [ ] The phrase acceptance table is run from the same rows in both runtimes.
