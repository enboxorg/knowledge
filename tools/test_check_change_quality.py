#!/usr/bin/env python3
"""Offline checks for the diff-splitting and reporting in check_change_quality.py (no API calls)."""
from check_change_quality import (
    QUESTIONS, WITH_INTENT, as_question, code_files, file_path, findings, language_of,
    load_intent, load_questions, questions_for,
)

DIFF = """diff --git a/crates/dwn-rs-core/src/records.rs b/crates/dwn-rs-core/src/records.rs
index 1..2 100644
--- a/crates/dwn-rs-core/src/records.rs
+++ b/crates/dwn-rs-core/src/records.rs
@@ -1 +1,2 @@
+let winner = candidates.first().unwrap();
diff --git a/README.md b/README.md
@@ -1 +1 @@
-old
+new
diff --git a/packages/agent/src/sync.ts b/packages/agent/src/sync.ts
@@ -1 +1 @@
+export const sync = () => {};
"""

assert file_path("diff --git a/x/y.rs b/x/y.rs\n") == "x/y.rs"
assert file_path("no header here") == "(unknown)"

assert language_of("a/b/c.rs") == "Rust"
assert language_of("a/b/c.tsx") == "TypeScript"
assert language_of("Cargo.lock") is None
assert language_of("Makefile") is None

files = code_files(DIFF)
assert [path for path, _, _ in files] == ["crates/dwn-rs-core/src/records.rs", "packages/agent/src/sync.ts"]
assert [language for _, language, _ in files] == ["Rust", "TypeScript"]
assert "unwrap" in files[0][2] and "sync.ts" in files[1][2]

answers = {"incomplete": 0.9, "untested": 0.61, "unidiomatic": 0.2, "error_handling": 0.75, "out_of_scope": 0.1}
assert findings("a.rs", answers, 0.6) == [
    "- `a.rs`: unfinished behaviour behind a finished-looking surface (0.90)",
    "- `a.rs`: behaviour this change does not test (0.61)",
    "- `a.rs`: a failure path dropped or turned into a panic (0.75)",
]
assert findings("a.rs", answers, 0.95) == []
assert set(answers) == set(QUESTIONS)

# An intent replaces the wording of the questions it changes, and asks no new per-file question.
assert set(questions_for(None)) == set(QUESTIONS)
assert set(questions_for("packet text")) == set(QUESTIONS)
assert set(WITH_INTENT) <= set(QUESTIONS)
assert questions_for("packet text")["out_of_scope"] != QUESTIONS["out_of_scope"]
assert questions_for("packet text")["incomplete"] == QUESTIONS["incomplete"]
assert "`intent`" in questions_for("packet text")["out_of_scope"][0]
assert findings("a.rs", {"out_of_scope": 0.9}, 0.6, questions_for("packet text")) == [
    "- `a.rs`: changes beyond what the stated intent calls for (0.90)"
]

import json
import pathlib
import tempfile

tmp = pathlib.Path(tempfile.mkdtemp())

# Intent gathers every file it is given, each labelled by where it came from.
packet, issue = tmp / "packet.md", tmp / "issue.md"
packet.write_text("Required: prune delete outranks write.")
issue.write_text("Reported: a write resurrected a pruned record.")
intent = load_intent([str(packet), str(issue)], 10_000)
assert "Required: prune delete" in intent and "Reported: a write" in intent
assert str(packet) in intent and str(issue) in intent
assert load_intent(None, 10_000) is None
assert len(load_intent([str(packet)], 12)) == 12

good = tmp / "q.json"
good.write_text(json.dumps({
    "prune_wins": {"instructions": "Does a prune delete still win over a later write?", "scope": "change", "label": "prune ordering lost"},
    "local_check": {"instructions": "Does this file compare timestamps before CIDs?", "scope": "file"},
}))
loaded = load_questions(str(good))
assert loaded["prune_wins"]["scope"] == "change" and loaded["local_check"]["scope"] == "file"
assert as_question(loaded["prune_wins"]) == {"type": "noul", "instructions": loaded["prune_wins"]["instructions"]}
assert as_question({"instructions": "x", "criteria": {"true": "t", "false": "f"}})["criteria"] == {"true": "t", "false": "f"}


def rejects(payload: object) -> bool:
    bad = tmp / "bad.json"
    bad.write_text(json.dumps(payload))
    try:
        load_questions(str(bad))
    except SystemExit:
        return True
    return False


assert rejects({})
assert rejects([{"instructions": "x"}])
assert rejects({"q": {"instructions": "  "}})
assert rejects({"q": {"instructions": "x", "scope": "module"}})
assert rejects({"incomplete": {"instructions": "collides with a built-in"}})

print("ok")
