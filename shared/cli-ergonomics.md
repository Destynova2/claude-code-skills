# Shared — CLI Ergonomics & The 4 Laws

> **Cross-skill reference.** The same ergonomic laws apply whenever a tool asks a human for input or runs in CI: setup wizards (`cli-audit-wizard`), shell scripts (`cli-audit-shell`), agent prompts (`cli-forge-chef`), and operator wrappers around third-party tools (`cli-forge-infra`). Reference it as `../../shared/cli-ergonomics.md`. Each skill keeps its own scoring; this file fixes the **law semantics** so they mean the same thing across surfaces.

## The 4 Laws

| Law | Meaning | Test | Violations |
|---|---|---|---|
| **1. Ask once, derive the rest** | If a value can be computed from another, don't ask. Seed questions only (3-5). | Count derivable questions; each one is a violation. | "What's your domain?" then "What's your ACME URL?" (derivable). Re-prompts on every run. |
| **2. Defaults are decisions** | Every default is an opinionated, justified choice. No empty strings, no `null`, no `# please configure`. | Can the user accept all defaults and get a working system? | Placeholder values, missing defaults, "TODO" in shipped config. |
| **3. Recap before action** | Show the diff/plan before touching state. The user can review and abort. | `--dry-run`, recap step, confirmation prompt before destructive ops. | Apply-without-recap; no preview; no abort path. |
| **4. Config-as-code / idempotent** | The artifact is a file on disk — committable, diffable, re-readable. Re-running is safe and lands on the same state. | Run twice → identical state. Output is in the repo, not hidden. | Black-box state; re-run reprompts everything; non-idempotent apply. |

The full reproducibility/idempotence toolkit (seed, clock, env pins) lives in `../../shared/determinism.md` — Law 4 depends on it.

## Surfaces

The Laws are surface-agnostic, but they look different in each setting.

| Surface | Law 1 (Ask once) | Law 2 (Defaults) | Law 3 (Recap) | Law 4 (Config-as-code) |
|---|---|---|---|---|
| **Interactive CLI** | `getopts` / flags accept once, derive the rest from `$0` and env | Flag defaults in `--help` | `--dry-run` mode | Output goes to a path, not stdout-only |
| **TUI / wizard** | 3-5 seed prompts, derive the rest | Pre-filled fields with sensible values | Final recap screen before write | Writes `config.toml` / `*.yaml` |
| **Agent prompt** | Single prompt with all required context; no follow-up clarifications | Sensible system prompt + tool defaults | Plan-then-act (the agent recaps before tool use) | Prompt is versioned in repo, not pasted ad-hoc |
| **CI batch** | All inputs via env / args at job start | Defaults survive missing env vars | `--check` / dry-run job ahead of apply | Pipeline file is the config, re-runnable |

## Per-skill emphasis

| Skill | What it uses the Laws for |
|---|---|
| `cli-audit-wizard` | Full 4-Laws scoring. The S section is "Law Compliance" with a Pass/Warn/Fail per law and a -5/-15 penalty per violation. |
| `cli-audit-shell` | S9 (CLI Ergonomics, 10% weight) maps Laws 1-3 to shell concretes: `getopts`, `--help`, single entry-point, non-interactive mode for CI (Law 4 covered separately by S10 idempotency). |
| `cli-forge-chef` | Prompt design = CLI design. Each Sous-Chef and Commis prompt should ask once, default sensibly, recap its plan, and live in the repo (committable). |
| `cli-forge-infra` | When choosing or wrapping an ops tool, prefer the path that respects the Laws — a CLI with `--help`, defaults, `--dry-run`, and a config file beats an interactive wizard that asks the same questions on every run. |

## Rule

A tool that violates Law 1 wastes the user's time; Law 2 transfers a decision the author should have made; Law 3 makes mistakes irreversible; Law 4 turns the system into a black box. CLIs, wizards, prompts, and CI jobs are the same surface in different costumes — measure them against the same Laws.
