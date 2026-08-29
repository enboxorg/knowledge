---
domain: conformance
kind: guide
reviewed: 2026-08-28
---

# Permissions Conformance

Use with `dwn/permissions.md` and `dwn/authorization.md`.

## Grant creation and scope

- [ ] Permission Grant records validate against the Permissions Protocol.
- [ ] Grantor/grantee identity is interpreted correctly.
- [ ] Interface, method, protocol, context, and other scope restrictions are enforced.
- [ ] A grantee cannot widen a grant through message construction.
- [ ] Delegated grants preserve the principal/Author semantics required by the grant chain.

## Time, expiry, and revocation

- [ ] Grant start/expiry boundaries are evaluated consistently.
- [ ] Revocation records are recognized.
- [ ] Historical admission evaluates revocation relative to the operation timestamp where required.
- [ ] Live/current authorization does not continue solely because an older message was once valid.

## Discovery

- [ ] Authorized parties can discover relevant grants through the defined query surface.
- [ ] Unauthorized callers cannot enumerate hidden grants merely by guessing identifiers.

## Negative cases

- [ ] Wrong grantee is rejected.
- [ ] Wrong method/interface is rejected.
- [ ] Wrong protocol/context is rejected.
- [ ] Expired or not-yet-active grant is rejected.
- [ ] Revoked-at-operation-time grant is rejected.
- [ ] Missing referenced grant is classified consistently as incomplete/not found according to the operation contract.
