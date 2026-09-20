#!/usr/bin/env python3
"""Offline checks for the diff-handling and grouping in check_knowledge_drift.py (no API calls)."""
from check_knowledge_drift import checklist, key_of, log_range, page_paths, page_summary, read_repo, trim

assert key_of("DWN-REC-004") == "dwn_rec_004"
assert key_of("dwn/queries-and-sync.md") == "dwn_queries_and_sync_md"

paths = page_paths()
assert "dwn/records.md" in paths and "builders/encryption-patterns.md" in paths
assert not [p for p in paths if p.startswith(("agents/", ".github/", "maintenance/")) or p.endswith("README.md")]
assert len(set(paths)) == len(paths)

summary = page_summary("dwn/records.md")
assert "---" not in summary and 0 < len(summary) <= 400
assert "·" in summary  # headings joined ahead of the opening line

assert log_range("main...HEAD") == "main..HEAD"
assert log_range("main..HEAD") == "main..HEAD"
assert log_range("HEAD") == "HEAD"

# A working-tree range carries no commit messages and still produces a usable change.
here = read_repo(".", "HEAD", None)
assert here["title"] == ". HEAD" and here["body"] == ""

small = "diff --git a/x b/x\n+one\n"
assert trim(small, 100) == small

big = "diff --git a/x b/x\n" + "+x\n" * 50 + "\ndiff --git a/y b/y\n+y\n"
trimmed = trim(big, 120)
assert "a/x" in trimmed and "a/y" not in trimmed, trimmed
assert "1 further file(s) omitted" in trimmed

invariants = {
    "DWN-REC-004": {"sources": ["dwn/distributed-semantics.md", "implementation/records-state-machine.md"]},
    "DWN-REC-003": {"sources": ["dwn/distributed-semantics.md"]},
}
assert checklist([("DWN-REC-004", 0.91), ("DWN-REC-003", 0.62)], invariants) == [
    "- [ ] `dwn/distributed-semantics.md` — DWN-REC-004 (0.91), DWN-REC-003 (0.62)",
    "- [ ] `implementation/records-state-machine.md` — DWN-REC-004 (0.91)",
]

print("ok")
