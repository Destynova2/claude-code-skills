#!/usr/bin/env bash
set -eu

# Install the repo skills (source of truth) into the Claude and Codex runtimes,
# as real copies. The repo -> runtime direction is the safe one; this script
# refuses to overwrite a runtime copy that was edited in place and not yet
# brought back into the repo, so an in-place edit is never silently destroyed.
#
# Usage:
#   scripts/install_skills.sh                 install into both runtimes
#   scripts/install_skills.sh --claude        install into Claude only
#   scripts/install_skills.sh --codex         install into Codex only
#   scripts/install_skills.sh --check         report divergence, change nothing
#   scripts/install_skills.sh --pull-claude   copy Claude edits back into the repo
#   scripts/install_skills.sh --pull-codex    copy Codex edits back into the repo
#   scripts/install_skills.sh --force ...     overwrite even runtime-ahead edits

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
FORCE=0
MANIFEST_NAME=".skills-manifest"

sha() { sha256sum "$1" 2>/dev/null | cut -d' ' -f1; }

usage() {
  echo "Usage: scripts/install_skills.sh [--claude] [--codex] [--check]" \
       "[--pull-claude] [--pull-codex] [--force]"
}

# Managed files (paths relative to $1): every cli-*/ dir that carries a
# SKILL.md, all of shared/, and gotchas.md. The manifest itself is not managed.
managed_relpaths() {
  ( CDPATH= cd -- "$1" 2>/dev/null || exit 0
    for d in cli-*/; do
      [ -f "${d}SKILL.md" ] || continue
      find "$d" -type f
    done
    [ -d shared ] && find shared -type f
    [ -f gotchas.md ] && printf 'gotchas.md\n'
  )
}

# Recorded sha for a relpath in a manifest (empty if absent).
man_sha() {
  [ -f "$1" ] || return 0
  awk -v r="$2" '$2 == r { print $1; exit }' "$1"
}

# Classify one managed file: prints "insync" | "repo-ahead" | "runtime-ahead".
classify() { # dest manifest rel
  s="$1/$3"; d="$ROOT/$3"; man="$2"; rel="$3"
  [ -f "$s" ] || { echo runtime-missing; return; }
  dsha="$(sha "$s")"; rsha="$(sha "$d")"
  [ "$dsha" = "$rsha" ] && { echo insync; return; }
  msha="$(man_sha "$man" "$rel")"
  # dest == what we last installed, repo moved on -> a normal update.
  if [ -n "$msha" ] && [ "$dsha" = "$msha" ]; then echo repo-ahead; return; fi
  # dest differs from both repo and last install -> unrecorded runtime work.
  echo runtime-ahead
}

# Refuse to overwrite runtime-ahead edits unless --force.
guard_inplace() { # dest label
  dest="$1"; label="$2"; man="$dest/$MANIFEST_NAME"
  [ -f "$man" ] || return 0          # no baseline yet: nothing to protect
  conflicts=""
  while read -r rel; do
    [ "$(classify "$dest" "$man" "$rel")" = runtime-ahead ] &&
      conflicts="$conflicts $rel"
  done < <(managed_relpaths "$ROOT")
  [ -z "$conflicts" ] && return 0
  if [ "$FORCE" -eq 1 ]; then
    echo "warning: overwriting runtime-ahead edits in $label (--force):" >&2
    for r in $conflicts; do echo "  $r" >&2; done
    return 0
  fi
  {
    echo "refusing to overwrite $label: these files were edited in place and are not in the repo:"
    for r in $conflicts; do echo "  $r"; done
    echo "reconcile:  scripts/install_skills.sh --pull-$label   (copies them into the repo, then commit)"
    echo "discard:    scripts/install_skills.sh --force --$label"
  } >&2
  exit 3
}

write_manifest() { # dest
  dest="$1"; man="$dest/$MANIFEST_NAME"; tmp="$man.tmp"
  : > "$tmp"
  while read -r rel; do
    f="$dest/$rel"
    [ -f "$f" ] && printf '%s %s\n' "$(sha "$f")" "$rel" >> "$tmp"
  done < <(managed_relpaths "$ROOT")
  mv "$tmp" "$man"
}

install_into() { # dest label
  dest="$1"; label="$2"
  mkdir -p "$dest"
  guard_inplace "$dest" "$label"
  for skill_dir in "$ROOT"/cli-*; do
    [ -d "$skill_dir" ] || continue
    [ -f "$skill_dir/SKILL.md" ] || continue
    name="$(basename "$skill_dir")"
    rm -rf "$dest/${name:?}"
    cp -R "$skill_dir" "$dest/$name"
  done
  rm -rf "$dest/shared"
  cp -R "$ROOT/shared" "$dest/shared"
  cp "$ROOT/gotchas.md" "$dest/gotchas.md"
  write_manifest "$dest"
  echo "installed -> $dest"
}

pull_from() { # dest label
  dest="$1"; label="$2"; any=0
  while read -r rel; do
    s="$dest/$rel"; d="$ROOT/$rel"
    [ -f "$s" ] || continue
    if ! cmp -s "$s" "$d"; then
      mkdir -p "$(dirname "$d")"
      cp "$s" "$d"
      echo "  pulled $rel"
      any=1
    fi
  done < <({ managed_relpaths "$ROOT"; managed_relpaths "$dest"; } | sort -u)
  if [ "$any" -eq 0 ]; then
    echo "nothing to pull from $label (repo already matches)"
  else
    echo "pulled $label edits into the repo. Review: git diff; python3 scripts/validate_skills.py; commit."
  fi
}

check_dest() { # dest label
  dest="$1"; label="$2"; man="$dest/$MANIFEST_NAME"; diffs=0
  echo "== $label ($dest) =="
  while read -r rel; do
    verdict="$(classify "$dest" "$man" "$rel")"
    case "$verdict" in
      insync) ;;
      repo-ahead)      echo "  repo-ahead      $rel  (install updates the runtime)"; diffs=$((diffs + 1)) ;;
      runtime-ahead)   echo "  RUNTIME-AHEAD   $rel  (edited in place, not in repo)"; diffs=$((diffs + 1)) ;;
      runtime-missing) echo "  runtime-missing $rel  (install adds it)"; diffs=$((diffs + 1)) ;;
    esac
  done < <({ managed_relpaths "$ROOT"; managed_relpaths "$dest"; } | sort -u)
  [ "$diffs" -eq 0 ] && echo "  in sync"
}

do_claude=0; do_codex=0; mode=install
for a in "$@"; do
  case "$a" in
    --force)       FORCE=1 ;;
    --check)       mode=check ;;
    --claude)      do_claude=1 ;;
    --codex)       do_codex=1 ;;
    --pull-claude) mode=pull; do_claude=1 ;;
    --pull-codex)  mode=pull; do_codex=1 ;;
    -h|--help)     usage; exit 0 ;;
    *)             usage >&2; exit 2 ;;
  esac
done
if [ "$do_claude" -eq 0 ] && [ "$do_codex" -eq 0 ]; then do_claude=1; do_codex=1; fi

CLAUDE="$HOME/.claude/skills"
CODEX="$HOME/.codex/skills"

case "$mode" in
  install)
    [ "$do_claude" -eq 1 ] && install_into "$CLAUDE" claude
    [ "$do_codex"  -eq 1 ] && install_into "$CODEX"  codex
    ;;
  check)
    [ "$do_claude" -eq 1 ] && check_dest "$CLAUDE" claude
    [ "$do_codex"  -eq 1 ] && check_dest "$CODEX"  codex
    ;;
  pull)
    [ "$do_claude" -eq 1 ] && pull_from "$CLAUDE" claude
    [ "$do_codex"  -eq 1 ] && pull_from "$CODEX"  codex
    ;;
esac
