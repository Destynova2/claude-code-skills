#!/usr/bin/env python3
"""Insert a Contents list into long reference files.

Anthropic's skill-authoring guidance: reference files longer than 100 lines
should open with a table of contents, so that a partial read (Claude often
previews with `head`) still reveals the full scope of what the file covers.

The list is generated from the file's own `##` headings and inserted after the
title block, meaning after the H1 and any `> When to read:` callout. Files that
already have a Contents section, or that have fewer than two `##` headings, are
left alone. Re-running the script is a no-op.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIN_LINES = 100
MIN_HEADINGS = 2

# A fenced code block can contain lines starting with '#', which are comments,
# not headings. Track fences so those are never picked up.
FENCE = re.compile(r"^\s*(```|~~~)")
H2 = re.compile(r"^## +(.+?)\s*$")


def headings(lines: list[str]) -> list[tuple[int, str]]:
    out, in_fence = [], False
    for i, line in enumerate(lines):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = H2.match(line)
        if m:
            out.append((i, m.group(1).strip()))
    return out


def has_toc(lines: list[str]) -> bool:
    head = "\n".join(lines[:30]).lower()
    return "## contents" in head or "**contents" in head or "table of contents" in head


def insertion_point(lines: list[str], first_heading: int) -> int:
    """Return the index to insert at: after the H1 and any intro callout."""
    idx = 0
    for i, line in enumerate(lines[:first_heading]):
        if line.startswith("# "):
            idx = i + 1
            break
    # Absorb a blockquote intro ("> When to read: ...") and its blank lines,
    # so the Contents list sits below the callout rather than splitting it.
    while idx < first_heading:
        line = lines[idx]
        if line.strip() == "" or line.lstrip().startswith(">"):
            idx += 1
            continue
        break
    # A horizontal rule directly after the intro belongs with the intro.
    if idx < first_heading and lines[idx].strip() in {"---", "***"}:
        idx += 1
        while idx < first_heading and lines[idx].strip() == "":
            idx += 1
    return idx


def process(path: Path, apply: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) <= MIN_LINES or has_toc(lines):
        return False
    hs = headings(lines)
    if len(hs) < MIN_HEADINGS:
        return False

    at = insertion_point(lines, hs[0][0])
    block = ["## Contents", ""] + [f"- {title}" for _, title in hs] + ["", "---", ""]
    new = lines[:at] + block + lines[at:]
    if apply:
        path.write_text("\n".join(new) + "\n", encoding="utf-8")
    return True


def main() -> int:
    apply = "--apply" in sys.argv
    targets = sorted(
        set(ROOT.glob("cli-*/references/*.md"))
        | set(ROOT.glob("cli-*/reference.md"))
        | set(ROOT.glob("shared/**/*.md"))
    )
    changed = [p for p in targets if process(p, apply)]
    verb = "updated" if apply else "would update"
    for p in changed:
        print(f"{verb}: {p.relative_to(ROOT)}")
    print(f"{verb} {len(changed)} of {len(targets)} reference files")
    if not apply and changed:
        print("re-run with --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
