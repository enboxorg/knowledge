# ADR 0004: Latest Record State Transitions Are Store-Owned and Atomic

- Status: Accepted for current Enbox architecture
- Date: 2026-08-28

## Context

Records admission decides which retained messages represent current logical state. If the handler performs message insertion, latest-state index mutation, feed emission, and displaced-message cleanup as independent writes, readers or a crash can observe an impossible intermediate state.

Current TypeScript Enbox addresses this by handing the complete latest-state transition to storage as one operation. Rust implemented this decision for Records and ProtocolsConfigure under `enbox-rust-core#189`; remaining work should test and preserve the decision rather than reintroducing independently committed handler mutations.

## Decision

The handler determines whether a state transition is valid and which messages are winners/retained/displaced. The storage layer owns the indivisible persistence of that transition, including the corresponding durable-feed effect.

For Records conflict resolution, the target convergence model includes delete-wins tombstone ordering so identical valid message sets converge independently of arrival order.

## Consequences

- Readers must not observe both old and new latest-state winners simultaneously.
- Crash/reopen must not leave latest-state indexes and the durable feed describing different accepted states.
- Data cleanup may follow the committed state transition; failure should bias toward orphaned data rather than a live message whose required data has already been destroyed.
- Storage conformance tests must cover real file-backed crash/reopen boundaries, not only in-memory behavior.

## Related

- `enbox-rust-core#169` — durable backend hardening
- `enbox-rust-core#189` — convergent Records admission and atomic latest-state semantics
