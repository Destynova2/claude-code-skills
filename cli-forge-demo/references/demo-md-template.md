# DEMO.md Template

> **When to read:** Step 3. This is the skeleton for the staged script. Fill every placeholder; delete sections that don't apply to the chosen support. Output in the project's language.

---

```markdown
# Demo — <feature / project>

- **Intent:** technique | fonctionnel | commercial | pédagogique
- **Support:** live | gif | cast | video | interactive
- **Audience:** <who>
- **Duration:** <n> min  ·  **Showstopper at:** 0:00
- **Reset:** `make demo-reset` (or detected runner target)
- **Understudy:** `docs/demos/<name>/demo.gif` (rendered, tested)

## Pre-flight  (run T-5 min)

- [ ] `make demo-reset` → confirm s0
- [ ] two dry-runs produce identical output
- [ ] notifications off · font size up · aliases loaded
- [ ] network plan / offline fallback ready
- [ ] understudy plays

## Cold open — the showstopper  (0:00–0:30)

> **Do the last thing first.** Open on the finished result.

- **Mark (command):**
  ```
  <the command that shows the payoff>
  ```
- **Expected output:**
  ```
  <what the audience must see — used to detect failure>
  ```
- **Line (say):** "<one sentence: what they're looking at and why it matters>"
- **Recovery:** if this errors → "<say this>", cut to understudy at <timestamp>.

## Beat 1 — <name>  (0:30–…)

- **Mark:** `<exact command>`
- **Expected:** `<expected output>`
- **Line:** "<talk-track>"
- **Budget:** ≤ 76 s
- **Recovery:** "<fallback line>"

## Beat 2 — <name>

<same shape>

## Beat 3 — <name>

<same shape>

## Close  (last 30 s)

- **Line:** "<CTA / 'now you try' / 'ship it'>"
- For technique/pédagogique: "Reproduce it: `git clone … && make demo`."

## Reset

```
make demo-reset    # idempotent; lands on s0
```

## Fallback

If anything breaks beyond ~45 s, switch to the understudy:
`docs/demos/<name>/demo.gif` — and narrate over it.
```

---

## Authoring rules

- **Marks are exact.** Paste the real command, not a paraphrase. Alias long ones.
- **Expected output is mandatory.** It's how you (and CI) know the beat passed.
- **Lines are short.** One or two sentences. The terminal is the star.
- **Every beat has a recovery line.** No exceptions — that's the anti-Demo-Gods guarantee.
- **Budgets sum to the stated duration.** If they don't, cut beats (Feature Tour).
- **The cold open is the payoff**, never setup or `cd`/`clone`.
