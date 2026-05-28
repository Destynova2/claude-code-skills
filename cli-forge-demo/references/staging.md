# The Theatre — Full Model, 7 Laws, Pre-Flight

> **When to read:** Step 0 (framing) and Step 5 (pre-flight). This is the reasoning spine of the skill.

## Why theatre

A demo and a stage play share the same hard problem: **deliver an identical, compelling performance to a live audience, on cue, despite everything that can go wrong.** Theatre solved this centuries ago with scripts, blocking, rehearsal, stage reset, and understudies. We borrow the whole apparatus.

The metaphor also smuggles in the one technical idea that matters most — **determinism** — without any maths: *a good production is the same every night.* It is the same not by luck but because the show is scripted, the marks are taped to the floor, and the stage is reset between performances. A reproducible demo is exactly that.

## The 8 mappings

| Stage craft | In nature of theatre | In the demo kit |
|---|---|---|
| **Script & blocking** | Actors say fixed lines and stand on taped marks | `DEMO.md`: exact talk-track + exact commands. Zero improvisation on stage. |
| **Same show every night** | The play is identical performance to performance | Fixed **seed + clock + env**. The run is deterministic — reality is seeded like a PRNG. |
| **Reset the stage** | Crew returns props to start positions in the interval | `reset` is **idempotent** and fast: `reset ∘ reset = reset`. Run the demo back-to-back. |
| **Open with the showstopper** | The hook in the first minute keeps the house | Do-the-last-thing-first: the payoff before the setup. |
| **Hit your marks** | Step off your mark and you're out of the light | Golden path / vertical slice only. Deviation is where demos die. |
| **Pace the scenes** | No monologue outstays its welcome | No uninterrupted segment > ~76 s (Gong). Segment, checkpoint, interact. |
| **The understudy** | A trained stand-in when the lead can't perform | A pre-rendered backup (GIF / asciinema). Never debug live > 45 s. |
| **The matinée** | A repeat performance the public attends themselves | The self-guided interactive walkthrough. |

## The 7 Laws (each evidence-backed)

1. **Same show every night.** Pin state, data, **clock**, and environment. Non-deterministic data is the #1 silent demo killer. The full pin toolkit is shared: read `../../shared/determinism.md`. *(reproducible-environments / seed-data practice)*
2. **Reset the stage.** The reset is idempotent and fast enough to run between takes. *(live-coding: `git reset --hard && git clean -fdx`)*
3. **Open with the showstopper.** Front-load the payoff, then peel back how. *(Great Demo!, "Do the Last Thing First")*
4. **Hit your marks.** Demo the golden path / walking-skeleton vertical slice only. "Unpredictability eventually bites you." *(live-coding + sales-demo prep)*
5. **No scene over 76 seconds.** No deal-winning demo had >76 s of uninterrupted pitching. *(Gong.io)*
6. **Keep the understudy ready.** A backup recording + offline mode; never troubleshoot live beyond ~45 s — recover in character. *(live-coding failure handling)*
7. **Show, don't tell.** Show the running thing in real context; slides only support. *(Apple keynote "show don't tell")*

## Pre-flight checklist (always emit)

Borrowed from conference live-coding survival guides:

- [ ] **Reset run once** — confirm the stage is at `s0` before the audience arrives
- [ ] **Two dry-runs match** — same output twice = determinism proven
- [ ] **Notifications off** — no Slack/mail/calendar popups (separate demo user/profile if possible)
- [ ] **Terminal legible** — font size up, high-contrast theme, window sized for the room/recording
- [ ] **Aliases loaded** — long commands aliased to avoid typos under pressure (`alias k=kubectl`)
- [ ] **Network plan** — assume the venue Wi-Fi fails; offline fallback or local mirror ready
- [ ] **Understudy rendered & tested** — the backup GIF/cast actually plays
- [ ] **Tools pre-installed** — nobody watches a package install; no live `apt`/`npm i`
- [ ] **Backup machine / second screen** — for high-stakes demos
- [ ] **Timer visible to you** — to honour the 76-second law

## The "cut any beat" test (load-bearing check)

After writing `DEMO.md`, for every beat: *remove it mentally.* Does the golden path still reach the showstopper and make sense?
- **No** → the beat is load-bearing. Keep it.
- **Yes** → it's a Feature Tour detour. Cut it.

The finished script is the **minimum sequence of beats from cold-open to payoff** — nothing that merely proves you know the product.
