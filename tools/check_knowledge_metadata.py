#!/usr/bin/env python3
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

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

check_guide_dir("builders", "builders")
check_guide_dir("implementation", "implementation")
check_guide_dir("conformance", "conformance")

for warning in warnings:
    print(f"WARNING: {warning}")
for error in errors:
    print(f"ERROR: {error}", file=sys.stderr)

if errors:
    sys.exit(1)

print("Knowledge metadata check passed.")
