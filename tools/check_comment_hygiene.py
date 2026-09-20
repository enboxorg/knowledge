#!/usr/bin/env python3
"""Find process references added to code comments.

`AGENTS.md` permits exactly one process reference in a comment: an invariant ID under the
repository's convention, such as `// Covers: DWN-REC-004`. Issue numbers, URLs, packet
references, review severities, commit markers, and agent-enumerated lists belong to the
artefact that produced them, and go stale in code.

This reads added comment lines from a diff. No model and no API key: every rule here is
exact, so it can fail a build without calibration.

    git diff main... | tools/check_comment_hygiene.py -
    tools/check_comment_hygiene.py --repo ../enbox-rust-core --range main...HEAD
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

# `--` needs the space: `--intent` in a usage example is a flag, not a SQL comment.
COMMENT = re.compile(r"^\+\s*(//+|\#+|/\*+|\*|--(?=\s)|<!--)\s?(?P<body>.*)")
INVARIANT = re.compile(r"\b(?:DWN|ENBOX|DID)(?:-[A-Z]+)+-\d{3}\b")

RULES = (
    (re.compile(r"(?:https?://\S+|\bgithub\.com/\S+)"), "a URL"),
    (re.compile(r"(?<![\w.])#\d+\b|\b[\w.-]+/[\w.-]+#\d+\b"), "an issue reference"),
    (re.compile(r"\b(?:BLOCK|GAP|RISK)\b|^\s*NOTE:"), "a review severity label"),
    (re.compile(r"\.agent/contracts|\bcontract packet\b", re.I), "a packet reference"),
    (re.compile(r"\bcommit\s+[0-9a-f]{7,40}\b|\bmilestone\b", re.I), "a commit or milestone marker"),
    (re.compile(r"^\(?[A-Za-z]\)[.)]?\s+\S|^[A-Za-z][.)]\s+\S"), "an agent-enumerated list marker"),
)


def read_diff(args: argparse.Namespace) -> str:
    if args.repo:
        return subprocess.run(
            ["git", "-C", args.repo, "diff", args.range], capture_output=True, text=True, check=True
        ).stdout
    return sys.stdin.read() if args.diff == "-" else open(args.diff, encoding="utf-8").read()


def findings(diff: str) -> list[tuple[str, str, str]]:
    """(file, comment, what was found) for each added comment line breaking a rule."""
    out, path = [], "(unknown)"
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
            continue
        match = COMMENT.match(line)
        if not match:
            continue
        body = match.group("body").strip()
        # An invariant ID is the one permitted process reference, and carries no other text.
        if INVARIANT.search(body) and re.fullmatch(r"(?:Covers:\s*)?(?:[\w-]+,?\s*)+", body):
            continue
        for pattern, label in RULES:
            if pattern.search(body):
                out.append((path, body, label))
                break
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--diff", help="unified diff file, or - for stdin")
    source.add_argument("--repo", help="path to a local checkout to diff")
    parser.add_argument("--range", default="main...HEAD", help="revision range for --repo")
    parser.add_argument("--strict", action="store_true", help="exit non-zero when anything is found")
    args = parser.parse_args()

    found = findings(read_diff(args))
    for path, body, label in found:
        print(f"{path}: {label} in an added comment: {body}")
    if found:
        print(f"\n{len(found)} comment(s) carry a process reference. Reword them in the code's own terms; "
              f"the issue, packet, or finding stays in the artefact that produced it.")
    else:
        print("No process references in added comments.")
    if found and args.strict:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
