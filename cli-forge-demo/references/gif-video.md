# GIF & Video — VHS Tapes, Sizing, Captions

> **When to read:** Step 4 when support = gif or video. Preferred tool for terminal demos: **VHS** (charmbracelet). For GUI/web: screencast + WebVTT.

## VHS tape — the recording as code

A `.tape` is a sequence of instructions VHS replays to render a GIF/MP4/WebM. Because it's code, it's reproducible, reviewable in a PR, and can gate CI against a golden render.

**Requires:** `vhs`, `ttyd`, `ffmpeg` on PATH.

### Annotated template (`demo.tape`)

```tape
# Output & quality
Output docs/demos/<name>/demo.gif
# Output docs/demos/<name>/demo.mp4   # uncomment for video

Set Theme "Catppuccin Mocha"
Set FontSize 22          # legible from the back of the room / on mobile
Set Width 1200
Set Height 640
Set Padding 24
Set TypingSpeed 60ms     # human-paced, not instant
Set PlaybackSpeed 1.0

# --- Backstage setup: hide it (anti Yak-Shaving) ---
Hide
Type "make demo-reset && clear" Enter
Sleep 1s
Show

# --- Cold open: the showstopper first ---
Type "make demo" Enter
Sleep 3s                 # let viewers READ the payoff (anti Director's Cut)

# --- Beat 1 ---
Type "openbao kv get secret/app" Enter
Sleep 2s

# --- Beat 2 ---
Type "openbao kv rotate secret/app" Enter
Sleep 2s

Sleep 2s                 # hold final frame before loop
```

### Tape rules

- **`Hide`/`Show`** wrap all setup (reset, clear, auth). The viewer never sees backstage. (anti Yak-Shaving / Cold Open)
- **`Sleep` after each result** so the frame is readable. A GIF nobody can read is a Director's Cut.
- **FontSize ≥ 20**, width ≤ ~1200 for README/mobile legibility.
- **Total ≤ ~30–45 s**, one idea. If it's longer, it's a Feature Tour — split into multiple tapes.
- **Deterministic commands only** — same seed/clock, or the golden render drifts and CI flakes.
- **End on a held final frame** so the loop restart isn't jarring.

### Wire into the runner

```make
demo-gif:
	vhs docs/demos/<name>/demo.tape
```

### CI / golden render (optional)

VHS in CI re-renders the tape on every change; diff the output (or a frame hash) against the committed asset to catch unintended UX changes — the demo doubles as a UX regression test.

## asciinema alternative (lighter, selectable text)

```
asciinema rec docs/demos/<name>/demo.cast   # one clean run of `make demo`
agg docs/demos/<name>/demo.cast demo.gif     # → GIF
svg-term --in demo.cast --out demo.svg --window  # → SVG for README (tiny, text selectable)
```

Use when you want a featherweight, text-selectable README asset rather than a pixel GIF.

## Video + subtitles (GUI/web, accessibility)

VHS is terminal-only — for GUI/web demos use a screen recorder, then **always** ship captions:

- Emit a **WebVTT** `.vtt` track synced to the beats (reuse DEMO.md lines as caption text).
- Captions ≤ 2 lines, ~32 chars/line, on screen long enough to read.
- Never rely on color alone; ensure large, high-contrast text.
- Caption file lives beside the video: `docs/demos/<name>/demo.vtt`.

### Minimal WebVTT shape

```vtt
WEBVTT

00:00.000 --> 00:04.000
Here's the result: secrets rotated with one command.

00:04.000 --> 00:08.000
No restart, no downtime — the app picks up the new value live.
```

## Picking gif vs cast vs video — quick rule

Terminal demo → **VHS** (reproducible, CI-able). Need it featherweight + selectable in a README → **asciinema → svg-term**. GUI/web or spoken narration → **screencast + WebVTT**.
