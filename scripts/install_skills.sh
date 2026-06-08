#!/usr/bin/env bash
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

install_into() {
  dest="$1"
  mkdir -p "$dest"

  for skill_dir in "$ROOT"/cli-*; do
    [ -d "$skill_dir" ] || continue
    [ -f "$skill_dir/SKILL.md" ] || continue
    name="$(basename "$skill_dir")"
    rm -rf "$dest/$name"
    cp -R "$skill_dir" "$dest/$name"
  done

  rm -rf "$dest/shared"
  cp -R "$ROOT/shared" "$dest/shared"
  cp "$ROOT/gotchas.md" "$dest/gotchas.md"
}

if [ "$#" -eq 0 ]; then
  install_into "$HOME/.claude/skills"
  install_into "$HOME/.codex/skills"
  exit 0
fi

for target in "$@"; do
  case "$target" in
    --claude) install_into "$HOME/.claude/skills" ;;
    --codex) install_into "$HOME/.codex/skills" ;;
    *)
      echo "Usage: scripts/install_skills.sh [--claude] [--codex]" >&2
      exit 2
      ;;
  esac
done
