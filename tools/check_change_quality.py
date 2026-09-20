#!/usr/bin/env python3
"""Judge a change file by file: is it complete, in the language's idiom, and tested?

This does not replace the deterministic tools. Run the repository's own linters,
type checks, and test suite first — `cargo clippy`, `cargo test`, `tsc`, `eslint` —
because they decide these questions exactly where they can. This covers what they
cannot see: work that compiles and lints cleanly while remaining a stub, a behaviour
change no test exercises, or a mechanism that fights the language it is written in.

Every answer is a candidate for review, never a verdict. The reviewer confirms it
against the code, and `agents/review-change.md` owns the severities.

Pass what the change is for with --intent, repeatably: the approved Behavioural Contract
Packet, the issue, the plan. Without it, scope and coverage are judged against the change's
own commit messages, which the change wrote — so it cannot overreach its own description.

--questions adds change-specific questions, written from the packet's test matrix, the
issue, and the diff as it currently stands. Each is `{"instructions": ..., "criteria": {...},
"scope": "change" | "file", "label": ...}`; `file` asks it of every changed code file.
Write them as observable behaviour, never as mechanism, or they flag the idiomatic
substitutions the implementation workflow allows.

    tools/check_change_quality.py --repo ../enbox-rust-core --range main...HEAD \
        --intent .agent/contracts/records-delete-convergence.md --intent issue-1684.md \
        --questions .agent/contracts/records-delete-convergence.questions.json
    tools/check_change_quality.py --pr enboxorg/enbox#1684 --json
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import argparse
import json
import os
import re
import sys

from check_invariant_semantics import ask_many
from check_knowledge_drift import read_change, split_files

LANGUAGES = {
    ".rs": "Rust", ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript",
    ".py": "Python", ".go": "Go", ".java": "Java", ".rb": "Ruby", ".kt": "Kotlin",
    ".swift": "Swift", ".c": "C", ".h": "C", ".cpp": "C++", ".cs": "C#", ".sql": "SQL",
}

QUESTIONS = {
    "incomplete": (
        "Does `file.diff` leave the behaviour it introduces unfinished — a stub, a TODO, an "
        "unimplemented branch, a hardcoded or placeholder value standing in for real work — while "
        "presenting a surface that looks implemented?",
        "unfinished behaviour behind a finished-looking surface",
    ),
    "untested": (
        "Does `file.diff` add or alter behaviour that no test in `change.diff` exercises? Judge the "
        "whole change: the test may live in another file. Answer no when the file is itself a test, "
        "or when its behaviour is already covered.",
        "behaviour this change does not test",
    ),
    "unidiomatic": (
        "Does `file.diff` work against the idioms of `file.language` — reimplementing what its "
        "standard library provides, modelling state as strings or integers where the language offers "
        "a type, or using a mechanism ported from another language in preference to the local one?",
        "fights the idioms of the language",
    ),
    "error_handling": (
        "Does `file.diff` drop, swallow, or panic on a failure that the surrounding code would "
        "otherwise carry — discarding an error, unwrapping a fallible value, or converting a "
        "recoverable failure into a crash — outside test code?",
        "a failure path dropped or turned into a panic",
    ),
    "out_of_scope": (
        "Does `file.diff` change behaviour beyond what this change is for: an unrelated refactor, "
        "an adjacent semantic change, or a test expectation rewritten to match the implementation "
        "rather than the intent?",
        "changes beyond the stated intent",
    ),
}

# Asked instead of the above when the caller supplies the approved contract, ticket, or plan.
WITH_INTENT = {
    "out_of_scope": (
        "`intent` states what this change is for: an approved behavioural contract, a ticket, or a "
        "plan. Does `file.diff` change behaviour `intent` does not call for — an unrelated refactor, "
        "an adjacent semantic change, or a test expectation rewritten to match the implementation?",
        "changes beyond what the stated intent calls for",
    ),
    "untested": (
        "`intent` states the behaviour this change must deliver, and may list the cases that prove "
        "it. Does `file.diff` add or alter behaviour that no test in `change.diff` exercises? Judge "
        "the whole change: the test may live in another file. Answer no when the file is itself a "
        "test, or when its behaviour is already covered.",
        "behaviour this change does not test",
    ),
}

# One judgement about the change as a whole, not about any single file.
UNIMPLEMENTED = (
    "`intent` states the behaviour this change must deliver. Does `change.diff` leave any of it "
    "unimplemented — a required case, condition, or error outcome that no part of the change "
    "realizes?",
    "the intent requires behaviour this change does not implement",
)


def file_path(file_diff: str) -> str:
    match = re.search(r"^diff --git a/(\S+) b/(\S+)", file_diff)
    return match.group(2) if match else "(unknown)"


def language_of(path: str) -> str | None:
    return LANGUAGES.get(path[path.rfind("."):]) if "." in path else None


def code_files(diff: str) -> list[tuple[str, str, str]]:
    """(path, language, file diff) for each changed file written in a known language."""
    out = []
    for file_diff in split_files(diff):
        path = file_path(file_diff)
        language = language_of(path)
        if language:
            out.append((path, language, file_diff))
    return out


def load_intent(paths: list[str] | None, limit: int) -> str | None:
    """The packet, the issue, the plan: everything stating what the change is for, in one block."""
    if not paths:
        return None
    parts = []
    for path in paths:
        text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
        parts.append(f"## {'stdin' if path == '-' else path}\n\n{text.strip()}")
    return "\n\n".join(parts)[:limit]


def load_questions(path: str) -> dict[str, dict]:
    """Change-specific questions, written from the packet and the diff by whoever runs this."""
    loaded = json.load(open(path, encoding="utf-8"))
    if not isinstance(loaded, dict) or not loaded:
        raise SystemExit(f"{path}: expected a non-empty object of questions keyed by name")
    for name, question in loaded.items():
        if not isinstance(question, dict) or not str(question.get("instructions", "")).strip():
            raise SystemExit(f"{path}: {name} needs non-empty instructions")
        if question.get("scope", "change") not in ("change", "file"):
            raise SystemExit(f"{path}: {name} scope must be 'change' or 'file'")
        if name in QUESTIONS:
            raise SystemExit(f"{path}: {name} collides with a built-in question")
    return loaded


def as_question(question: dict) -> dict:
    return {"type": "noul", "instructions": question["instructions"]} | (
        {"criteria": question["criteria"]} if question.get("criteria") else {}
    )


def questions_for(intent: str | None) -> dict[str, tuple[str, str]]:
    """The intent-aware wording where an intent was supplied, the standalone wording otherwise."""
    return QUESTIONS | WITH_INTENT if intent else QUESTIONS


def findings(path: str, answers: dict[str, float], threshold: float, questions: dict | None = None) -> list[str]:
    questions = questions or QUESTIONS
    return [
        f"- `{path}`: {label} ({answers[name]:.2f})"
        for name, (_, label) in questions.items()
        if answers.get(name, 0.0) >= threshold
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--pr", help="pull request as owner/repo#number")
    source.add_argument("--diff", help="unified diff file, or - for stdin")
    source.add_argument("--repo", help="path to a local checkout to diff")
    parser.add_argument("--range", default="main...HEAD", help="revision range for --repo")
    parser.add_argument("--title", help="change description when reading a diff")
    parser.add_argument("--intent", action="append", help="what the change is for: the approved Contract Packet, the issue, the plan; repeatable, - for stdin")
    parser.add_argument("--questions", help="JSON file of change-specific questions derived from the packet and diff")
    parser.add_argument("--threshold", type=float, default=0.6, help="probability at or above which an answer is reported")
    parser.add_argument("--max-files", type=int, default=30, help="how many changed code files to judge")
    parser.add_argument("--max-chars", type=int, default=200_000, help="diff budget")
    parser.add_argument("--json", action="store_true", help="emit the answers as JSON")
    args = parser.parse_args()
    args.text = None  # read_change reads the same inputs, minus the task-text form

    key = os.environ.get("TYPESAFE_API_KEY")
    if not key:
        print("TYPESAFE_API_KEY is not set; skipping change quality check.")
        return

    intent = load_intent(args.intent, args.max_chars)
    generated = load_questions(args.questions) if args.questions else {}
    change = read_change(args)
    files = code_files(change["diff"])[: args.max_files]
    if not files:
        print("No changed files in a recognised language.")
        return

    asked = questions_for(intent)
    questions = {name: {"type": "noul", "instructions": text} for name, (text, _) in asked.items()}
    questions |= {name: as_question(q) for name, q in generated.items() if q.get("scope", "change") == "file"}
    whole_questions = {name: as_question(q) for name, q in generated.items() if q.get("scope", "change") == "change"}
    if intent:
        whole_questions["unimplemented"] = {"type": "noul", "instructions": UNIMPLEMENTED[0]}

    base = {"change": change} | ({"intent": intent} if intent else {})
    with ThreadPoolExecutor(max_workers=4) as pool:
        # One request per file: the questions are about this file, against the whole change.
        futures = {
            path: pool.submit(
                ask_many, key, base | {"file": {"path": path, "language": language, "diff": file_diff}}, questions,
            )
            for path, language, file_diff in files
        }
        # Realized intent and change-scoped questions are about the change, not about a file.
        whole = pool.submit(ask_many, key, base, whole_questions) if whole_questions else None
        answered = {path: {name: a["noul"] for name, a in future.result().items()} for path, future in futures.items()}
        change_answers = {name: a["noul"] for name, a in whole.result().items()} if whole else {}
        unimplemented = change_answers.pop("unimplemented", None)

    if args.json:
        json.dump(
            {
                "title": change["title"],
                "intent": bool(intent),
                "unimplemented": None if unimplemented is None else round(unimplemented, 3),
                "change_answers": {k: round(v, 3) for k, v in change_answers.items()},
                "files": [
                    {"path": path, "language": language_of(path), "answers": {k: round(v, 3) for k, v in answers.items()}}
                    for path, answers in answered.items()
                ],
            },
            sys.stdout, indent=2,
        )
        print()
        return

    report = [f"## Change quality: {change['title']}", ""]
    labels = {name: q.get("label", name) for name, q in generated.items()}
    flagged = [line for path, answers in answered.items() for line in findings(path, answers, args.threshold, asked)]
    flagged += [
        f"- `{path}`: {labels[name]} ({probability:.2f})"
        for path, answers in answered.items()
        for name, probability in answers.items()
        if name in labels and probability >= args.threshold
    ]
    flagged += [
        f"- the change as a whole: {labels[name]} ({probability:.2f})"
        for name, probability in change_answers.items()
        if probability >= args.threshold
    ]
    if unimplemented is not None and unimplemented >= args.threshold:
        flagged.insert(0, f"- the change as a whole: {UNIMPLEMENTED[1]} ({unimplemented:.2f})")
    if flagged:
        report.append("Candidates to confirm against the code. Run the repository's linters and tests first; these are the questions those tools cannot answer.")
        report.append("")
        report += flagged
    else:
        report.append(f"Nothing above {args.threshold:.2f} across {len(files)} file(s).")
    if not intent:
        report += ["", "No intent supplied: scope and coverage were judged against the change's own description, which the change also wrote. Pass `--intent <packet|ticket|plan>` to judge them against what the change is for."]
    text = "\n".join(report) + "\n"
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as summary:
            summary.write(text)


if __name__ == "__main__":
    main()
