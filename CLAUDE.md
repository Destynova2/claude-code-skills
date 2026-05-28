# CLAUDE.md — cli-code-skills

## Skills installation

Skills are installed as **copies** in `~/.claude/skills/` (global, available in all projects).
Source of truth is this repo (`~/workspace/cli-code-skills/`).

**After modifying a skill in this repo, copy it to `~/.claude/skills/` :**
```bash
rm -rf ~/.claude/skills/cli-audit-wizard && cp -r cli-audit-wizard ~/.claude/skills/cli-audit-wizard
```

Or copy all skills at once:
```bash
for d in cli-*/; do n="${d%/}"; rm -rf ~/.claude/skills/"$n" && cp -r "$n" ~/.claude/skills/"$n"; done
```

The `rm -rf` before each copy is required: `cp -r src dest` nests `src` inside `dest`
when `dest` already exists (creating `dest/src`) instead of replacing it.

**Shared files** (`gotchas.md` and `shared/`) are referenced by skills as `../../<name>`
and must also be installed at the skills root:
```bash
cp gotchas.md ~/.claude/skills/gotchas.md
rm -rf ~/.claude/skills/shared && cp -r shared ~/.claude/skills/shared
```

Do NOT use symlinks — use real copies.

## Current skills (27)

**Audit (9):** cli-audit-code, cli-audit-doc, cli-audit-drift, cli-audit-shell, cli-audit-sync, cli-audit-tangle, cli-audit-test, cli-audit-wizard, cli-cycle

**Forge (16):** cli-forge-arch, cli-forge-chef, cli-forge-demo, cli-forge-doc, cli-forge-github, cli-forge-hld, cli-forge-infra, cli-forge-lld, cli-forge-oci-rootless, cli-forge-pipeline, cli-forge-prez, cli-forge-quorum, cli-forge-readme, cli-forge-resilience, cli-forge-schema, cli-forge-tree

**Git (1):** cli-git-conventional

**Watermark (1):** cli-watermark

## Git identity

Use `clement <cliard@a00.fr>` for this repo. Never use naval-group email.

## Commit style

This repo uses the `cli-git-conventional` skill. Never add `Co-Authored-By` trailers.
Follow Conventional Commits v1.0.0 spec. Ghostwriter style — human voice, no AI markers.
