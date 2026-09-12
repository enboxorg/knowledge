# Semantic Review Report

## Change reviewed

- PR / branch / diff:
- Contract Packet:
- Reviewer session/model:
- Independent of implementer / of packet author: yes / no (say which, and why if no)

## Verdict

`PASS` / `PASS WITH FOLLOW-UP` / `CHANGES REQUIRED`

## Contract fidelity

Judged against the packet's binding section and test matrix, not its reference section.

Summary:

Mechanism deviations reported by the implementer, and whether each preserves the observable
contract:

## Contract soundness

Does the contract solve the stated problem in the concrete scenario, and does it respect the
non-goals? Check this independently of whether the implementation matches the packet.

Did the packet itself hold up? Take each entry in its "Assumptions to challenge" section and say
whether it survived, plus any load-bearing assumption the packet failed to list.

| Assumption | Source | Survived? | Basis |
| --- | --- | --- | --- |
| | | | |

A contract error is `BLOCK` even when the implementation matches the packet exactly.

## Invariant coverage

| Invariant | Contract class | Implementation status | Test evidence | Result |
| --- | --- | --- | --- | --- |
| | | | | |

## Findings

### BLOCK

- None / ...

### GAP

- None / ...

### RISK

- None / ...

### NOTE

- None / ...

## Edge-case review

- [ ] duplicate delivery
- [ ] arrival-order permutations
- [ ] stale historical operations
- [ ] delete/write ordering
- [ ] missing dependencies / repair
- [ ] revocation / expiry
- [ ] protocol versioning
- [ ] replay after mutable auth state
- [ ] crash/reopen
- [ ] convergence
- [ ] checkpoint advancement
- [ ] encryption/key-control dependencies
- [ ] Signer vs Author
- [ ] not applicable cases explained

Notes:

## Architecture / ADR review

- 

## Knowledge impact

- [ ] no drift detected
- [ ] knowledge update required
- [ ] invariant update required
- [ ] conformance follow-up required
- [ ] divergence/parity issue required

Details:

## Required follow-ups

- 

Findings and severities stay in this report; never copy them into code comments
or PRs as labelled or enumerated lists.
