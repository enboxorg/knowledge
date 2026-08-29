#!/usr/bin/env python3
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_INVARIANT_CONTRACTS = {"normative", "enbox-parity", "implementation-contract"}

errors: list[str] = []
warnings: list[str] = []


def parse_front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    result: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def check_date(path: Path, key: str, value: str) -> None:
    if not DATE_RE.match(value):
        errors.append(f"{path}: {key} must be YYYY-MM-DD")
        return
    try:
        reviewed = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        errors.append(f"{path}: {key} is not a valid date")
        return
    age = (date.today() - reviewed).days
    if age > 180:
        warnings.append(f"{path}: {key} is {age} days old; consider source review")


def check_guide_dir(dirname: str, domain: str) -> None:
    directory = ROOT / dirname
    if not directory.exists():
        return
    for path in sorted(directory.glob("*.md")):
        if path.name == "README.md":
            continue
        meta = parse_front_matter(path)
        for key in ("domain", "kind", "reviewed"):
            if not meta.get(key):
                errors.append(f"{path}: missing front-matter field {key}")
        if meta.get("domain") and meta["domain"] != domain:
            errors.append(f"{path}: domain must be {domain}")
        if meta.get("kind") and meta["kind"] != "guide":
            errors.append(f"{path}: kind must be guide")
        if meta.get("reviewed"):
            check_date(path, "reviewed", meta["reviewed"])


def check_invariants() -> None:
    directory = ROOT / "invariants"
    if not directory.exists():
        return
    seen_ids: dict[str, Path] = {}
    for path in sorted(directory.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        if not isinstance(payload, list):
            errors.append(f"{path}: top-level invariant document must be an array")
            continue
        for index, item in enumerate(payload):
            prefix = f"{path}[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{prefix}: invariant must be an object")
                continue
            invariant_id = item.get("id")
            statement = item.get("statement")
            contract = item.get("contract")
            sources = item.get("sources")
            if not isinstance(invariant_id, str) or not invariant_id.strip():
                errors.append(f"{prefix}: missing non-empty id")
            elif invariant_id in seen_ids:
                errors.append(f"{prefix}: duplicate id {invariant_id}; first seen in {seen_ids[invariant_id]}")
            else:
                seen_ids[invariant_id] = path
            if not isinstance(statement, str) or not statement.strip():
                errors.append(f"{prefix}: missing non-empty statement")
            if contract not in ALLOWED_INVARIANT_CONTRACTS:
                errors.append(f"{prefix}: contract must be one of {sorted(ALLOWED_INVARIANT_CONTRACTS)}")
            if not isinstance(sources, list) or not sources or not all(isinstance(source, str) and source.strip() for source in sources):
                errors.append(f"{prefix}: sources must be a non-empty list of strings")


for path in sorted((ROOT / "dwn").glob("*.md")):
    meta = parse_front_matter(path)
    for key in ("domain", "kind", "spec", "spec-reviewed"):
        if not meta.get(key):
            errors.append(f"{path}: missing front-matter field {key}")
    if meta.get("domain") and meta["domain"] != "dwn":
        errors.append(f"{path}: domain must be dwn")
    if meta.get("kind") and meta["kind"] != "normative":
        errors.append(f"{path}: kind must be normative")
    if meta.get("spec-reviewed"):
        check_date(path, "spec-reviewed", meta["spec-reviewed"])

for path in sorted((ROOT / "enbox").glob("*.md")):
    if path.name == "README.md":
        continue
    meta = parse_front_matter(path)
    for key in ("domain", "kind", "upstream-baseline", "reviewed"):
        if not meta.get(key):
            errors.append(f"{path}: missing front-matter field {key}")
    if meta.get("domain") and meta["domain"] != "enbox":
        errors.append(f"{path}: domain must be enbox")
    if meta.get("kind") and meta["kind"] != "implementation":
        errors.append(f"{path}: kind must be implementation")
    baseline = meta.get("upstream-baseline")
    if baseline and not SHA_RE.match(baseline):
        errors.append(f"{path}: upstream-baseline must be a 40-character lowercase commit SHA")
    if meta.get("reviewed"):
        check_date(path, "reviewed", meta["reviewed"])

check_guide_dir("learning", "learning")
check_guide_dir("builders", "builders")
check_guide_dir("examples", "examples")
check_guide_dir("implementation", "implementation")
check_guide_dir("conformance", "conformance")
check_guide_dir("agents", "agents")
check_invariants()

for warning in warnings:
    print(f"WARNING: {warning}")
for error in errors:
    print(f"ERROR: {error}", file=sys.stderr)

if errors:
    sys.exit(1)

print("Knowledge metadata check passed.")