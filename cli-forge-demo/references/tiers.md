# Tiers — Intent × Support Matrix

> **When to read:** Step 0. A demo is one cell of a 2-axis grid: **who it's for** × **how it's delivered**. Don't enumerate all cells — pick one value per axis.

## Axis 1 — Intent / audience

Ask if not supplied via `--intent`. **Never guess the audience** — the same feature demoed to a developer and to a buyer is two different shows.

| Intent | Audience | The one thing it must prove | Tone |
|---|---|---|---|
| **technique** | devs, ops, SREs; conference; internal review | "it works end-to-end, and here's the mechanism" | precise, fast, command-driven |
| **fonctionnel** | PO, stakeholders; sprint review; acceptance | "the feature delivers the agreed outcome" | outcome-driven, plain language |
| **commercial** | prospect, buyer, exec; pitch, sales call | "this removes *your specific* pain" | situation-first, value-driven |
| **pédagogique** | new user, contributor; onboarding, tutorial | "you can reproduce this yourself" | slow, verifiable, forgiving |

Default narrative framework per intent lives in `dramaturgy.md`.

## Axis 2 — Support / medium

**Recommend dynamically; let the user force with `--support`.** Read the signals, propose the best compromise, state the reason in one line, then proceed.

| Support | Best when | Tooling | Notes |
|---|---|---|---|
| **live** | audience present; conference, review, sales call | project runner + understudy recording | always pair with a backup |
| **gif** | CLI/TUI tool; README needs motion; chat/issue | **VHS** `.tape` → GIF/MP4 | reproducible; doubles as integration test; ideal for OpenBao & ops CLIs |
| **cast** | docs site, copy-pasteable, lightweight embed | **asciinema** `.cast` → `agg` (GIF) / `svg-term` (SVG) | text-based, tiny, selectable text |
| **video** | async, accessibility, wide/mixed audience | screencast + **WebVTT** captions | captions are mandatory, not optional |
| **interactive** | onboarding; "let them try"; tutorial | teachme / Killercoda / CodeTour-style stepped markdown | self-guided "next-next"; verification per step |

### Dynamic recommendation logic

```
is CLI/TUI tool AND output is mostly terminal?   → gif (VHS)        # OpenBao, kubectl, a CLI
README/docs need an embeddable, lightweight clip? → cast (asciinema)
audience will be physically present?              → live (+ understudy)
goal is "users learn to do it themselves"?        → interactive
audience is broad/async or accessibility matters? → video (+ subtitles)
GUI/web app, not terminal?                        → video or live (VHS is terminal-only)
```

If two fit, prefer the **more reproducible** one (gif/cast over video; interactive over live for onboarding). Always state: *"Picked X because Y — force another with `--support`."*

## How dramaturgy shifts per cell (examples)

| Cell | What changes |
|---|---|
| technique × gif | tight VHS tape, real commands, no narration; caption overlays for the 2-3 key lines |
| commercial × live | open on the dashboard result (Do-It), 90 s on their situation first, never show config screens |
| fonctionnel × video | one user story, acceptance-criteria voiceover, subtitles, < 3 min |
| pédagogique × interactive | every step copyable + a verification command + "if you see X, you're on track" |
| technique × live | live-coding sandwich (slide → demo → slide), aliases, understudy cast ready |

## Multi-output

A single kit can render **several supports from one source of truth** (the `DEMO.md` beats):
- the **VHS tape** is generated from the same beat commands → live + gif stay in sync;
- the **interactive walkthrough** reuses the beats as steps;
- the **cast** is recorded from one clean run of the runner's `demo` target.

Keep the beats as the single source; never let supports drift apart.
