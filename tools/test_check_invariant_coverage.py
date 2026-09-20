#!/usr/bin/env python3
"""Offline checks for the inventory, shortlisting, and status rules in check_invariant_coverage.py."""
from pathlib import Path

from check_invariant_coverage import rust_tests, shortlist, status, ts_tests, words

RUST = """
use super::*;

#[test]
fn helper_is_not_a_test() {
    assert!(true);
}

#[cfg(test)]
mod tests {
    #[tokio::test]
    async fn prune_dominates_newer_plain_delete_in_both_arrival_orders() {
        assert_eq!(winner(), prune);
    }

    #[test]
    #[should_panic]
    fn rejects_malformed_records() {}
}
"""

found = rust_tests(Path("state.rs"), RUST)
names = [t["name"] for t in found]
assert names == ["helper_is_not_a_test", "prune_dominates_newer_plain_delete_in_both_arrival_orders", "rejects_malformed_records"], names
assert all(t["path"] == "state.rs" for t in found)
assert "assert_eq!(winner(), prune);" in found[1]["body"]

TS = """
describe('records', () => {
  it('rejects a resurrected delete', async () => {
    expect(result).to.equal(undefined);
  });
  test(`counts the projected population`, () => {});
});
"""
assert [t["name"] for t in ts_tests(Path("a.spec.ts"), TS)] == [
    "rejects a resurrected delete", "counts the projected population"
]

assert "delete" in words("A delete is terminal") and "is" not in words("A delete is terminal")
assert not words("a of to in on")  # stopwords and short tokens only

tests = [
    {"name": "prune_dominates_newer_plain_delete", "path": "records/state.rs", "body": ""},
    {"name": "parses_a_gateway_uri", "path": "did/dht.rs", "body": ""},
    {"name": "unrelated", "path": "x.rs", "body": ""},
]
picked = shortlist("A prune delete dominates a plain delete for a Record", tests, 5)
assert [t["name"] for t in picked] == ["prune_dominates_newer_plain_delete"]
assert shortlist("nothing matches here whatsoever", tests, 5) == []
assert len(shortlist("delete record gateway parses", tests, 1)) == 1

covering = [{"probability": 0.9}]
weak = [{"probability": 0.2}]
assert status([], covering, 0.6) == "untagged, judged covering"
assert status(["a_test"], covering, 0.6) == "tagged, judged covering"
assert status(["a_test"], weak, 0.6) == "tagged, not judged covering"
assert status([], weak, 0.6) == "no covering test found"
assert status([], [], 0.6) == "no covering test found"

print("ok")
