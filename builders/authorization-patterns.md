---
domain: builders
kind: guide
reviewed: 2026-08-28
---

# Authorization Patterns

## Start with the semantic actor

Do not design authorization around "who signed the request" alone. Delegation can make the Signer and semantic Author different identities.

Ask which actor the application rule actually means:

- tenant/owner,
- Record author,
- recipient,
- protocol role holder,
- Permission Grant grantee,
- delegate acting for a principal.

Then choose the mechanism that expresses that relationship.

## Mechanism selection

| Requirement | Prefer |
|---|---|
| One identity owns/creates its own Record | author-based rule |
| A known counterparty needs access | recipient-based rule |
| Membership in a protocol context grants authority | protocol role |
| Authority must be granted outside protocol rules | Permission Grant |
| Another signer must act as the principal/Author | delegated grant |

Do not use a delegated author grant merely to provide ordinary access. Delegation changes whose authority the signer is exercising.

## Author versus recipient

Author rules are provenance-oriented: who created/controls the logical Record under the protocol rule.

Recipient rules express directed access to a specific identity. A recipient is not automatically the author and does not automatically gain update/delete rights unless rules grant them.

## Roles for contextual authority

Use roles when authority depends on membership/position inside a protocol context: workspace admin, conversation participant, project editor.

Roles should usually be scoped narrowly enough that holding a role in context A does not accidentally authorize context B.

## Permission Grants for explicit capability

Use grants when authority is not naturally encoded by the application protocol, especially administrative access, tooling, delegated services, or cross-application capabilities.

Scope grants tightly by interface/method/protocol/context where possible. Treat revocation/expiry semantics as part of the design, not an afterthought.

## Historical versus continuing authority

Admission of a signed operation and continuing access are different questions.

A historically valid write should not become invalid simply because a grant was later revoked. A live subscription or future operation may need current authority.

Design UI/service behavior accordingly: "this operation was valid then" is distinct from "this actor may still do this now."

## Avoid authority encoded only in payload data

If a field such as `role: admin` exists only inside arbitrary Record data, the DWN authorization layer cannot safely treat it as capability state unless protocol semantics explicitly bind authority to it.

Use protocol roles or grants for authority-bearing state.

## Review questions

- Which semantic identity is each rule about?
- Can a delegate accidentally gain authority as itself rather than the principal?
- Does a role escape its intended context?
- Is a grant broader than the product requirement?
- What happens after role deletion, grant revocation, or expiry?
- Are read/query/subscribe disclosure rules aligned, or can one path expose more than another?