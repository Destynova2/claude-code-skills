# Demo Anti-Patterns

> **When to read:** Step 3 (forge) and Step 6 (quality gate). Avoid these while generating; flag them if present in the input material.

## 12 Anti-Patterns

| Anti-Pattern | Detection | Fix |
|---|---|---|
| **Demo Gods** | Live run with no fallback — one timeout/typo and the demo dies | Always render an understudy (VHS gif / asciinema cast). Never debug live > 45 s; recover in character and cut to the recording |
| **Feature Tour** | Clicking through every menu/feature to prove you know the product | Show only the golden path. Run the "cut any beat" test: if removing a beat doesn't break the path, cut it. 3-5 beats max |
| **Cold Open** | The demo starts from leftover state from the last run | Run `reset` first, every time. The reset must be idempotent so back-to-back runs are clean |
| **The Monologue** | One uninterrupted segment > 76 s of talking/clicking | Segment into beats, add checkpoints, invite interaction. No deal-winning demo had >76 s of solid pitch (Gong) |
| **Yak Shaving** | Installing/configuring/`npm i`/login during the demo | Pre-install and pre-auth backstage. Hide setup (`Hide`/`Show` in VHS, behind-the-scenes in demo-magic). Nobody watches a package install |
| **Mystery Data** | Random/changing/timestamped data; "works on my machine" | Pin a fixed seed **and** clock (`SOURCE_DATE_EPOCH`). Keep demo data separate from app seed data so it never shifts under you |
| **No Exit** | No plan when Wi-Fi/cluster/API is down | Offline fallback: local mirror, recorded cast, second machine. Assume the venue network fails |
| **Slideware** | "Telling" the feature on slides instead of showing it run | Show the running thing in real context. Slides only frame the demo (sandwich), they never replace the beat |
| **Cursor Ballet** | Mouse zipping aimlessly; the audience can't follow the eye | Move deliberately, pause on the target, use keyboard + aliases. In recordings, hide idle cursor movement |
| **Login Fumble** | Time lost on logins, loading test data, env hiccups | Pre-seed and pre-auth. Every fumbled minute reads as "this product is clunky" — especially with 6 stakeholders on a 30-min call |
| **Director's Cut** | A 3-minute GIF / a tape so fast it's unreadable | Keep GIFs ≤ ~30-45 s, one idea. Add `Sleep` so viewers can read; loop with a clear start. Trim setup with `Hide` |
| **Silent Movie** | Video/GIF with no captions, color-only signals, tiny text | Ship WebVTT subtitles; caption key terminal lines; large font, high contrast. Accessibility is part of "done" |

## Red flags during generation

- A beat with **no expected output** → can't detect failure → add the expected output line
- A beat with **no recovery line** → Demo Gods risk → add "if this errors, say X, cut to understudy"
- The script reads fine **without anyone running anything** → Slideware → it's a doc, not a demo
- The data contains **today's date / a random id** → Mystery Data → pin seed + clock
- A `demo.sh` sits next to a `Makefile`/`justfile` → wrong runner → use the project's tooling
- The longest beat is **over ~76 s** → The Monologue → split it
- More than **5 beats** → Feature Tour → cut to the golden path

## The two non-negotiables

Every demo kit must pass these before delivery:

1. **It resets.** Run reset twice → identical `s0`. No Cold Open.
2. **It survives a failure.** Pull the network mid-demo → the understudy carries the story. No Demo Gods, No Exit.
