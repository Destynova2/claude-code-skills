# CLAUDE.md — cli-code-skills

## Skills installation

Skills are installed as **copies** in `~/.claude/skills/` for Claude Code and
`~/.codex/skills/` for Codex (global, available in all projects).
Source of truth is this repo (`~/workspace/cli-code-skills/`).

**After modifying a skill in this repo, copy it to both runtimes:**
```bash
scripts/install_skills.sh
```

Or install only one runtime:
```bash
scripts/install_skills.sh --claude
scripts/install_skills.sh --codex
```

The installer removes each destination skill before copying it. That avoids stale
files when a reference is renamed or deleted.

**Shared files** (`gotchas.md` and `shared/`) are referenced by root `SKILL.md`
files as `../<name>` and by `references/` files as `../../<name>`.
The installer copies them to the skills root for both runtimes.

Do NOT use symlinks — use real copies.

## Validation

Before committing or installing changes, run:

```bash
python3 scripts/validate_skills.py
```

The validator checks frontmatter, skill counts, README/CLAUDE inventories,
shared-file paths, and Claude/Codex-neutral `cli-cycle` orchestration.

## Current skills (33)

**Audit (10):** cli-audit-code, cli-audit-doc, cli-audit-drift, cli-audit-review, cli-audit-shell, cli-audit-sync, cli-audit-tangle, cli-audit-test, cli-audit-wizard, cli-audit-xray

**Cycle (1):** cli-cycle

**Forge (20):** cli-forge-arch, cli-forge-chef, cli-forge-choice-ux, cli-forge-demo, cli-forge-doc, cli-forge-github, cli-forge-hld, cli-forge-infra, cli-forge-lld, cli-forge-oci-rootless, cli-forge-perf, cli-forge-pipeline, cli-forge-plume, cli-forge-prez, cli-forge-profile, cli-forge-quorum, cli-forge-readme, cli-forge-resilience, cli-forge-schema, cli-forge-tree

**Git (1):** cli-git-conventional

**Watermark (1):** cli-watermark

## Git identity

Use `clement <cliard@a00.fr>` for this repo. Never use naval-group email.

## Commit style

This repo uses the `cli-git-conventional` skill. Never add `Co-Authored-By` trailers.
Follow Conventional Commits v1.0.0 spec. Ghostwriter style — human voice, no AI markers.
