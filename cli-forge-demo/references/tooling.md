# Tooling — Runner Detection + Recording Stack

> **When to read:** Step 2 (runner) and Step 4 (support artifact). Golden rule: **meet the project where it lives. Never impose a stray `.sh`.**

## Part A — Detect the runner, emit targets there

Probe the repo root (and one level down) and route to the **first** match:

| Probe | Runner | Targets to add |
|---|---|---|
| `Makefile` / `GNUmakefile` | **make** | `demo`, `demo-seed`, `demo-reset`, `demo-gif` |
| `Taskfile.yml` / `Taskfile.yaml` | **go-task** | `demo:run`, `demo:seed`, `demo:reset`, `demo:gif` |
| `justfile` / `.justfile` | **just** | `demo`, `demo-seed`, `demo-reset` |
| `package.json` with `scripts` | **npm/pnpm/yarn** | `"demo:run"`, `"demo:seed"`, `"demo:reset"` |
| `ansible/` or `*.yml` playbooks | **ansible** | `playbooks/demo.yml` with tags `seed` / `reset` / `run` |
| `flux-system/` or `kustomization.yaml` | **flux/kustomize** | `demo` overlay namespace + seed `Job` + `make` wrapper |
| `*.chainsaw.yaml` / chainsaw configured | **chainsaw** | step assertions for k8s demo (doubles as test) |
| `mise.toml` / `.mise.toml` | **mise** | `[tasks.demo*]` |
| `nix` / `flake.nix` | **nix** | `apps.demo` / a `devShell` demo command |
| **none of the above** | propose one | recommend `make` or `just`; only then a documented POSIX `sh` block, clearly fenced |

### Target contract (whatever the runner)

- **seed** — populate deterministic demo state; idempotent; fixed seed + fixed clock; separate from app seed data.
- **reset** — return to `s0`; idempotent (`reset` twice = same state); fast enough to run between takes.
- **run** — (optional) drive the scripted live run.
- **gif / record** — (optional) render the understudy via the recording stack below.

Example `Makefile` shape (adapt to detected runner):

```make
DEMO := docs/demos/quickstart

demo-seed:    ## deterministic demo data (fixed seed + clock)
	SEED=1337 SOURCE_DATE_EPOCH=1700000000 ./... # project's own data tool

demo-reset:   ## idempotent return to s0
	git checkout -- . && git clean -fdq $(DEMO)/_work || true
	$(MAKE) demo-seed

demo-gif:     ## render the understudy
	vhs $(DEMO)/demo.tape

demo: demo-reset ## run the scripted demo
	# drive beats, or open DEMO.md
```

> Use the project's container/orchestration verbs where relevant: `compose down -v && compose up -d` to reset a stack, `kubectl delete ns demo --wait && kubectl apply -k overlays/demo` for k8s.

## Part B — Recording / delivery stack

### Terminal GIF as code — **VHS** (charmbracelet) — preferred for CLI demos
- `.tape` file = the recording **as code** → GIF / MP4 / WebM / PNG frames.
- Reproducible and reviewable in PRs; can serve as an **integration test** (compare against a golden render).
- Needs `ttyd` + `ffmpeg` on PATH.
- See `gif-video.md` for tape syntax, sizing, and caption patterns.

### Terminal recording — **asciinema**
- `asciinema rec demo.cast` → lightweight text `.cast`.
- Convert: **`agg`** → animated GIF; **`svg-term-cli`** / **`termsvg`** / **termtosvg** → animated SVG for READMEs (selectable text, tiny).
- `asciinema-scripted` (YAML) for fully scripted casts.
- The `.cast` is an excellent **understudy**: plays in a terminal or embeds on a page, no video weight.

### Scripted live typing — **demo-magic** (only if the project has no better runner)
- `pe`/`pei` simulate typing then run on ENTER; `Hide`/`Show` equivalents for backstage setup.
- Prefer wiring the live run into the project's runner; reach for demo-magic only as a portable fallback.

### Video + subtitles
- Any screen recorder for GUI/web demos (VHS is terminal-only).
- **Always** ship a `.vtt` (WebVTT) caption track — accessibility is non-negotiable. Keep captions ≤ 2 lines, synced to beats.

## Decision: gif vs cast vs video

| Want | Use |
|---|---|
| Reproducible, scripted, terminal, in CI | **VHS** `.tape` |
| Tiny, selectable-text, README embed | **asciinema** → `svg-term` |
| Quick share, terminal, no setup | **asciinema** → `agg` GIF |
| GUI / web / spoken narration | **screencast + WebVTT** |

When unsure and the demo is terminal-based: **VHS**. It is the most reproducible and the only one that doubles as a test.
