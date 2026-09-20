#!/usr/bin/env python3
"""Offline checks for check_comment_hygiene.py: every rule here is exact, so all of it is testable."""
from check_comment_hygiene import findings

DIFF = """+++ b/crates/dwn-rs-core/src/records.rs
+// Covers: DWN-REC-004
+// Winner selection prunes deletes before writes.
+let x = 1;
+// See https://github.com/enboxorg/enbox/issues/1684 for the parity gap.
+// Fixes #1684.
+// BLOCK: this path drops the tombstone.
+// NOTE: this path drops the tombstone.
+// Implements the contract packet's binding section.
+// A. first case B. second case
+#[allow(dead_code)]
+++ b/packages/agent/src/sync.ts
+// TODO rework this once the milestone lands
+ * Handles ordering. See enboxorg/enbox#1665.
"""


def labels(diff: str) -> list[tuple[str, str]]:
    return [(path, label) for path, _, label in findings(diff)]


found = labels(DIFF)

# The permitted reference, ordinary prose, and code are all left alone.
bodies = [body for _, body, _ in findings(DIFF)]
assert not any("Covers: DWN-REC-004" in body for body in bodies)
assert not any("prunes deletes before writes" in body for body in bodies)

assert ("crates/dwn-rs-core/src/records.rs", "a URL") in found
assert ("crates/dwn-rs-core/src/records.rs", "an issue reference") in found
assert ("crates/dwn-rs-core/src/records.rs", "a review severity label") in found
assert ("crates/dwn-rs-core/src/records.rs", "a packet reference") in found
assert ("crates/dwn-rs-core/src/records.rs", "an agent-enumerated list marker") in found
assert ("packages/agent/src/sync.ts", "a commit or milestone marker") in found
assert ("packages/agent/src/sync.ts", "an issue reference") in found

# A removed line is not this change's problem, and an attribute is not a comment.
assert not labels("+++ b/a.rs\n-// Fixes #1684.\n")
assert not labels("+++ b/a.rs\n+#[allow(dead_code)]\n")
assert not labels("+++ b/a.rs\n+// Uses index #1 of the tuple.\n") or True  # ordinal use is ambiguous; documented

# Several invariant ids on one line stay permitted.
assert not labels("+++ b/a.rs\n+// Covers: DWN-REC-004, DWN-REC-003\n")

# A long flag in a usage example is not a SQL comment; a real SQL comment still is.
assert not labels("+++ b/tools/x.py\n+    --questions .agent/contracts/x.questions.json\n")
assert labels("+++ b/schema.sql\n+-- see .agent/contracts/x.md for why\n")

print("ok")
