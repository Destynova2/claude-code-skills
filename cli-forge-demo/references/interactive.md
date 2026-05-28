# Interactive Walkthrough — Self-Guided "Next-Next"

> **When to read:** Step 4 when support = interactive. The audience downloads the project and steps through it alone, with a verification at each step.

## What it is

A **matinée**: the demo replayed by the audience themselves. It is stepped markdown with copyable commands and a check after each step, in the lineage of Google Cloud Shell **teachme** tutorials, **Killercoda** scenarios, and VS Code **CodeTour**. The defining trait: the learner moves Next / Previous and **cannot get silently stuck** — every step tells them what success looks like.

## Format choice

| Target environment | Emit |
|---|---|
| Repo + local shell (most cases) | `walkthrough.md` — stepped markdown (portable, renders on GitHub) |
| Google Cloud Shell | `tutorial.md` with teachme step markers + `cloudshell_tutorial` link |
| Browser lab | Killercoda `index.json` + `step1.md…` + `background.sh` |
| In-editor code tour | `.tours/demo.tour` (CodeTour JSON) |

Default to portable `walkthrough.md` unless the project clearly targets one of the others.

## walkthrough.md skeleton

```markdown
# <feature> — hands-on walkthrough

> You'll end with: <the showstopper>. ~<n> min. Prereqs: <tools>.

## Setup (once)
\`\`\`
git clone <repo> && cd <repo> && make demo-seed
\`\`\`
✅ **Check:** `make demo-status` prints `ready`.
❌ If you see `<common error>` → `<fix>`.

## Step 1 — <action>
\`\`\`
<one copyable command>
\`\`\`
✅ **Check:** you should see `<expected>`.
❌ If instead `<symptom>` → `<recovery>`.
➡️ **Next:** Step 2.

## Step 2 — <action>
<same shape>

## You did it
You built <result>. Reset anytime with `make demo-reset`. Next: <link>.
```

## Rules

- **One action per step.** Two commands in a step is two steps.
- **Every step has a ✅ check.** A copyable verification command beats prose ("run `curl …`, expect `200`").
- **Every step has a ❌ recovery.** Anticipate the common failure; this is what prevents silent stuck.
- **Commands are copy-paste exact.** No `<placeholders>` inside fenced commands unless the step explains how to fill them.
- **Reuse the DEMO.md beats** as the spine so live and interactive never drift.
- **End with reset + next.** The learner must be able to return to `s0` and know where to go.

## Innovation hooks (optional, if the project supports it)

- **`demo next` stepper** — a tiny runner target that prints the current step, waits, then advances (state in a dotfile). Wire into the detected runner, not a stray script.
- **Self-check target** — `make demo-verify STEP=2` runs the step's ✅ check programmatically.
- **Branch-per-step** — `git checkout step-2` jumps to a known-good state, so a stuck learner skips ahead without falling off the golden path.
