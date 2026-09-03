---
domain: implementation
kind: guide
reviewed: 2026-09-03
---

# Error Model

A DWN engine's error model is part of interoperability because callers, sync engines, and agents need to know whether to retry, repair, or stop.

## Useful classes

At minimum distinguish:

- malformed/unsupported message,
- integrity or signature failure,
- authorization failure,
- semantic conflict/state rejection,
- repairable incomplete dependency,
- not found,
- transient storage/transport failure,
- internal implementation failure.

## Properties

Errors should be:

- stable enough for machine handling,
- specific enough to identify the failed semantic stage,
- safe to expose without leaking sensitive authorization state unnecessarily,
- independent of incidental database exception strings.

For covered current-Enbox parity failures, the public boundary carries a structured error code plus optional structured information (`ENBOX-ERR-001`). Internal code should use typed errors/outcomes and perform the status/wire mapping once at the boundary. Unknown storage or implementation errors remain internal/transient failures; they must not be converted into client validation errors by string matching.

## Replication implications

A sync engine needs to know whether a destination result means:

```text
retry later
fetch dependency then retry
permanently reject this message
already have it / idempotent success
```

Do not advance durable sync progress merely because an error was returned; classify whether the message has actually settled according to the replication contract.

## Security boundary

Avoid turning authorization errors into an oracle that reveals existence of hidden Records, role membership, grants, or encrypted metadata beyond what the requesting principal is allowed to know.

See `implementation/message-processing-pipeline.md` and `implementation/dependency-resolution.md`.
