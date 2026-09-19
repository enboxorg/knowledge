#!/usr/bin/env python3
"""Offline checks for the policy half of check_invariant_semantics.py (no API calls)."""
from check_invariant_semantics import meaning_finding, source_findings

item = {"contract": "enbox-parity", "sources": ["dwn/records.md", "enbox/records.md"]}

assert meaning_finding("old", item, 0.3) is None
assert "refines" in meaning_finding("old", item, 1.2)
assert meaning_finding("old", {**item, "revisions": [{"previous": "old"}]}, 1.2) is None
assert meaning_finding("other", {**item, "revisions": [{"previous": "old"}]}, 1.2) is not None
assert "new ID" in meaning_finding("old", {**item, "revisions": [{"previous": "old"}]}, 1.8)

# A draft page contradicting an enbox-parity invariant is expected.
assert source_findings(item, {"dwn/records.md": ("contradicts", 0.95), "enbox/records.md": ("supports", 0.9)}, {}) == []
# The same contradiction on a normative invariant is reported.
normative = {**item, "contract": "normative"}
assert source_findings(normative, {"dwn/records.md": ("contradicts", 0.95), "enbox/records.md": ("supports", 0.9)}, {}) == [
    "`dwn/records.md`: contradicts the statement"
]
# Uncertain support counts as neither support nor contradiction.
assert source_findings(item, {"enbox/records.md": ("supports", 0.6)}, {}) == [
    "`enbox/records.md`: uncertain `supports` (0.60)"
]
# A context citation is only reported when no source states the rule.
supported_pair = {"dwn/records.md": ("says_nothing", 0.9), "enbox/records.md": ("supports", 0.95)}
assert source_findings(item, supported_pair, {}) == []
assert source_findings(item, {**supported_pair, "enbox/records.md": ("supports", 0.5)}, {}) == [
    "`dwn/records.md`: does not address the statement",
    "`enbox/records.md`: uncertain `supports` (0.50)",
]
# A confident contradiction is reported even when another source supports the statement.
assert source_findings(normative, {"dwn/records.md": ("contradicts", 0.95), "enbox/records.md": ("supports", 0.95)}, {}) == [
    "`dwn/records.md`: contradicts the statement"
]
# A source note acknowledges a source's verdict, but never stands in for support.
noted = {**item, "source_notes": {"enbox/records.md": "background only"}}
assert source_findings(noted, {"enbox/records.md": ("says_nothing", 0.9)}, {}) == [
    "no source confidently supports the statement"
]

# A page that names the ID instead of restating the rule defers to the registry.
cites = {"enbox/did-dht.md": True}
parity = {"contract": "enbox-parity", "sources": ["enbox/did-dht.md"]}
assert source_findings(parity, {"enbox/did-dht.md": ("supports", 0.5)}, cites) == []
assert source_findings({**parity, "contract": "normative"}, {"enbox/did-dht.md": ("supports", 0.5)}, cites) == [
    "`enbox/did-dht.md`: uncertain `supports` (0.50)"
]
# Deferring never excuses a contradiction.
assert source_findings(parity, {"enbox/did-dht.md": ("contradicts", 0.9)}, cites) == [
    "`enbox/did-dht.md`: contradicts the statement"
]

print("ok")
