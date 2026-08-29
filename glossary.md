# Glossary

## Author
The semantic principal on whose behalf a DWN message acts. With author delegation, the Author can differ from the cryptographic Signer.

## Signer
The DID/key that produced the message's JWS signature.

## DWN message
A signed description of an operation against a DWN interface and method.

## Record
Logical application state derived from one or more Records messages. A Record is not itself a single stored row or message.

## Record ID
Stable identifier for a logical Record, derived from the initial write semantics.

## Entry ID
Identifier associated with a specific RecordsWrite state entry; used as part of deterministic ordering.

## Context ID
Identifier for a protocol record context. A root protocol Record uses its Record ID as its context ID; descendants extend the context chain.

## Initial Write
The first RecordsWrite for a Record. It establishes immutable Record properties and is retained as lifecycle evidence even when later states replace the visible write.

## Tombstone
A retained RecordsDelete state representing terminal deletion of a Record.

## Permission Grant
A DWN capability record authorizing a grantee to perform a scoped operation. Possessing a grant does not itself provide encryption keys.

## Protocol Role
A protocol-defined role represented by Records that can participate in protocol authorization rules.

## Progress Token
Source-local durable-feed cursor used to resume `MessagesQuery` reconciliation. It is a high-water position, not a causal timestamp.

## Dependency Closure
The set of protocol configurations, initial writes, parents/ancestors, roles, grants, encryption-control records, cross-protocol references, and/or data required before a replicated message can be admitted.

## Fingerprint
A compact set-convergence signal over retained message CIDs for a canonical replication scope. It verifies convergence; it does not identify the missing messages by itself.

## Governing Protocol Configuration
The protocol definition selected for validation at the relevant governing timestamp.

## Core Protocol
A protocol with implementation-level lifecycle hooks in Enbox, such as Permissions and current encryption-control/key-delivery functionality.
