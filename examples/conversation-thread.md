---
domain: examples
kind: guide
reviewed: 2026-08-28
---

# Worked Example: Conversation Thread

## Goal

Model a private conversation thread with explicit participants and append-oriented messages that may be authored offline and synchronized later.

This example emphasizes context-scoped participant authority and the difference between message ordering, delivery ordering, and DWN conflict semantics.

## Actors

- **Thread creator** — creates the conversation and participant assignments.
- **Participant** — can read the thread and append messages.
- **Non-participant** — has no thread access.

Assume Alice creates a thread with Bob.

## Domain model

```text
thread
├── participant ($role)
└── message
```

A `message` is a separate immutable-ish domain event rather than repeatedly updating one giant conversation Record.

That design gives each message:

- stable authorship,
- independent delivery/retry identity,
- simple append lifecycle,
- natural pagination/query behavior.

## Authorization matrix

| Operation | Creator | Participant | Other |
|---|---:|---:|---:|
| Create thread | yes | no | no |
| Add/remove participant | yes | no | no |
| Read thread | yes | yes | no |
| Create message | yes | yes | no |
| Read messages | yes | yes | no |
| Edit message | no by default | no by default | no |
| Delete own message | optional policy | optional policy | no |

This example chooses append-only messages. If editing is required, define that lifecycle explicitly instead of assuming messages can be mutated.

## Protocol tree

```text
thread
├── participant
└── message
```

Protocol URI:

```text
https://example.com/protocols/conversation
```

## Illustrative protocol definition

```json
{
  "protocol": "https://example.com/protocols/conversation",
  "published": false,
  "types": {
    "thread": { "dataFormats": ["application/json"] },
    "participant": { "dataFormats": ["application/json"] },
    "message": { "dataFormats": ["application/json"] }
  },
  "structure": {
    "thread": {
      "$actions": [
        { "who": "author", "can": ["create", "read", "delete"] }
      ],
      "participant": {
        "$role": true,
        "$actions": [
          { "who": "author", "of": "thread", "can": ["create", "read", "delete"] }
        ]
      },
      "message": {
        "$actions": [
          { "role": "participant", "can": ["create", "read"] },
          { "who": "author", "of": "thread", "can": ["create", "read"] }
        ]
      }
    }
  }
}
```

Validate exact role/action syntax against the current draft/runtime. The design intent is contextual participant authority.

## Message payload

```json
{
  "text": "Are we still on for 3pm?",
  "clientMessageId": "01J..."
}
```

A client-generated identifier inside payload can help application deduplication across UI retries, but it does not replace DWN message/Record identity.

## Record walkthrough

### 1. Alice creates thread T1

```text
recordId: T1
protocolPath: thread
contextId: T1
author: Alice
```

### 2. Alice creates Bob participant role P-Bob

```text
protocolPath: thread/participant
parentId: T1
recipient/role-holder: Bob
```

### 3. Alice and Bob append messages

Alice creates M1, Bob creates M2.

Each message is a child of T1 and invokes the relevant participant authority.

## Ordering model

Do not use DWN arrival order as conversation order.

There are at least three order concepts:

```text
messageTimestamp / signed application time
transport arrival time
application display order
```

They are not guaranteed to be identical.

For human chat, a reasonable UI may primarily sort by signed timestamp and use stable tie-breaking while still tolerating late arrivals. If stronger causal/conversation ordering is required, model causal references or sequence state explicitly at the application layer.

DWN does not magically provide total-order consensus across offline writers.

## Offline scenario

Alice and Bob both go offline after seeing M1.

```text
Alice creates M2 at 10:00:05
Bob   creates M3 at 10:00:04
```

M2 reaches server first; M3 reaches later.

The UI should eventually display the chosen stable application order without assuming transport arrival defines chronology.

Because M2 and M3 are independent Records, they do not conflict as competing versions of one Record.

This is a useful modeling property: append events avoid unnecessary same-Record conflicts.

## Participant removal

Alice removes Bob from T1.

Effects to reason about:

- future participant-authorized writes,
- Bob's ability to query/read future content,
- offline messages Bob signed before/around removal under temporal authorization semantics,
- encryption/key rotation if the thread is encrypted,
- already downloaded message history.

Again, removal is not retroactive erasure of data Bob already possesses.

## Query patterns

List messages for T1:

```text
protocol = conversation
protocolPath = thread/message
context scoped to T1
```

Pagination should use stable query semantics from the runtime; do not assume client-side offset pagination remains stable while new messages arrive.

List participant state:

```text
protocolPath = thread/participant
context scoped to T1
```

## Notifications versus source of truth

A live subscription can reduce latency, but the durable message/query path remains the source of truth for recovery.

Client pattern:

```text
subscription wakes client
    -> query durable state/feed
    -> process missing messages
    -> advance local checkpoint
```

Do not make correctness depend on receiving every transient subscription notification.

## Encryption extension

A private conversation commonly requires encrypted message payloads.

Authorization answers who may access through the DWN; encryption answers who can derive plaintext.

Participant removal may require new key material for future messages if the product wants forward exclusion. It cannot revoke message plaintext or keys already obtained.

## Failure cases

### Message before participant dependency

During replication, a message may arrive before the role Record proving participant authority. Dependency resolution should repair this ordering rather than permanently misclassifying a valid message.

### Duplicate message delivery

Idempotent.

### Participant from wrong thread

Must not authorize T1 messages.

### Subscription loss

Client must recover through durable query; no message should be permanently missed solely because a websocket/event notification was lost.

### Clock skew

Clients should not treat timestamp ordering as perfect physical truth. Large skew may require UX or server validation constraints.

## Delete semantics

If "delete message" is supported, decide what it means:

- hide from future authorized queries?
- retain tombstone/history?
- remove attachment data when safe?
- does it affect replies/references?

Do not market deletion as remote erasure from participant devices.

## Test plan

```text
[ ] creator can create T1 and assign Bob participant role
[ ] Bob participant can append/read messages in T1
[ ] Bob role in T1 cannot authorize another thread
[ ] non-participant cannot append/read
[ ] independent offline messages both survive and converge
[ ] delivery order does not define display/correctness semantics
[ ] duplicate message delivery is idempotent
[ ] missing participant dependency is repairable
[ ] lost subscription notification is recovered by durable query
[ ] participant removal affects future authority correctly
[ ] historical valid messages remain verifiable after later role changes
[ ] encrypted variant separates authorization and key possession
```

## What this example teaches

- Append events are often better modeled as independent Records than updates to one shared Record.
- Contextual roles fit conversation participation naturally.
- Transport arrival is not application chronology.
- Subscriptions are latency optimization, not the sole durable delivery mechanism.
- Membership removal and information erasure are different concepts.
