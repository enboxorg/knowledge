---
domain: implementation
kind: guide
reviewed: 2026-08-28
---

# Authorization Evaluation

Authorization should be implemented as a semantic decision over a cryptographically verified message, not collapsed into signature verification.

## Separate identities

At minimum preserve:

- Signer — DID proven by the JWS.
- Author — semantic principal represented by the operation; delegation may make Author differ from Signer.
- tenant — DID whose DWN is processing the message.
- grantee/delegate/role holder — capability-bearing identities used by specific authorization paths.

## Evaluation model

```text
verify signature
→ resolve semantic Author/delegation
→ identify applicable authorization mechanism
→ load referenced grants/roles/protocol state
→ evaluate scope, time, revocation, context, method and protocol constraints
→ permit or reject
```

## Historical versus current state

Be explicit about which checks are evaluated at the signed operation timestamp and which require current authority.

Historical admission of a grant-authorized operation should not become invalid merely because the grant was revoked later if the protocol defines revocation relative to the operation timestamp. Long-lived/live disclosure such as subscriptions may require current reauthorization.

## Avoid

- treating `kid` owner as automatically equal to Author,
- applying current mutable role/protocol state blindly to an exact already-admitted replay,
- letting a broad grant escape its protocol/context/interface/method scope,
- assuming a valid signature implies tenant authorization.

See `dwn/authorization.md`, `dwn/permissions.md`, and `dwn/protocols.md`.
