#!/usr/bin/env python3
"""Check a Behavioural Contract Packet before it is approved.

The expensive failure is a contract that is faithfully implemented and wrong. Two shapes
of that are checkable here: a mechanism promoted into the binding section, which forbids
implementations that meet the behaviour by another route, and parity behaviour presented
as normative DWN semantics.

Structure is checked in code; the binding statements are judged one question each, all
over one copy of the packet. Nothing here approves a packet: a human does that, after
reading the assumptions the packet says a reviewer should try to falsify.

    tools/check_packet.py .agent/contracts/records-delete-convergence.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

from check_invariant_semantics import ask_many, load_invariants

BINDING = "Required behaviour (binding)"
REQUIRED_SECTIONS = (BINDING, "Assumptions to challenge", "Test matrix", "Controlling invariants")
MAX_STATEMENTS = 40

MECHANISM = (
    "`statement` is one requirement from the binding section of `packet`, which states the "
    "observable behaviour an implementation must produce. Would an implementation that produces "
    "exactly that observable behaviour, using a different data structure, library, algorithm, or "
    "API, nonetheless violate this requirement as written?"
)
PARITY_AS_NORMATIVE = (
    "Does `packet` present current Enbox implementation behaviour as normative DWN semantics — "
    "stating as a requirement of the protocol something it supports only by reference to what the "
    "TypeScript implementation does?"
)


def sections(text: str) -> dict[str, str]:
    out, current = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            out[current] = ""
        elif current:
            out[current] += line + "\n"
    return out


def statements(section: str) -> list[str]:
    """Bullets and sentences from the binding section, each judged on its own."""
    out = []
    for line in section.splitlines():
        line = re.sub(r"^\s*[-*+]\s+|^\s*\d+[.)]\s+", "", line).strip()
        if not line or line.startswith(("|", "#", "```")):
            continue
        out += [part.strip() for part in re.split(r"(?<=[.!?])\s+(?=[A-Z`])", line) if len(part.strip()) > 20]
    return out[:MAX_STATEMENTS]


def cited_ids(text: str) -> list[str]:
    return sorted(set(re.findall(r"\b(?:DWN|ENBOX|DID)-[A-Z]+-\d{3}\b", text)))


def structure_findings(text: str, parsed: dict[str, str], invariants: dict[str, dict]) -> list[str]:
    out = []
    for name in REQUIRED_SECTIONS:
        if not parsed.get(name, "").strip():
            out.append(f"section `{name}` is missing or empty")
    for name in ("Assumptions to challenge", "Test matrix"):
        rows = [
            line for line in parsed.get(name, "").splitlines()
            if line.strip().startswith("|") and not re.fullmatch(r"[|\s:-]+", line.strip())
        ]
        if len(rows) < 2:  # a header row and nothing else
            out.append(f"`{name}` has no rows; a packet approved without it hides what it rests on")
    unknown = [i for i in cited_ids(text) if i not in invariants]
    if unknown:
        out.append(f"cites unknown invariant ids: {', '.join(unknown)}")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("packet", help="path to the Behavioural Contract Packet, or - for stdin")
    parser.add_argument("--threshold", type=float, default=0.6, help="probability at or above which an answer is reported")
    parser.add_argument("--json", action="store_true", help="emit the answers as JSON")
    args = parser.parse_args()

    text = sys.stdin.read() if args.packet == "-" else open(args.packet, encoding="utf-8").read()
    parsed = sections(text)
    invariants = load_invariants(None)
    structural = structure_findings(text, parsed, invariants)
    binding = statements(parsed.get(BINDING, ""))

    key = os.environ.get("TYPESAFE_API_KEY")
    answers: dict[str, float] = {}
    if key and binding:
        questions = {f"s{index}": {"type": "noul", "instructions": f"{MECHANISM}\n\nstatement: {line}"}
                     for index, line in enumerate(binding)}
        questions["parity_as_normative"] = {"type": "noul", "instructions": PARITY_AS_NORMATIVE}
        answers = {name: a["noul"] for name, a in ask_many(key, {"packet": text}, questions).items()}

    mechanism = [(binding[int(name[1:])], probability) for name, probability in answers.items()
                 if name.startswith("s") and probability >= args.threshold]

    if args.json:
        json.dump({
            "packet": args.packet,
            "structure": structural,
            "cited_invariants": cited_ids(text),
            "mechanism_as_contract": [{"statement": s, "probability": round(p, 3)} for s, p in mechanism],
            "parity_as_normative": round(answers.get("parity_as_normative", 0.0), 3) if answers else None,
        }, sys.stdout, indent=2)
        print()
        return

    report = [f"## Packet check: {args.packet}", ""]
    report += [f"- structure: {finding}" for finding in structural]
    report += [f"- mechanism stated as contract ({probability:.2f}): {statement}" for statement, probability in mechanism]
    if answers.get("parity_as_normative", 0.0) >= args.threshold:
        report.append(f"- presents Enbox parity behaviour as normative DWN semantics ({answers['parity_as_normative']:.2f})")
    if len(report) == 2:
        report.append(f"No findings across {len(binding)} binding statement(s).")
    if not key:
        report += ["", "TYPESAFE_API_KEY is not set; only the structural checks ran."]
    elif mechanism:
        report += ["", "Move a mechanism finding to the non-binding reference section, or keep it and say why the mechanism is itself the contract."]
    print("\n".join(report))


if __name__ == "__main__":
    main()
