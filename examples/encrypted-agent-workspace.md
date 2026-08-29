---
domain: examples
kind: guide
reviewed: 2026-08-28
---

# Worked Example: Encrypted Workspace with Delegated Agent

## Goal

Model a private collaborative workspace where:

- workspace content is encrypted,
- human members have contextual access,
- an AI/software agent can act for Alice under narrowly delegated authority,
- removing a member affects future authorization and future key delivery without pretending to erase historical knowledge.

This example combines protocol roles, encryption, delegation, offline sync, and least-privilege design.

## Actors

- **Alice** — workspace owner and grantor.
- **Bob** — human workspace member.
- **Alice's agent** — separate DID/signing identity that may act semantically as Alice only within a bounded delegated grant.
- **Other principals** — no authority.

The agent is intentionally not given Alice's private key.

## Domain model

```text
workspace
├── member        ($role)
├── document
├── task
└── agent-log
```

`agent-log` is optional application audit state. It is not a substitute for signed DWN messages, but it can capture higher-level agent intent/result metadata useful to Alice.

## Core authority model

There are three separate capability questions:

```text
1. May this principal perform the DWN operation?
2. If delegated, whose semantic authority is being exercised?
3. Does the principal possess key material required to decrypt/encrypt data?
```

Do not collapse them.

The agent can be:

```text
Signer = did:example:alice-agent
Author = did:example:alice
```

when a valid delegated author grant permits the operation.

That does not automatically give the agent every encryption key Alice possesses.

## Protocol tree

```text
workspace
├── member
├── document
├── task
└── agent-log
```

Protocol URI:

```text
https://example.com/protocols/encrypted-workspace
```

## Authorization matrix

| Operation | Alice | Bob member | Alice agent with bounded delegation | Other |
|---|---:|---:|---:|---:|
| Create workspace | yes | no | no | no |
| Manage membership | yes | no | preferably no | no |
| Read workspace data | yes | yes | only if granted + key supplied | no |
| Create document | yes | yes | yes if delegated | no |
| Update Alice-owned document | yes | policy-dependent | yes if delegated | no |
| Create task | yes | yes | yes if delegated | no |
| Delete workspace | yes | no | no | no |
| Rotate/provision keys | yes/control-plane service | no by default | no by default | no |

The agent should not receive broad membership-management or tenant-wide power merely because it needs to draft documents.

## Illustrative protocol definition

Conceptually:

```json
{
  "protocol": "https://example.com/protocols/encrypted-workspace",
  "published": false,
  "types": {
    "workspace": { "dataFormats": ["application/json"] },
    "member": { "dataFormats": ["application/json"] },
    "document": { "dataFormats": ["application/json"] },
    "task": { "dataFormats": ["application/json"] },
    "agent-log": { "dataFormats": ["application/json"] }
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
          { "role": "member", "can": ["create", "read", "update"] }
        ]
      },
      "agent-log": {
        "$actions": [
          { "who": "author", "of": "workspace", "can": ["create", "read"] }
        ]
      }
    }
  }
}
```

Encryption policy/control directives are intentionally not copied here as if the draft and current Enbox control plane were identical. The current TypeScript implementation and draft have a known divergence in encryption-control structure. Use `dwn/encryption.md`, `enbox/encryption.md`, and the tracked spec issues before producing production configuration.

## Delegated agent grant

Alice issues a delegated author grant to the agent with a narrow scope.

Conceptually permit:

```text
protocol: encrypted-workspace
context: W1
paths:
  - workspace/document
  - workspace/task
operations:
  - create
  - update (where Alice would be authorized)
expiry: bounded
```

Explicitly exclude:

```text
workspace/member
workspace deletion
unrelated protocols
unrelated contexts
```

The grant should be discoverable/verifiable through the DWN permission/delegation model and bound into the agent-authored message authorization as required by current semantics.

## Record walkthrough

### 1. Alice creates W1

Alice creates the workspace and a member role Record for Bob.

### 2. Encryption control state is provisioned

The system establishes whatever current encryption audience/key-delivery Records are required for Alice and Bob under the active Enbox/DWN encryption model.

Important separation:

```text
Bob role Record       -> authorization capability
Bob encryption state  -> decryption capability
```

Neither automatically substitutes for the other.

### 3. Alice delegates document/task work to her agent

The agent receives the delegated grant, but not necessarily every workspace key.

There are two reasonable product modes:

#### Mode A: agent may read content

Provision the agent enough encryption material to decrypt the paths it must reason over.

Risk: the agent now possesses plaintext/key capability. Treat this as a real disclosure boundary.

#### Mode B: agent may write from external/plaintext inputs but not read existing workspace content

Do not provision read keys. The agent can only perform operations compatible with what it can construct without decryption.

This is materially safer when the task permits it.

### 4. Agent writes D1 as Alice

Cryptographically:

```text
Signer = AliceAgent
```

Semantically, with a valid delegated author grant:

```text
Author = Alice
```

Protocol authorization evaluates the effective Author where the protocol defines author-based actor semantics.

The message still records/proves the actual signer and delegated grant relationship.

### 5. Bob reads D1

Bob must satisfy both:

```text
role/read authorization
and
decryption key possession
```

A bug in either layer can produce either unauthorized disclosure or confusing inaccessible-but-authorized state.

## Key lifecycle when Bob leaves

Alice removes Bob's member role.

For future confidentiality, the system should consider:

1. stop delivering future key material to Bob,
2. rotate relevant audience/content keys if the encryption model requires it,
3. encrypt future Records under the new authorized audience state,
4. retain/recover historical key material for principals who should still read old data,
5. avoid claims that Bob's old plaintext or keys have been remotely erased.

Authorization revocation and cryptographic forward exclusion are related but separate processes.

## Agent revocation

If Alice revokes the delegated grant:

- newly unauthorized agent operations should fail admission according to grant temporal semantics,
- the agent may still possess previously disclosed plaintext/keys,
- if compromise is suspected, rotate encryption material the agent possessed,
- durable audit should preserve evidence of previously valid signed actions.

Do not "solve" agent revocation merely by deleting the local grant object while replicas can still encounter historical messages.

## Query patterns

Documents in W1:

```text
protocolPath = workspace/document
context scoped to W1
```

Agent-authored operational audit can be reconstructed from signed messages/signers, while optional `agent-log` Records can add application intent such as:

```json
{
  "task": "Draft launch plan",
  "resultRecordId": "D1",
  "model": "application-defined identifier"
}
```

Do not put secrets, prompts, or decrypted content into queryable tags unless disclosure is explicitly acceptable.

## Offline scenario

The agent works on a laptop while disconnected and signs operation A1 under a delegated grant. Alice later revokes the grant before A1 reaches another DWN.

Admission must follow the protocol's historical grant semantics, using the signed operation timestamp and grant validity rules rather than a simplistic "grant is revoked now, therefore all old actions were invalid" rule.

For live ongoing subscriptions/capabilities, current authority may need re-evaluation.

This distinction is important for durable signed operations versus continuing access.

## Replication and dependencies

A replica may receive D1 before it has:

- the delegated grant,
- governing protocol configuration,
- role/control Records,
- encryption-control dependencies.

The replication engine should classify missing dependencies as repairable when appropriate, retrieve them, and then re-run normal admission.

Never insert D1 directly into trusted state just because a peer says it is valid.

## Threat analysis

### Overbroad agent delegation

Risk: agent can modify membership, unrelated contexts, or tenant-wide data.

Mitigation: narrow protocol/context/path/operation scope and bounded lifetime.

### Agent gets unnecessary read keys

Risk: data exfiltration boundary expands from Alice to agent runtime/vendor.

Mitigation: provision only the encryption capability necessary for the task.

### Bob removed but still has old key

Expected limitation: historical disclosure cannot be revoked cryptographically after Bob learned the key/plaintext.

Mitigation: rotate for future content; communicate product semantics accurately.

### Authorization says yes but decrypt fails

Possible during key provisioning lag/recovery failure.

Mitigation: treat authorization state and key-delivery state as separately observable dependencies.

### Decrypt succeeds but DWN read is unauthorized

Possession of bytes/keys outside the DWN cannot be undone by access control. Inside the DWN, never use possession of encryption material as a substitute for authorization.

### Cross-context grant use

Agent delegated for W1 must not use that grant in W2.

## Schema/protocol evolution

Suppose v2 adds `summary` Records writable by agents but not human members.

A safe rollout should:

1. install the new protocol configuration,
2. update delegated-grant scopes explicitly,
3. update encryption audience policy if needed,
4. test old Records under historical config,
5. avoid silently expanding an existing grant to the new path unless that is explicitly intended by scope semantics.

Delegation scopes should be reviewed whenever protocol structure grows.

## Test plan

```text
[ ] Alice can create W1 and manage membership
[ ] Bob role authorizes only W1 content
[ ] Bob needs both read authorization and correct key material
[ ] agent can perform only delegated W1 document/task operations
[ ] agent Signer differs from semantic Author under delegation
[ ] agent cannot manage membership or W2
[ ] expired/revoked grant behavior matches historical authorization semantics
[ ] missing delegated-grant dependency is repaired before admission
[ ] removing Bob stops future authorization according to policy
[ ] future encryption key delivery excludes removed Bob
[ ] old plaintext/key possession is not misrepresented as revocable
[ ] agent without read key cannot decrypt existing content
[ ] agent with read key is treated as a genuine disclosure boundary
[ ] arrival-order permutations of role/grant/content dependencies converge
[ ] duplicate replication is idempotent
[ ] protocol v2 does not silently broaden old delegation scope
```

## What this example teaches

- Agent identity should be separate from the human principal's private key.
- Delegated semantic authorship is not the same as cryptographic signing identity.
- Authorization capability and encryption capability must be modeled separately.
- Least privilege applies to both operations and keys.
- Revoking a role/grant controls future authority; key rotation controls future cryptographic access; neither erases already disclosed information.
- Replicated delegated/encrypted Records still pass through normal dependency-aware admission.
