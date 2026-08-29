---
domain: builders
kind: guide
reviewed: 2026-08-28
---

# Schema and Protocol Evolution

## Treat protocol versions as compatibility boundaries

Changing a protocol definition can change validation, hierarchy, authorization, and interoperability. Do not treat it like editing an application-side JSON schema in place.

Before changing a deployed protocol, decide whether the change is:

- backward-compatible interpretation,
- additive new path/schema/tag,
- authorization change,
- structural/context change,
- incompatible new protocol version.

## Preserve old data semantics

Existing Records were created under the protocol state that admitted them. Avoid migrations that assume every historical Record can be reinterpreted safely under new rules.

If old and new records must coexist, make the compatibility model explicit in application code and queries.

## Prefer additive evolution

Where practical:

- add new paths rather than repurposing old ones,
- add optional fields rather than changing existing meanings,
- introduce new role types rather than broadening an old role ambiguously,
- preserve stable Record identifiers/references.

## Authorization changes need special care

A protocol evolution that changes who can create/read/update/delete data is a security migration, not only a schema migration.

Review:

- existing role Records,
- existing grants/delegations,
- historical Records,
- subscription visibility,
- encrypted key distribution.

## Migration records versus rewriting history

Prefer explicit migration/new-version Records over rewriting signed historical facts merely to fit a new model. DWN data has provenance; preserve it when the old fact is still meaningful.

## Client compatibility

Plan how clients discover which protocol/version they understand. Do not assume every device updates simultaneously.

An older client should fail predictably when it encounters unsupported paths or versions rather than corrupting data by interpreting them as an older shape.

## Query migration

When tags or paths evolve, review all discovery queries. A schema migration is incomplete if new Records are valid but existing clients can no longer find the right population.

## Test matrix

For each evolution, test:

- old client + old data,
- new client + old data,
- new client + new data,
- old client encountering new data,
- offline old client reconnecting after protocol change,
- authorization changes with pre-existing roles/grants,
- sync between replicas containing mixed versions.