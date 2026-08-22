#!/usr/bin/env python3
"""Check the evaluation cases in evals/cases/.

This is a structural harness, not a grader. Judging whether a skill produced a
good audit needs a model in the loop; what this script does is keep the case
files honest so that a human or model review starts from correct data:

  - every case is valid JSON with the fields the harness expects
  - every skill named by a case actually exists in the repo
  - every fixture path a case points at actually exists
  - every dimension ID cited (S1, C7, ...) is defined by that skill's SKILL.md

That last check is the valuable one. A case file that asserts "S9 flags rm -rf"
looks authoritative and is worse than no case at all when S9 is really CLI
Ergonomics. This catches exactly that class of mistake.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals" / "cases"
REQUIRED = ("id", "skills", "query", "expected_behavior")

# A dimension ID as used in the scoring tables: S1, C12, D3 ...
DIM = re.compile(r"\b([A-Z]{1,3}\d{1,2})\b")


def defined_dimensions(skill: Path) -> set[str]:
    """IDs that appear in a leading table cell of the skill or its references."""
    found: set[str] = set()
    paths = [skill / "SKILL.md", *skill.glob("references/*.md")]
    for path in paths:
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            found |= set(re.findall(r"^\|\s*([A-Z]{1,3}\d{1,2})\s*\|", text, re.M))
    return found


def main() -> int:
    errors: list[str] = []
    cases = sorted(CASES.glob("*.json"))
    if not cases:
        print("no evaluation cases found")
        return 0

    for path in cases:
        rel = path.relative_to(ROOT)
        try:
            case = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}: invalid JSON: {exc}")
            continue

        for key in REQUIRED:
            if not case.get(key):
                errors.append(f"{rel}: missing or empty field {key!r}")
        if case.get("id") and case["id"] != path.stem:
            errors.append(f"{rel}: id {case['id']!r} does not match filename")

        for name in case.get("files", []):
            if not (ROOT / name).exists():
                errors.append(f"{rel}: fixture does not exist: {name}")

        known: set[str] = set()
        for name in case.get("skills", []):
            skill = ROOT / name
            if not (skill / "SKILL.md").is_file():
                errors.append(f"{rel}: unknown skill {name!r}")
                continue
            known |= defined_dimensions(skill)

        if known:
            text = " ".join(case.get("expected_behavior", []) + case.get("must_not", []))
            for dim in sorted(set(DIM.findall(text))):
                if dim not in known:
                    errors.append(
                        f"{rel}: cites dimension {dim}, which no listed skill defines"
                    )

    for message in errors:
        print(f"FAIL: {message}")
    if errors:
        return 1
    print(f"OK: {len(cases)} evaluation case(s) checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
