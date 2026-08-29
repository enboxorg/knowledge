---
domain: learning
kind: guide
reviewed: 2026-08-28
---

# 06 — Build a Protocol

## Read first

- `builders/getting-started.md`
- `builders/designing-a-protocol.md`
- `builders/data-modeling.md`
- `builders/querying-and-indexing.md`
- `builders/testing-and-failure-modes.md`
- one relevant worked example under `examples/`

## Design sequence

Do not begin with protocol JSON. Start with the domain and authority model.

### 1. Name the durable concepts

Identify the application objects that deserve durable Record identities and contexts. Avoid encoding UI screens or RPC operations as protocol paths.

### 2. Draw the context tree

For each root and descendant, decide what context relationship it represents and which queries/authorization rules depend on that hierarchy.

### 3. Write the actor matrix

For each path and operation, list who may create, update, delete, and read. Distinguish author, recipient, contextual role, Permission Grant, and delegated author authority.

### 4. Define lifecycle rules

For every Record type, answer:

- how is it created?
- what is immutable?
- who can update/delete it?
- what happens to descendants when parent/capability state changes?
- what must remain queryable after deletion?

### 5. Design query metadata

Put only intentionally queryable, non-sensitive fields in tags/indexable metadata. Keep high-cardinality or private content in Record data unless the product explicitly accepts leakage.

### 6. Design offline and revocation behaviour

Ask what happens when a client performs an operation using stale authority and later syncs. The answer must come from normal admission rules, not from trusting the source replica/client.

### 7. Add encryption as a separate capability lifecycle

If confidentiality is required, define who receives key material, how membership changes affect future keys, and how key recovery works. Do not treat read authorization as equivalent to decryption.

### 8. Write tests before finalizing the definition

At minimum test:

- allowed and denied actor/operation pairs;
- cross-context role isolation;
- duplicate/reordered delivery where applicable;
- stale offline authority;
- protocol evolution;
- metadata leakage expectations;
- encryption and key-removal scenarios.

## Exercise

Design a lightweight project-review protocol with:

- project owners;
- reviewers scoped to one project;
- review requests;
- comments from reviewers;
- a final decision writable only by the owner;
- offline reviewers;
- optional encrypted review content.

Before writing any JSON, produce:

1. the context tree;
2. actor/authorization matrix;
3. Record lifecycle table;
4. query/tag plan;
5. stale-offline scenario;
6. encryption/key lifecycle;
7. ten high-value tests.

Then compare your reasoning—not syntax—to `examples/team-workspace.md` and `examples/encrypted-agent-workspace.md`.