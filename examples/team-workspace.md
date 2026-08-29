---
domain: examples
kind: guide
reviewed: 2026-08-28
---

# Worked Example: Team Workspace

## Goal

Model a collaborative workspace with contextual membership, documents, and tasks.

This example introduces protocol roles and shows why role Records are authorization capability state rather than ordinary content.

## Actors

- **Workspace owner/admin** — creates the workspace and manages membership.
- **Member** — can read workspace content and create/update allowed resources.
- **Non-member** — has no workspace authority.

Assume Alice owns the DWN, creates workspace `W1`, and adds Bob and Carol as members.

## Domain model

```text
workspace
├── member   ($role)
├── document
└── task
```

A membership Record belongs inside the workspace context because the authority is contextual:

```text
Bob is a member of W1
```

must not imply:

```text
Bob is a member of every workspace
```

## Authorization matrix

| Operation | Owner/admin | Member | Other |
|---|---:|---:|---:|
| Create workspace | yes | no | no |
| Add/remove member | yes | no | no |
| Read workspace | yes | yes | no |
| Create document | yes | yes | no |
| Read document | yes | yes | no |
| Update own document | yes | yes | no |
| Delete own document | yes | yes | no |
| Create task | yes | yes | no |
| Update task | yes | yes, if policy allows | no |

This example uses one `member` role. A production system may introduce `admin`, `editor`, or `viewer`, but every additional role multiplies authorization state and tests.

## Protocol tree

```text
workspace
├── member
├── document
└── task
```

Protocol URI:

```text
https://example.com/protocols/workspace
```

## Illustrative protocol definition

Conceptually:

```json
{
  "protocol": "https://example.com/protocols/workspace",
  "published": false,
  "types": {
    "workspace": { "dataFormats": ["application/json"] },
    "member": { "dataFormats": ["application/json"] },
    "document": { "dataFormats": ["application/json"] },
    "task": { "dataFormats": ["application/json"] }
  },
  "structure": {
    "workspace": {
      "$actions": [
        { "who": "author", "can": ["create", "read", "update", "delete"] }
      ],
      "member": {
        "$role": true,
        "$actions": [
          { "who": "author", "of": "workspace", "can": ["create", "read", "delete"] }
        ]
      },
      "document": {
        "$actions": [
          { "role": "member", "can": ["create", "read"] },
          { "who": "author", "can": ["update", "delete"] }
        ]
      },
      "task": {
        "$actions": [
          { "role": "member", "can": ["create", "read", "update"] },
          { "who": "author", "can": ["delete"] }
        ]
      }
    }
  }
}
```

The role/action syntax is illustrative. Verify exact current syntax before use. The durable design requirement is that membership authority is bound to the workspace context.

## Record walkthrough

### 1. Alice creates workspace W1

```text
recordId: W1
protocolPath: workspace
author: Alice
contextId: W1
```

Payload:

```json
{
  "name": "Enbox Planning",
  "description": "Design and launch planning"
}
```

### 2. Alice assigns Bob the member role

Create role Record `M-Bob` under W1.

```text
protocolPath: workspace/member
parentId: W1
recipient: Bob
```

The exact field used to associate the role holder follows protocol role semantics in the current implementation/spec.

The important model is:

```text
M-Bob + W1 context -> Bob has member capability in W1
```

### 3. Bob creates document D1

Bob invokes the contextual `member` role when authorizing the write.

```text
protocolPath: workspace/document
parentId: W1
author: Bob
```

Payload:

```json
{
  "title": "Launch checklist",
  "body": "..."
}
```

### 4. Carol creates task T1

Carol's own membership Record under W1 supplies the relevant role authority.

### 5. Alice removes Bob

Deleting/revoking the member role affects Bob's future authority according to protocol semantics.

Do not use `$recordLimit` or other visibility mechanisms in ways that can hide a role Record while accidentally preserving authorization capability. Current Enbox specifically treats role paths carefully; role state must remain explicit and deterministic.

## Membership lifecycle

Membership changes are security-sensitive events.

When Bob leaves:

- future member-authorized operations should no longer be accepted once the removal governs them,
- previously valid historical Records do not become cryptographically invalid merely because Bob later left,
- previously disclosed plaintext cannot be erased from Bob's devices,
- encrypted future data may require key rotation/reprovisioning if membership controls decryption.

Application UX should distinguish "removed from workspace" from "all past copies erased."

## Role scope isolation

Suppose Alice also owns workspace W2 and Bob is not a member there.

A valid Bob role Record under W1 must never authorize:

```text
workspace/document under W2
```

This should be an explicit conformance test. Context leakage in role authorization is a severe bug.

## Query patterns

List workspaces visible to Alice:

```text
protocol = workspace
protocolPath = workspace
```

List documents in W1:

```text
protocolPath = workspace/document
context scoped to W1
```

List membership Records in W1 for administration:

```text
protocolPath = workspace/member
context scoped to W1
```

Treat role discovery as capability-state discovery, not merely UI member-list data.

## Offline scenario

Bob goes offline while still a member and creates D2. Alice removes Bob before D2 reaches a remote DWN.

The system must evaluate D2 according to the temporal authorization semantics that govern that signed operation; it should not invent a blanket rule like "current membership always decides all historical admission."

This is exactly why operation timestamps, governing protocol state, and role history matter.

The application still needs UX for uncertain local state:

```text
local pending -> synchronized/admitted
              -> rejected/needs user action
```

## Encryption extension

If workspace data is encrypted for members, role authorization and key possession remain distinct.

Membership removal generally requires thinking about:

- stopping future key delivery to Bob,
- rotating keys for future content if forward exclusion matters,
- retaining enough old key material for authorized historical readers,
- not promising retroactive secrecy for plaintext/key material Bob already possessed.

See `examples/encrypted-agent-workspace.md` for the full treatment.

## Failure cases

### Hidden/stale role state

Authorization must not depend on a non-deterministic visibility projection that can make replicas disagree about whether Bob holds the role.

### Role from wrong context

Reject.

### Member role replay after deletion

Historical role messages may be retained for verification/history, but the logical capability state must reflect the governing lifecycle semantics.

### Child arrives before workspace/role dependency

Classify as dependency-repairable when appropriate; fetch dependencies before final admission.

### Two membership updates arrive in different order

Replicas must converge on the same logical role state independent of delivery order.

## Protocol evolution

A v2 protocol might add `admin` and `viewer` roles.

Migration questions:

- Are existing `member` Records grandfathered?
- Which protocol configuration governs old documents?
- Must clients create replacement role Records?
- Does encryption audience mapping change?

Do not silently reinterpret old membership assignments as a new role type.

## Test plan

```text
[ ] Alice can create W1
[ ] Alice can add/remove Bob membership under W1
[ ] Bob member can create/read W1 content
[ ] non-member Carol cannot until role assigned
[ ] Bob W1 role does not authorize W2
[ ] removed Bob cannot perform newly unauthorized operations
[ ] historical valid Bob-authored Records remain verifiable
[ ] different role-update delivery orders converge
[ ] role dependency can be repaired during replication
[ ] duplicate role/content delivery is idempotent
[ ] current visibility projection cannot accidentally grant/revoke role authority
[ ] protocol upgrade preserves correct historical authorization
```

## What this example teaches

- Roles model contextual capability state.
- Role Records need stricter lifecycle thinking than ordinary content.
- Membership removal affects future authority, not information already learned.
- Context isolation must be tested explicitly.
- Offline authorization requires temporal semantics, not naive current-state checks.
