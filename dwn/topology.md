---
domain: dwn
kind: normative
spec: https://dwn-spec.pages.dev/
spec-reviewed: 2026-08-28
divergences:
  - enboxorg/dwn-spec#41
---

# Topology

## DWN service endpoints

A DID can advertise one or more DWN endpoints through a `#dwn` service entry. Endpoint discovery is a routing concern layered on top of DID resolution.

Multiple full endpoints for the same tenant are equivalent replicas from the client's perspective. Implementations should support failover rather than assuming one canonical server.

## Full and cache endpoints

Endpoint metadata can distinguish durable full nodes from cache/relay nodes.

A full endpoint retains the tenant's messages and data according to DWN retention rules. A cache endpoint can be storage-constrained and may retain message envelopes while treating data as evictable or best-effort.

Clients should prefer full endpoints for reads when durability matters.

## Forwarding

After accepting a signed write/delete operation, a provider can forward that same original message to the tenant's peer DWN endpoints.

Forwarding must not re-author or mutate the message. The receiving endpoint independently admits it through normal DWN validation.

Forwarding is a latency/availability mechanism, not a replacement for durable replication.

## Read proxying

A node can know a RecordsWrite envelope while lacking its data bytes. It may proxy a RecordsRead to a peer endpoint, return the data transparently, and optionally cache the result.

Failure to locate data should be distinguishable from absence of the Record envelope.

## Participant delivery

Protocol delivery to other tenants is different from forwarding between replicas of the same tenant:

```text
forwarding
    same tenant -> another endpoint

delivery
    origin context -> participant tenant(s)
```

Participant delivery remains ordinary signed-message transport at the destination and does not create provider trust.

## DID-as-service-endpoint

The draft permits a DWN service endpoint to reference another DID and defines recursive resolution with a bounded depth. Current implementation support is still being aligned; see `enboxorg/dwn-spec#41`.

## Common traps

- Do not mix signature-key resolution with endpoint discovery.
- Do not treat forwarded messages as trusted replication writes.
- Do not confuse same-tenant forwarding with participant delivery.
- Do not assume cache endpoints retain all Record data.
- Do not rely on forwarding alone for eventual convergence; durable sync remains the backstop.
