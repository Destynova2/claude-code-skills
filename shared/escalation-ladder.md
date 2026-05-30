# Shared — Escalation Ladder (Headless → GUI)

> **Cross-skill reference.** Canonical 5-rung ladder for "I need to automate X but no obvious headless path exists." Reference it as `../../shared/escalation-ladder.md`. The rule: **climb up only when the rung below is proven infeasible**, never when assumed so. Used by `cli-forge-perf` (xctrace vs GPU debugger), `cli-forge-infra` (CLI > Helm > Operator > Terraform), `cli-audit-wizard` (setup CLI vs GUI driving), `cli-forge-chef` (tmux send-keys as last resort), and `cli-forge-oci-rootless` (service API > admin GUI). Complementary to `../../shared/done-gate.md` (per-artifact gate) and `../../shared/gate-ladder.md` (system proof rungs).

## The 5 rungs

| Rung | Path | Cost | Acceptable for |
|---|---|---|---|
| **1. CLI / public API** | The intended interface (`xcrun`, REST, gRPC, SDK) | low | always preferred — exhaust this rung first |
| **2. Documented data file** | Parse the file the tool writes (`.xcresult`, `.gputrace`, `.trace`, JSON exports) | low-medium | stable / documented formats |
| **3. Private API / dylib** | `dlopen` + ObjC runtime / undocumented symbols / private frameworks | medium-high | one-off research; **never** in shipped public tooling — EULA risk + breaks every release |
| **4. Reverse-engineered protocol** | Sniff IPC the GUI uses to talk to its daemon | high | local daemons only; brittle, undocumented |
| **5. GUI automation** | macOS Accessibility / Windows UIA / Linux AT-SPI / `cua-driver` / `osascript` | very high | **last resort** — only if recurring + GUI stable + budget for upkeep |

## Rules

1. **Exhaust the lower rungs first.** Most "no headless path exists" claims are false. Check `xcrun --find`, hidden subcommands, private framework CLI counterparts, and file formats documented in headers (`/Library/Frameworks/**/Headers/`).
2. **Climb in order.** A rung-5 GUI automation built before checking rungs 1-2 is malpractice.
3. **Cost of rung n+1 ≥ 3× cost of rung n.** Move up only when the lower rung is *proven* infeasible — not assumed.
4. **Rung 3+ never ships in public tooling.** Private API or GUI-piloting code can live in personal scripts, internal CI, or your own product. A shared library / MCP / skill that propagates these to others becomes a maintenance trap and a legal hazard.
5. **Rung 5 requires four conditions, all four:** (a) the task is recurring, (b) the GUI is stable across versions, (c) a test suite fails when the GUI changes, (d) a documented fallback exists when it breaks. Miss any → do it manually instead.

## Anti-pattern: the "let's just drive the GUI" reflex

Symptoms:
- *"It's only 40 min, I'll just script Xcode / the IDE / whatever."*
- 4h later: still fighting Accessibility, the GUI crashes on init, you're capturing screenshots of error dialogs.
- The lower rung you skipped (`xctrace` headless, `.xcresult` parsing, framework `dlopen`) would have closed it in 5 min.

Rule: when a session smells like rung 5, **stop and search rungs 1-4 for 15 min first**. If still nothing, ask: *is this actually recurring, or is this one-shot?* If one-shot — do it manually and move on.

## Per-skill application

| Skill | How it applies |
|---|---|
| `cli-forge-perf` | `xctrace` Metal System Trace (rung 1) before GPU debugger (`.gputrace` = rung 5). On CUDA: Nsight Systems (rung 1) vs Nsight Graphics (rung 5). |
| `cli-forge-infra` | "Pick the simplest config path: CLI > Helm > Operator > Terraform" = rung-1 maximalism applied to ops integration. |
| `cli-audit-wizard` | A wizard is a rung-1 setup CLI, not a rung-5 GUI driving. The 4 Laws (`../../shared/cli-ergonomics.md`) are unreachable from rung 5 (no "ask once" possible when the only input is mouse clicks). |
| `cli-forge-chef` | `tmux send-keys` is rung 5 inside the Brigade — used only as a fallback to unblock UI permissions (G6, G37). Gate it on quorum and log the decision. |
| `cli-forge-oci-rootless` | A service with a CLI or REST API is rung 1 — never drive its admin GUI when an API exists. |
