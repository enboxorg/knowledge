#!/usr/bin/env python3
"""Rank the knowledge base against a change or a task.

Every invariant is judged against the change, batched over one copy of it. The sources of
the affected invariants are the pages to review; --pages additionally ranks the pages no
invariant cites. For the PR rule in `maintenance/freshness.md`, each listed page needs a
same-change update, a linked follow-up, or an explicit statement that it is unaffected.
For contract discovery and review, the ranking is a reading list, not a verdict.

    tools/check_knowledge_drift.py --pr enboxorg/enbox#1684
    tools/check_knowledge_drift.py --repo ../enbox-rust-core --range main...HEAD
    tools/check_knowledge_drift.py --text issue.md --pages --top 15 --json
    git diff main... | tools/check_knowledge_drift.py --diff -
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import argparse
import json
import os
import subprocess
import sys

import re

from check_invariant_semantics import ROOT, ask_many, load_invariants

BATCH = 20
MAX_CHARS = 60_000

TRIGGERS = {
    "architecture_replaced": (
        "The change removes or replaces a named architectural component, rather than modifying behaviour within the existing architecture.",
        "check the pages naming that architecture.",
    ),
    "parity_baseline": (
        "The change moves current TypeScript Enbox behaviour that a Rust implementation targets for parity.",
        "follow the rebaseline procedure in `maintenance/freshness.md`.",
    ),
    "unregistered_behaviour": (
        "The change establishes a behavioural rule that no invariant in `invariants` states, so the registry would need a new entry to cover it.",
        "propose an invariant, or record the gap as a follow-up.",
    ),
}


PREAMBLE = "`change` is work on a DWN implementation: a pull request, a diff, or a task description."


def invariant_question(statement: str) -> dict:
    return {
        "type": "noul",
        "instructions": (
            f"{PREAMBLE} Could this work alter whether the following rule holds, or does it "
            f"implement, test, or depend on the behaviour the rule describes?\n\nRule: {statement}"
        ),
        "criteria": {
            "true": "The work touches the behaviour the rule describes, so the rule needs rechecking.",
            "false": "The work is unrelated to the behaviour the rule describes.",
        },
    }


def page_question(path: str) -> dict:
    return {
        "type": "noul",
        "instructions": (
            f"{PREAMBLE} `pages` holds knowledge pages, each summarised by its headings and opening. "
            f"Would someone doing this work need to read the page at `pages['{path}']`?"
        ),
        "criteria": {
            "true": "The page covers the semantics, architecture, or expectations this work depends on or changes.",
            "false": "The page covers an unrelated part of the system.",
        },
    }


def trigger_question(description: str) -> dict:
    return {"type": "noul", "instructions": f"{PREAMBLE} {description}"}


def key_of(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def page_paths() -> list[str]:
    """Substantive knowledge pages: the material a reader is sent to, not process or navigation."""
    listed = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "*.md"], capture_output=True, text=True, check=True
    ).stdout.split()
    skipped = ("agents/", ".github/", "maintenance/")
    return [p for p in listed if not p.endswith("README.md") and not p.startswith(skipped)]


def page_summary(path: str, limit: int = 400) -> str:
    """Front-matter kind, headings, and opening prose: enough to judge whether the page is worth reading."""
    text = (ROOT / path).read_text(encoding="utf-8")
    body = text.split("---", 2)[2] if text.startswith("---") else text
    headings = [line.lstrip("# ").strip() for line in body.splitlines() if line.startswith("#")]
    opening = next((line.strip() for line in body.splitlines() if line.strip() and not line.startswith("#")), "")
    return f"{' · '.join(headings)}\n{opening}"[:limit]


def split_files(diff: str) -> list[str]:
    """One entry per file in a unified diff, each still headed by its `diff --git` line."""
    return ["diff --git " + chunk for chunk in diff.split("diff --git ")[1:]]


def trim(diff: str, max_chars: int) -> str:
    """Keep whole files from the diff until the budget runs out."""
    if len(diff) <= max_chars:
        return diff
    files = split_files(diff) or [diff]
    kept, used = [], 0
    for piece in files:
        if used + len(piece) > max_chars:
            break
        kept.append(piece)
        used += len(piece)
    if not kept:  # a first file larger than the budget
        kept = [files[0][:max_chars]]
    dropped = len(files) - len(kept)
    return "".join(kept) + f"\n\n[{dropped} further file(s) omitted from this diff]"


def log_range(range_: str) -> str:
    """`git diff` compares a merge base with `...`; `git log` wants `..` for the same commits."""
    return range_.replace("...", "..") if "..." in range_ else range_


def read_repo(path: str, range_: str, title: str | None) -> dict:
    def run(*args: str) -> str:
        return subprocess.run(["git", "-C", path, *args], capture_output=True, text=True, check=True).stdout

    diff = run("diff", range_)
    messages = run("log", "--format=%s%n%b", log_range(range_)) if ".." in range_ else ""
    subjects = [line for line in messages.splitlines() if line.strip()]
    return {
        "title": title or (subjects[0] if subjects else f"{path} {range_}"),
        "body": "\n".join(subjects[1:]),
        "diff": diff,
    }


def read_change(args: argparse.Namespace) -> dict:
    if args.text:
        text = sys.stdin.read() if args.text == "-" else open(args.text, encoding="utf-8").read()
        return {"title": args.title or "(task)", "body": text, "diff": ""}
    if args.repo:
        change = read_repo(args.repo, args.range, args.title)
        return {**change, "diff": trim(change["diff"], args.max_chars)}
    if args.diff:
        diff = sys.stdin.read() if args.diff == "-" else open(args.diff, encoding="utf-8").read()
        return {"title": args.title or "(local diff)", "body": "", "diff": trim(diff, args.max_chars)}
    repo, _, number = args.pr.partition("#")
    view = subprocess.run(
        ["gh", "pr", "view", number, "--repo", repo, "--json", "title,body"],
        capture_output=True, text=True, check=True,
    )
    diff = subprocess.run(["gh", "pr", "diff", number, "--repo", repo], capture_output=True, text=True, check=True)
    meta = json.loads(view.stdout)
    return {"title": meta["title"], "body": meta["body"], "diff": trim(diff.stdout, args.max_chars)}


def checklist(affected: list[tuple[str, float]], invariants: dict[str, dict]) -> list[str]:
    """Group affected invariants by the pages that document them."""
    pages: dict[str, list[str]] = {}
    for invariant_id, probability in affected:
        for source in invariants[invariant_id]["sources"]:
            pages.setdefault(source, []).append(f"{invariant_id} ({probability:.2f})")
    lines = []
    for page, ids in sorted(pages.items()):
        lines.append(f"- [ ] `{page}` — {', '.join(ids)}")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--pr", help="pull request as owner/repo#number")
    source.add_argument("--diff", help="unified diff file, or - for stdin")
    source.add_argument("--repo", help="path to a local checkout to diff")
    source.add_argument("--text", help="issue, task, or design question as a file, or - for stdin")
    parser.add_argument("--pages", action="store_true", help="also rank the knowledge pages no invariant cites")
    parser.add_argument("--range", default="main...HEAD", help="revision range for --repo, e.g. main...HEAD or HEAD")
    parser.add_argument("--title", help="change description when reading a diff")
    parser.add_argument("--threshold", type=float, default=0.5, help="probability at or above which an invariant is affected")
    parser.add_argument("--top", type=int, help="take the N highest-ranked invariants instead of applying --threshold")
    parser.add_argument("--json", action="store_true", help="emit the ranking as JSON for another program to consume")
    parser.add_argument("--max-chars", type=int, default=MAX_CHARS, help="diff budget sent to the model")
    args = parser.parse_args()

    key = os.environ.get("TYPESAFE_API_KEY")
    if not key:
        print("TYPESAFE_API_KEY is not set; skipping knowledge drift check.")
        return

    change = read_change(args)
    invariants = load_invariants(None)
    ids = sorted(invariants)
    batches = [ids[i:i + BATCH] for i in range(0, len(ids), BATCH)]

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [
            pool.submit(ask_batch, key, change, {key_of(i): invariant_question(invariants[i]["statement"]) for i in batch})
            for batch in batches
        ]
        # The registry rides along, so "no invariant states this" is answered against the real list.
        futures.append(pool.submit(
            ask_batch, key, change,
            {name: trigger_question(description) for name, (description, _) in TRIGGERS.items()},
            {"invariants": [{"id": i, "statement": invariants[i]["statement"]} for i in ids]},
        ))

        paths = page_paths() if args.pages else []
        page_batches = [paths[i:i + BATCH] for i in range(0, len(paths), BATCH)]
        page_futures = [
            # Each batch carries only its own summaries, so the state stays small.
            pool.submit(
                ask_batch, key, change,
                {key_of(p): page_question(p) for p in batch},
                {"pages": {p: page_summary(p) for p in batch}},
            )
            for batch in page_batches
        ]
        answers: dict[str, float] = {}
        for future in futures + page_futures:
            answers.update(future.result())

    page_ranking = sorted(((p, answers.get(key_of(p), 0.0)) for p in paths), key=lambda pair: -pair[1])
    if args.top:
        page_ranking = page_ranking[: args.top]
    else:
        page_ranking = [pair for pair in page_ranking if pair[1] >= args.threshold]

    ranked = sorted(((i, answers.get(key_of(i), 0.0)) for i in ids), key=lambda pair: -pair[1])
    affected = ranked[: args.top] if args.top else [pair for pair in ranked if pair[1] >= args.threshold]

    if args.json:
        json.dump(
            {
                "title": change["title"],
                "invariants": [
                    {"id": i, "probability": round(p, 3), **{k: invariants[i][k] for k in ("contract", "statement", "sources")}}
                    for i, p in affected
                ],
                "pages_from_invariants": sorted({source for i, _ in affected for source in invariants[i]["sources"]}),
                "pages_ranked": [{"path": path, "probability": round(p, 3)} for path, p in page_ranking],
                "triggers": {name: round(answers.get(name, 0.0), 3) for name in TRIGGERS},
            },
            sys.stdout,
            indent=2,
        )
        print()
        return

    report = [f"## Knowledge drift: {change['title']}", ""]
    if not affected:
        report.append("No invariant is affected at the current threshold. State in the PR why knowledge is unaffected.")
    else:
        report.append("Resolve each page with a same-change update, a linked follow-up, or an explicit statement that it is unaffected.")
        report.append("")
        report += checklist(affected, invariants)
        report.append("")
        report += [
            f"- `{i}` ({invariants[i]['contract']}, {probability:.2f}): {invariants[i]['statement'][:140]}"
            for i, probability in affected
        ]
    if page_ranking:
        cited = {source for i, _ in affected for source in invariants[i]["sources"]}
        report += ["", "Pages ranked directly (`*` where no affected invariant cites the page):"]
        report += [
            f"- [ ] `{path}` ({probability:.2f}){'' if path in cited else ' *'}"
            for path, probability in page_ranking
        ]
    for name, (description, advice) in TRIGGERS.items():
        if answers.get(name, 0.0) >= args.threshold:
            report.append(f"- {description} ({answers[name]:.2f}) — {advice}")

    text = "\n".join(report) + "\n"
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as summary:
            summary.write(text)


def ask_batch(key: str, change: dict, questions: dict, extra: dict | None = None) -> dict[str, float]:
    state = {"change": change} | (extra or {})
    answers = ask_many(key, state, questions)
    return {name: answer["noul"] for name, answer in answers.items()}


if __name__ == "__main__":
    main()
