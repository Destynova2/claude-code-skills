# Shared — Project Reconnaissance

> **Cross-skill reference.** Canonical "read the project first" step for the presentation family: `cli-forge-readme`, `cli-forge-prez`, `cli-forge-demo`. Reference it as `../../shared/recon.md`. The goal is one shared mental model so the README, the slides, and the live demo tell the *same* story.

## What to extract (in order)

| # | Question | Where to look |
|---|---|---|
| 1 | **What does it do?** One sentence, no jargon. | README hero, package description, main entrypoint |
| 2 | **Who is it for?** The actual user/persona. | README, docs audience, issue templates |
| 3 | **What problem does it solve?** The pain before the tool. | README "why", motivation docs, commit history |
| 4 | **What's the headline capability?** The single most impressive thing it does end-to-end. | the main command / the demo-worthy feature |
| 5 | **What makes it different?** The one non-obvious strength. | comparisons, design docs, distinctive deps |
| 6 | **What's the golden path?** The happy-path sequence a real user runs. | quickstart, tests, examples/ |

## The headline capability = the showstopper

Items 4 and 6 are the spine of any presentation artifact:
- **README** opens its quickstart with it.
- **prez** opens on it (the hook).
- **demo** does it *first* (cold-open showstopper).

If you can't name the headline capability in one sentence, you haven't finished recon — keep reading the project, don't start generating.

## Recon discipline

- **Read before writing.** Build the model from the code/docs, not from assumptions.
- **One story, three fidelities.** README (written) · prez (slides) · demo (live, moving). They must not contradict each other.
- **Concrete over abstract.** Capture the specific real example first; generalize later.
- **Note what's out of scope.** The features you're *not* leading with — so they don't leak into the hook.

## Output of recon (hand to the generating skill)

A 6-line brief: what / who / problem / headline / differentiator / golden-path. Every downstream presentation skill consumes this same brief.
