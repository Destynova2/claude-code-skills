#!/usr/bin/env python3
"""Validate repository-level invariants for cli-code-skills."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


WARNINGS: list[str] = []


def warn(message: str) -> None:
    """Record a non-blocking guidance violation, reported at the end."""
    WARNINGS.append(message)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def skill_dirs() -> list[Path]:
    return sorted(
        p for p in ROOT.glob("cli-*") if p.is_dir() and (p / "SKILL.md").is_file()
    )


def frontmatter(text: str, path: Path) -> str:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        fail(f"{path} has no YAML frontmatter")
    return match.group(1)


def frontmatter_has_key(fm: str, key: str) -> bool:
    return bool(re.search(rf"^{re.escape(key)}:\s*.+", fm, re.MULTILINE))


# Limits from the Agent Skills spec:
# https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/best-practices
NAME_MAX = 64
DESCRIPTION_MAX = 1024
# Anthropic recommends keeping the SKILL.md body under 500 lines so it stays
# cheap to load once the skill triggers. Warn rather than fail: a few large
# generators predate the guidance and splitting them is a separate change.
BODY_MAX_LINES = 500


def frontmatter_value(fm: str, key: str) -> str:
    """Return a frontmatter scalar, joining YAML line folds into one string."""
    match = re.search(
        rf"^{re.escape(key)}:\s*(.*?)(?=\n[A-Za-z_-]+:|\Z)", fm, re.DOTALL | re.MULTILINE
    )
    if not match:
        return ""
    value = " ".join(match.group(1).split())
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value


def check_frontmatter(skills: list[Path]) -> None:
    seen: set[str] = set()
    for skill in skills:
        path = skill / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        fm = frontmatter(text, path)
        for key in ("name", "description"):
            if not frontmatter_has_key(fm, key):
                fail(f"{path} missing frontmatter key: {key}")
        name = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE).group(1).strip()
        if name != skill.name:
            fail(f"{path} name={name!r} does not match directory {skill.name!r}")
        if name in seen:
            fail(f"duplicate skill name: {name}")
        seen.add(name)

        if len(name) > NAME_MAX:
            fail(f"{path} name is {len(name)} chars, spec limit is {NAME_MAX}")
        if not re.fullmatch(r"[a-z0-9-]+", name):
            fail(f"{path} name {name!r} must be lowercase letters, digits, hyphens")

        description = frontmatter_value(fm, "description")
        if len(description) > DESCRIPTION_MAX:
            fail(
                f"{path} description is {len(description)} chars, "
                f"spec limit is {DESCRIPTION_MAX}"
            )

        body_lines = len(text[text.index("\n---\n", 3) + 5 :].splitlines())
        if body_lines > BODY_MAX_LINES:
            warn(f"{path} body is {body_lines} lines, guidance is <{BODY_MAX_LINES}")


def check_readme(skills: list[Path]) -> None:
    readme = read("README.md")
    expected_count = len(skills)

    badge = re.search(r"skills-(\d+)-green\.svg", readme)
    if not badge:
        fail("README.md has no skills badge")
    if int(badge.group(1)) != expected_count:
        fail(f"README.md badge says {badge.group(1)} skills, found {expected_count}")

    for skill in skills:
        if f"/{skill.name}" not in readme and f"{skill.name}/" not in readme:
            fail(f"README.md does not mention {skill.name}")

    required = [
        "scripts/install_skills.sh",
        "--claude",
        "--codex",
        "shared",
        "gotchas.md",
    ]
    for needle in required:
        if needle not in readme:
            fail(f"README.md installation docs missing {needle}")


def check_claude(skills: list[Path]) -> None:
    claude = read("CLAUDE.md")
    expected_count = len(skills)
    match = re.search(r"Current skills \((\d+)\)", claude)
    if not match:
        fail("CLAUDE.md has no Current skills count")
    if int(match.group(1)) != expected_count:
        fail(f"CLAUDE.md says {match.group(1)} skills, found {expected_count}")

    current = claude.split("## Current skills", 1)[1].split("## Git identity", 1)[0]
    for skill in skills:
        if skill.name not in current:
            fail(f"CLAUDE.md Current skills does not mention {skill.name}")

    for needle in (
        "scripts/install_skills.sh",
        "~/.claude/skills",
        "~/.codex/skills",
        "shared",
        "gotchas.md",
    ):
        if needle not in claude:
            fail(f"CLAUDE.md installation docs missing {needle}")


def check_installer() -> None:
    installer = read("scripts/install_skills.sh")
    for needle in (
        "$HOME/.claude/skills",
        "$HOME/.codex/skills",
        "gotchas.md",
        "shared",
        "rm -rf",
    ):
        if needle not in installer:
            fail(f"scripts/install_skills.sh missing {needle}")


def check_shared_paths(skills: list[Path]) -> None:
    for skill in skills:
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        if "../../shared/" in text:
            fail(f"{skill}/SKILL.md uses ../../shared from root skill file")
        if "../../gotchas.md" in text:
            fail(f"{skill}/SKILL.md uses ../../gotchas.md from root skill file")

    shared_readme = read("shared/README.md")
    if "../shared/<file>.md" not in shared_readme:
        fail("shared/README.md does not document root SKILL.md shared path")
    if "../../shared/<file>.md" not in shared_readme:
        fail("shared/README.md does not document references/ shared path")


def check_cycle_runtime_neutrality() -> None:
    skill = read("cli-cycle/SKILL.md")
    orchestration = read("cli-cycle/references/orchestration.md")

    if "SKILLS_ROOT" not in skill:
        fail("cli-cycle/SKILL.md does not describe SKILLS_ROOT resolution")
    if "SKILLS_ROOT" not in orchestration:
        fail("cli-cycle orchestration does not use SKILLS_ROOT")
    forbidden = [
        "Read the skill instructions from ~/.claude/skills",
        "Read ~/.claude/skills/gotchas.md",
        "`~/.claude/skills/shared/result-schema.md`",
    ]
    for needle in forbidden:
        if needle in orchestration:
            fail(f"cli-cycle orchestration still hardcodes Claude path: {needle}")


def check_ci() -> None:
    workflow = read(".github/workflows/validate.yml")
    if "scripts/validate_skills.py" not in workflow:
        fail(".github/workflows/validate.yml does not run the skill validator")


# Rows like: | C1 | Naming & Readability | 8% | ... |
WEIGHT_ROW = re.compile(r"^\|\s*([A-Z]{1,3}\d{1,2})\s*\|[^|]*\|\s*(\d{1,3})%\s*\|", re.M)


def weight_table(text: str) -> dict[str, int]:
    return {i: int(w) for i, w in WEIGHT_ROW.findall(text)}


def check_scoring_weights(skills: list[Path]) -> None:
    """Scoring skills publish weighted dimensions; the weights must total 100%.

    A skill that scores out of 97% or 103% silently produces wrong grades, and
    the SKILL.md table and its references/scoring.md copy are edited separately,
    so they drift. Both properties are cheap to check and expensive to notice.
    """
    for skill in skills:
        tables = {}
        for path in [skill / "SKILL.md", *sorted(skill.glob("references/*.md"))]:
            if not path.is_file():
                continue
            table = weight_table(path.read_text(encoding="utf-8"))
            # Fewer than 4 rows is prose that happens to look tabular.
            if len(table) < 4:
                continue
            tables[path] = table
            total = sum(table.values())
            if total != 100:
                fail(f"{path} scoring weights sum to {total}%, expected 100%")

        canonical = tables.get(skill / "SKILL.md")
        if canonical is None:
            continue
        for path, table in tables.items():
            if path.name == "SKILL.md":
                continue
            drift = {
                key: (canonical.get(key), table.get(key))
                for key in set(canonical) | set(table)
                if canonical.get(key) != table.get(key)
            }
            if drift:
                fail(f"{path} weights disagree with {skill.name}/SKILL.md: {drift}")


def main() -> int:
    skills = skill_dirs()
    if not skills:
        fail("no cli-* skills found")

    check_frontmatter(skills)
    check_scoring_weights(skills)
    check_readme(skills)
    check_claude(skills)
    check_installer()
    check_shared_paths(skills)
    check_cycle_runtime_neutrality()
    check_ci()

    for message in WARNINGS:
        print(f"WARN: {message}")

    print(f"OK: {len(skills)} skills validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
