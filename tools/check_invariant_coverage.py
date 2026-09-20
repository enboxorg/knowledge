#!/usr/bin/env python3
"""Ask which invariants the test suites actually exercise.

A `Covers:` tag is a claim, and a probability is a judgement. Neither is proof: only a
test that fails when the rule is broken proves anything. This reports the three apart —
what is tagged, what a judgement says is covered anyway, and what nothing reaches — and
never merges them.

Candidates are found in code by name overlap, judged by name, then the best of them are
judged again with their bodies in view. The question is always the same one: would this
test fail if the rule were violated?

    tools/check_invariant_coverage.py --repo ../enbox-rust-core --repo ../enbox
    tools/check_invariant_coverage.py --repo ../enbox-rust-core --only DWN-REC-004 --json
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import sys

from check_invariant_semantics import ask_many, load_invariants

TAG = re.compile(r"\b(?:DWN|ENBOX|DID)(?:-[A-Z]+)+-\d{3}\b")
RUST_TEST = re.compile(r"#\[(?:tokio::)?test\b[^\]]*\]")
RUST_FN = re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+(\w+)")
TS_TEST = re.compile(r"""^\s*(?:it|test)\(\s*['"`](?P<name>[^'"`]+)""")
STOPWORDS = frozenset("""
the a an and or of to in on for with that this it its is are be been must may not no any same
when where which while if then than as at by from into over under after before must_not does do
""".split())
BODY_LINES = 60

NAME_QUESTION = (
    "`invariant` is a rule a DWN implementation must satisfy. `candidate` is a test in the "
    "codebase, named behaviourally. Judging by its name and path alone, is this test likely to "
    "exercise the rule — so that the test would fail if the rule were violated?"
)
BODY_QUESTION = (
    "`invariant` is a rule a DWN implementation must satisfy. `candidate` is a test, with its "
    "source. Would this test fail if the rule were violated? Answer no when the test exercises "
    "neighbouring behaviour without constraining the rule, or asserts only that a call succeeds."
)


def words(text: str) -> set[str]:
    return {w for w in re.split(r"[^a-z0-9]+", text.lower()) if len(w) > 3 and w not in STOPWORDS}


def rust_tests(path: Path, text: str) -> list[dict]:
    out, lines = [], text.splitlines()
    for index, line in enumerate(lines):
        if not RUST_TEST.search(line):
            continue
        for offset in range(index + 1, min(index + 5, len(lines))):
            match = RUST_FN.match(lines[offset])
            if match:
                # From two lines above the attribute: a `Covers:` tag often sits there.
                out.append({
                    "name": match.group(1),
                    "path": str(path),
                    "body": "\n".join(lines[max(index - 2, 0):offset + BODY_LINES]),
                })
                break
    return out


def ts_tests(path: Path, text: str) -> list[dict]:
    lines = text.splitlines()
    return [
        {"name": match.group("name"), "path": str(path), "body": "\n".join(lines[index:index + BODY_LINES])}
        for index, line in enumerate(lines)
        if (match := TS_TEST.match(line))
    ]


def inventory(repo: str) -> list[dict]:
    listed = subprocess.run(["git", "-C", repo, "ls-files"], capture_output=True, text=True, check=True).stdout.split()
    out = []
    for name in listed:
        path = Path(repo) / name
        if name.endswith(".rs"):
            reader, relevant = rust_tests, True
        elif re.search(r"\.(spec|test)\.tsx?$", name):
            reader, relevant = ts_tests, True
        else:
            relevant = False
        if relevant:
            try:
                out += reader(Path(name), path.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                continue
    return out


def tags(repo: str) -> dict[str, list[str]]:
    """Where each invariant id is named in the repository, by whoever tagged it."""
    # git grep uses POSIX ERE, where `\b` matches nothing; the ids come back out with TAG.
    found = subprocess.run(
        ["git", "-C", repo, "grep", "-nE", r"(DWN|ENBOX|DID)(-[A-Z]+)+-[0-9]{3}", "--", "*.rs", "*.ts", "*.tsx"],
        capture_output=True, text=True,
    ).stdout
    out: dict[str, list[str]] = {}
    for line in found.splitlines():
        for invariant_id in TAG.findall(line):
            out.setdefault(invariant_id, []).append(line.split(":")[0])
    return {k: sorted(set(v)) for k, v in out.items()}


def shortlist(statement: str, tests: list[dict], size: int) -> list[dict]:
    """Name overlap decides what is worth asking about; the model decides what it means."""
    keywords = words(statement)
    scored = [(len(keywords & words(t["name"] + " " + t["path"])), t) for t in tests]
    scored.sort(key=lambda pair: -pair[0])
    return [test for score, test in scored[:size] if score]


def key_of(index: int) -> str:
    return f"c{index}"


def judge(key: str, statement: str, candidates: list[dict], question: str, with_body: bool) -> dict[str, float]:
    if not candidates:
        return {}
    state = {
        "invariant": statement,
        "candidates": {
            key_of(i): {"name": c["name"], "path": c["path"]} | ({"source": c["body"]} if with_body else {})
            for i, c in enumerate(candidates)
        },
    }
    questions = {
        key_of(i): {"type": "noul", "instructions": f"{question}\n\ncandidate: `candidates.{key_of(i)}`"}
        for i in range(len(candidates))
    }
    return {name: answer["noul"] for name, answer in ask_many(key, state, questions).items()}


def tagged_tests(invariant_id: str, tests: list[dict]) -> list[dict]:
    """Tests naming the invariant themselves; these are judged whatever the name overlap says."""
    return [t for t in tests if invariant_id in t["body"]]


def assess(key: str, invariant_id: str, invariant: dict, tests: list[dict], shortlist_size: int, deep: int) -> dict:
    statement = invariant["statement"]
    claimed = tagged_tests(invariant_id, tests)
    candidates = claimed + [t for t in shortlist(statement, tests, shortlist_size) if t not in claimed]
    by_name = judge(key, statement, candidates, NAME_QUESTION, with_body=False)
    ranked = [c for c, _ in sorted(((candidates[int(k[1:])], p) for k, p in by_name.items()), key=lambda pair: -pair[1])]
    # Whatever else is judged, the most promising test claiming the invariant is judged on its source.
    best = ranked[:deep]
    claimed_ranked = [c for c in ranked if c in claimed]
    if claimed_ranked and not any(c in claimed for c in best):
        best = [claimed_ranked[0]] + best[: deep - 1]
    by_body = judge(key, statement, best, BODY_QUESTION, with_body=True)
    return {
        "candidates": len(candidates),
        "tests": sorted(
            ({"name": best[int(k[1:])]["name"], "path": best[int(k[1:])]["path"], "probability": round(p, 3)}
             for k, p in by_body.items()),
            key=lambda t: -t["probability"],
        ),
    }


def status(tagged: list[str], tests: list[dict], threshold: float) -> str:
    """A tag on a test is a claim about that test, so the claim and the judgement stay apart."""
    covering = any(t["probability"] >= threshold for t in tests)
    if tagged and covering:
        return "tagged, judged covering"
    if tagged:
        return "tagged, not judged covering"
    if covering:
        return "untagged, judged covering"
    return "no covering test found"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", action="append", required=True, help="checkout to search; repeatable")
    parser.add_argument("--only", action="append", help="limit to these invariant ids")
    parser.add_argument("--shortlist", type=int, default=20, help="candidates judged by name per invariant")
    parser.add_argument("--deep", type=int, default=3, help="candidates judged with their source per invariant")
    parser.add_argument("--threshold", type=float, default=0.6, help="probability at or above which a test counts as covering")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    key = os.environ.get("TYPESAFE_API_KEY")
    if not key:
        print("TYPESAFE_API_KEY is not set; skipping invariant coverage.")
        return

    tests, tagged = [], {}
    for repo in args.repo:
        tests += inventory(repo)
        for invariant_id, paths in tags(repo).items():
            tagged.setdefault(invariant_id, []).extend(paths)

    invariants = load_invariants(None)
    ids = [i for i in sorted(invariants) if not args.only or i in args.only]

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {i: pool.submit(assess, key, i, invariants[i], tests, args.shortlist, args.deep) for i in ids}
        assessed = {i: future.result() for i, future in futures.items()}

    rows = [
        {
            "id": i,
            "contract": invariants[i]["contract"],
            "tagged_in": tagged.get(i, []),
            "tagged_tests": [t["name"] for t in tagged_tests(i, tests)],
            "status": status([t["name"] for t in tagged_tests(i, tests)], assessed[i]["tests"], args.threshold),
            **assessed[i],
        }
        for i in ids
    ]

    if args.json:
        json.dump({"tests_searched": len(tests), "invariants": rows}, sys.stdout, indent=2)
        print()
        return

    print(f"## Invariant coverage ({len(tests)} tests searched across {len(args.repo)} repo(s))\n")
    print("A tag is a claim and a probability is a judgement. Only a test that fails when the rule")
    print("is broken proves coverage; confirm a judged row by reading the test before trusting it.\n")
    for row in rows:
        best = row["tests"][0] if row["tests"] else None
        detail = f"{best['path']}::{best['name']} ({best['probability']:.2f})" if best else f"{row['candidates']} candidate(s) by name"
        if not row["tagged_tests"] and row["tagged_in"]:
            detail += f"; id named in {len(row['tagged_in'])} source file(s), no test"
        print(f"- `{row['id']}` ({row['contract']}): {row['status']} — {detail}")
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print("\n" + "; ".join(f"{count} {name}" for name, count in sorted(counts.items())))


if __name__ == "__main__":
    main()
