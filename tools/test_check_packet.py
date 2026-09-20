#!/usr/bin/env python3
"""Offline checks for the parsing and structural rules in check_packet.py (no API calls)."""
from check_packet import cited_ids, sections, statements, structure_findings

PACKET = """# Behavioural Contract Packet

## Controlling invariants

- DWN-REC-004 (implementation-contract)
- DWN-REC-999 (does not exist)

## Required behaviour (binding)

- A prune delete wins over a plain delete, and both win over a write. Ties break on canonical message timestamp.
- Split the reference on the last `#` to find the fragment.
- ok

## Assumptions to challenge

| Assumption | Source | If false |
| --- | --- | --- |
| Deletes are terminal | issue 1684 | resurrection becomes possible |

## Test matrix

| Case | Setup | Expected | Invariant(s) |
| --- | --- | --- | --- |
"""

parsed = sections(PACKET)
assert set(parsed) == {"Controlling invariants", "Required behaviour (binding)", "Assumptions to challenge", "Test matrix"}
assert "prune delete wins" in parsed["Required behaviour (binding)"]

lines = statements(parsed["Required behaviour (binding)"])
assert lines[0].startswith("A prune delete wins over a plain delete")
assert lines[1] == "Ties break on canonical message timestamp."
assert any("last `#`" in line for line in lines)
assert "ok" not in lines  # too short to be a requirement
assert not [line for line in lines if line.startswith(("|", "-"))]

assert cited_ids(PACKET) == ["DWN-REC-004", "DWN-REC-999"]

found = structure_findings(PACKET, parsed, {"DWN-REC-004": {}})
assert "cites unknown invariant ids: DWN-REC-999" in found
assert any("Test matrix" in f and "no rows" in f for f in found)          # header only
assert not any("Assumptions to challenge" in f for f in found)            # has a row
assert any("`Required behaviour (binding)`" not in f for f in found)

missing = structure_findings("", {}, {})
assert len([f for f in missing if "is missing or empty" in f]) == 4

print("ok")
