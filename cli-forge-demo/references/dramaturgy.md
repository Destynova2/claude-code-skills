# Dramaturgy — Narrative Frameworks per Intent

> **When to read:** Step 3 (forge the script). Pick the framework that matches the intent, then map your golden-path beats onto it.

## Universal opener: Do the Last Thing First

Whatever the intent, **open on the payoff** (Great Demo!'s "Do It"). Show the finished, working result — the dashboard populated, the secret rotated, the deploy green — *before* any setup. You earn attention by proving relevance in the first 30 seconds, then peel back the "how". A slow build-up loses the room.

The classic structure is therefore an **inverted pyramid**: payoff → how it works → (optionally) how to reproduce.

## By intent

### technique — "it works, here's how"
Framework: **Walking skeleton / vertical slice.**
1. **Showstopper** — the end-to-end result running (request → response, deploy → healthy).
2. **The path** — the 3-5 commands that produced it, the golden path only.
3. **The mechanism** — point at the one interesting internal (the trick, the architecture beat).
4. **Reproduce** — "clone, `make demo`, you get this." (ties to the kit itself)

Keep narration minimal; the terminal is the star. Caption the 2-3 lines that matter.

### fonctionnel — "the feature does the job"
Framework: **Problem → Solution → Result (PSR).**
1. **Problem** — the user pain / the acceptance criterion, in one sentence.
2. **Solution** — the feature, used exactly as a real user would.
3. **Result** — the outcome, measured against the criterion ("ticket closed in one click vs five screens").

No jargon, no config screens. Tie every beat to the agreed "definition of done".

### commercial — "this solves your pain"
Framework: **Great Demo! — Situation then Do-It.**
1. **Situation** (≤ 90 s) — *their* world: goal, current situation, pain, value desired, timeline. Earns the right to demo.
2. **Showstopper** — the single screen that resolves the headline pain. Do it first.
3. **One or two more pains** — each as its own short Do-It, matched to a pain they named.
4. **The vision** — where this takes them.

Villain/hero framing works (Jobs: existing tools are the villain; your product is the hero). **No feature tour.** Every click has a job. Remember the 76-second law — let them interrupt.

### pédagogique — "you can do it too"
Framework: **Guided steps with verification (teachme/Killercoda style).**
1. **Showstopper preview** — "by the end you'll have *this*."
2. **Stepped path** — each step: one action, one copyable command, one **verification** ("you should see X").
3. **Recovery** — each step has a "if you see Y instead, do Z".
4. **Recap + next** — what they built, where to go next.

Slow and forgiving. Optimise for the learner not getting stuck, not for speed.

## The 7-sentence story (Pixar rule #4) — optional spine for video/pitch

Useful when you need a tight narrated arc (commercial video, conference open):

1. Once there was *[user]*…
2. Every day they *[routine / status quo]*…
3. Until one day *[the pain / trigger]*…
4. Because of that *[escalation]*…
5. Because of that *[consequence]*…
6. Until finally *[your product / the demo moment]*…
7. And ever since *[the new better state]*.

## Rule of three

Three beats, three benefits, three key commands. Complex enough to feel substantial, simple enough to remember. If you have seven things to show, you have a Feature Tour — cut to three.

## Mapping checklist

- [ ] Beat 1 is the **payoff**, not setup
- [ ] The framework matches the **intent** (don't run a sales Situation on a dev audience)
- [ ] Every beat maps to a **pain or criterion**, never to "look, another feature"
- [ ] Total beats ≤ 3-5; anything more is cut or moved to "reproduce yourself"
- [ ] There is a clear **last line** (CTA / "now you try" / "ship it")
