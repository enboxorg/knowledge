---
domain: dwn
kind: normative
spec: https://dwn-spec.pages.dev/
spec-reviewed: 2026-08-28
---

# Authorization

## Core model

Authentication proves who signed a message. Authorization decides whether that effective principal may perform the requested operation.

Keep these concepts separate:

```text
Signer   = DID/key proven by JWS verification
Author   = semantic principal represented by the operation
Tenant   = DID whose DWN is processing the message
Authority = mechanism that permits the operation
```

Without author delegation, `Author == Signer`. With author delegation, the delegate signs while acting as the grantor, so `Signer != Author`.

## Authorization order

A useful model for DWN admission is:

1. verify the message signature and signed commitments;
2. resolve author delegation when present;
3. determine whether the effective Author is the tenant;
4. otherwise evaluate an invoked Permission Grant if present;
5. otherwise evaluate protocol authorization where applicable.

The exact method controls which branches are legal. Do not assume every message type supports every authority mechanism.

## Delegation

An author-delegated grant changes the semantic actor. The delegate signs the message, but protocol rules that refer to `author` evaluate the grantor represented by the delegated grant.

This differs from an ordinary Permission Grant:

```text
direct Permission Grant
    Bob signs as Bob
    grant supplies authority

author delegation
    Bob signs
    effective Author is Alice
```

This distinction matters for protocol rules such as `who: author`, update/co-update actions, and author-based actor chains.

## Permission Grant invocation

A Permission Grant is an authorization capability, not identity substitution. Grant validation typically binds:

- grantor and grantee,
- message timestamp against grant lifetime,
- revocation state at the relevant authorization time,
- interface and method,
- Records selectors such as protocol, protocol path, context, and conditions.

A later revocation is not automatically retroactive to an operation that was valid at its signed historical timestamp.

## Protocol authorization

Protocol authorization evaluates the governing Protocol Definition and the Record's position in its protocol/context graph.

Common inputs include:

- effective Author,
- recipient,
- action (`create`, `update`, `co-update`, `delete`, `co-delete`, `prune`, `co-prune`, `read`, etc.),
- `who`, `of`, and role rules,
- ancestor/parent Records,
- protocol roles and context prefixes,
- cross-protocol composition where `uses`/`$ref` applies.

Protocol authorization is state-aware: role assignments, parent chains, and governing Protocol Configure messages may be dependencies required to evaluate the operation.

## Historical authorization

DWN authorization often evaluates authority at the message's signed time rather than current wall-clock time. This is especially important for durable replication: a valid historical operation should not become invalid merely because a Permission Grant was revoked later.

Live capabilities are different. Long-lived subscriptions may require current authorization to be re-evaluated while the stream remains open.

## Common traps

- Do not use the JWS signer as the protocol Author when author delegation is present.
- Do not treat a direct Permission Grant as identity delegation.
- Do not evaluate historical grant validity using only current wall-clock time.
- Do not assume successful signature verification implies protocol authorization.
- Do not bypass authorization for replicated messages; replication changes transport, not authority.