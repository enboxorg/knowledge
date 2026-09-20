#!/usr/bin/env python3
"""Advisory semantic checks for invariants/*.json using TypeSafe System One.

ID stability: a statement changed since --base is compared with its base statement.
Source support: each (statement, source page) pair is judged for support.

By default only invariants changed since --base, and invariants citing pages changed
since --base, are checked. --all checks every invariant against every source.
Findings go to stdout and $GITHUB_STEP_SUMMARY; the exit status is always 0.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import json
import os
import subprocess
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
API_URL = "https://api.typesafe.ai/v1/systemone"
MODEL = os.environ.get("TYPESAFE_MODEL", "jev-latest")
CONFIDENT = 0.8

MEANING_QUESTION = {
    "type": "score",
    "instructions": (
        "`before` and `after` are two versions of one invariant: a compact assertion about how a "
        "system must behave. How does the assertion in `after` relate to the assertion in `before`?"
    ),
    "criteria": [
        "`after` asserts exactly what `before` asserts; only wording, clarity, or examples differ, "
        "and any system satisfying one satisfies the other.",
        "`after` keeps the subject and rule of `before` but adds or removes a condition, exception, "
        "scope limit, or ordering detail, so some systems satisfy one version and not the other.",
        "`after` asserts a different rule than `before`: a different subject, or an outcome that "
        "conflicts with what `before` requires.",
    ],
}

SUPPORT_QUESTION = {
    "type": "choice",
    "instructions": (
        "`claim` is a compact invariant; `source.text` is a knowledge page cited as its source. "
        "The page may explain the rule at length or in different terms. "
        "What does the page say about the claim?"
    ),
    "criteria": {
        "supports": "The page states the claim, or directly implies that it is true.",
        "contradicts": "The page states the opposite of the claim, or implies that it is false.",
        "says_nothing": "The page does not address the claim either way.",
    },
}


def support_state(statement: str, source: str, text: str) -> dict:
    return {"claim": statement, "source": {"path": source, "text": text}}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def load_invariants(ref: str | None) -> dict[str, dict]:
    if ref:
        files = [f for f in git("ls-tree", "--name-only", ref, "invariants/").split() if f.endswith(".json")]
        texts = [git("show", f"{ref}:{f}") for f in files]
    else:
        texts = [p.read_text(encoding="utf-8") for p in sorted((ROOT / "invariants").glob("*.json"))]
    return {item["id"]: item for text in texts for item in json.loads(text)}


def ask_many(key: str, state: dict, questions: dict) -> dict:
    """One request carrying any number of questions over the same state."""
    body = json.dumps({"state": state, "model": MODEL, "questions": questions}).encode()
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(API_URL, body, headers), timeout=180) as resp:
                return json.load(resp)["answers"]
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 529) or attempt == 4:
                raise
            time.sleep(2**attempt)
    raise AssertionError("unreachable")


def ask(key: str, state: dict, question: dict) -> dict:
    return ask_many(key, state, {"q": question})["q"]


def meaning_finding(before: str, item: dict, score: float) -> str | None:
    """Policy for a changed statement, given the meaning-change Score."""
    level = round(score)
    if level == 0:
        return None
    if level == 2:
        return f"asserts a different rule (score {score:.2f}); use a new ID"
    if any(rev.get("previous") == before for rev in item.get("revisions", [])):
        return None
    return f"refines its rule (score {score:.2f}); add a `revisions` entry whose `previous` is the old statement"


def source_findings(item: dict, verdicts: dict[str, tuple[str, float]], cites_id: dict[str, bool]) -> list[str]:
    """Policy for one invariant, given a (choice, confidence) verdict per source.

    `cites_id` says whether each source page names the invariant ID. A page that names the ID
    without stating the rule is deferring to the registry, which only a normative invariant
    may not do: its rule belongs in the draft-derived prose it cites.
    """
    notes = item.get("source_notes", {})
    findings: list[str] = []
    silent: list[str] = []
    supported = False
    for source, (choice, confidence) in verdicts.items():
        if choice == "supports" and confidence >= CONFIDENT:
            supported = True
        if source in notes:
            continue
        if choice == "contradicts" and item["contract"] == "enbox-parity" and source.startswith("dwn/"):
            continue
        if choice != "contradicts" and cites_id.get(source) and item["contract"] != "normative":
            supported = True
            continue
        if choice == "contradicts" and confidence >= CONFIDENT:
            findings.append(f"`{source}`: contradicts the statement")
        elif confidence < CONFIDENT:
            silent.append(f"`{source}`: uncertain `{choice}` ({confidence:.2f})")
        elif choice == "says_nothing":
            silent.append(f"`{source}`: does not address the statement")
    # A source that merely fails to state the rule is a context citation once another source
    # states it; only an unsupported invariant needs to hear about it.
    if not supported and not findings:
        findings.extend(silent or ["no source confidently supports the statement"])
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", default="origin/main", help="git ref to compare against")
    parser.add_argument("--all", action="store_true", help="check every invariant against every source")
    args = parser.parse_args()

    key = os.environ.get("TYPESAFE_API_KEY")
    if not key:
        print("TYPESAFE_API_KEY is not set; skipping invariant semantic checks.")
        return

    head = load_invariants(None)
    base = load_invariants(args.base)
    lines: list[str] = []

    removed = sorted(base.keys() - head.keys())
    if removed:
        lines.append(f"- Removed IDs: {', '.join(removed)}")
    for inv_id in sorted(head.keys() & base.keys()):
        if head[inv_id]["contract"] != base[inv_id]["contract"]:
            lines.append(f"- `{inv_id}`: contract `{base[inv_id]['contract']}` → `{head[inv_id]['contract']}`")

    changed = [i for i in sorted(head.keys() & base.keys()) if head[i]["statement"] != base[i]["statement"]]
    if args.all:
        targets = sorted(head)
    else:
        pages = set(git("diff", "--name-only", f"{args.base}...HEAD").split())
        targets = sorted(
            i for i, item in head.items()
            if i not in base or i in changed or item["sources"] != base[i]["sources"] or pages & set(item["sources"])
        )

    with ThreadPoolExecutor(max_workers=4) as pool:
        meaning = {
            i: pool.submit(ask, key, {"before": base[i]["statement"], "after": head[i]["statement"]}, MEANING_QUESTION)
            for i in changed
        }
        pages = {
            source: (ROOT / source).read_text(encoding="utf-8")
            for i in targets for source in head[i]["sources"] if (ROOT / source).is_file()
        }
        support = {
            (i, source): pool.submit(ask, key, support_state(head[i]["statement"], source, pages[source]), SUPPORT_QUESTION)
            for i in targets for source in head[i]["sources"] if source in pages
        }

        for i, future in meaning.items():
            finding = meaning_finding(base[i]["statement"], head[i], future.result()["score"])
            if finding:
                lines.append(f"- `{i}`: {finding}")
        for i in targets:
            verdicts = {
                source: (answer["choice"], answer["confidence"])
                for (inv_id, source), f in support.items() if inv_id == i
                for answer in [f.result()]
            }
            cites_id = {source: i in text for source, text in pages.items()}
            findings = source_findings(head[i], verdicts, cites_id)
            for index, finding in enumerate(findings):
                source = next((s for s in verdicts if f"`{s}`" in finding), None)
                if not source:
                    continue
                # A verdict that does not survive being asked again is ambiguous, not a finding.
                again = ask(key, support_state(head[i]["statement"], source, pages[source]), SUPPORT_QUESTION)["choice"]
                if again != verdicts[source][0]:
                    findings[index] = f"`{source}`: unstable verdict (`{verdicts[source][0]}`, then `{again}`)"
            lines.extend(f"- `{i}`: {finding}" for finding in findings)

    scope = "all invariants" if args.all else f"changes since `{args.base}`"
    report = [f"## Invariant semantic checks ({scope})", "", f"Checked {len(changed)} statement change(s) and {len(targets)} invariant(s) against their sources.", ""]
    report += lines or ["No findings."]
    text = "\n".join(report) + "\n"
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as summary:
            summary.write(text)


if __name__ == "__main__":
    main()
