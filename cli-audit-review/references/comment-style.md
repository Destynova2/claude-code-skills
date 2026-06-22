# Review Comment Style

> **When to read:** Before writing final review reports, MR comments, or line-level suggestions.

---

## Tone

Use a direct, concrete, professional tone. In French contexts, concise French comments are preferred. Review the change, not the author.

Do:

- lead with concrete risk or convention;
- cite `file:line`;
- explain consequence when the issue is not obvious;
- propose the smallest correction;
- name the proof expected;
- separate blockers from nice-to-haves;
- label non-blocking comments explicitly;
- mark uncertainty as a question;
- include good practices found.

Do not:

- mention personal identities, corpus origin, private URLs, internal projects, commit hashes, or raw training examples;
- imitate a person’s identity or private speech habits;
- over-focus on formatting when contract, idempotence, proof, or security is broken;
- approve deployable behavior when proof is missing;
- ask for broad rewrites without identifying the risk closure.

## Comment Length by Severity

| Severity | Style |
|---|---|
| Blocker/Critical | Structured comment: risk, consequence, fix, proof. |
| Major | 2-5 sentences or bullets; include proof expected. |
| Minor | One concise line when the fix is obvious. |
| Info/Question | Short question plus why it matters. |

## Intent Labels

Use labels to prevent ambiguity:

| Label | Meaning |
|---|---|
| `Blocker:` | Must be fixed before merge. |
| `Major:` | Should be fixed before merge unless explicit risk is accepted. |
| `Minor:` | Low-risk improvement. |
| `Nit:` | Polish; never blocks merge by itself. |
| `Optional:` | Suggestion only. |
| `Question:` | Clarification needed before deciding severity. |
| `Non-blocking:` | Safe to merge with this left unresolved. |

When using GitLab-style conventional comments, keep the same semantics. Do not mix mandatory and optional requests in the same paragraph.

## Full Finding Shape

```markdown
### [Severity] R# — Short title
- **File**: `path/to/file.yml:42`
- **Risk**: Concrete deployable/security/correctness risk.
- **Why it matters**: Consequence for operator, CI, release, idempotence, platform, rollback, or maintenance.
- **Fix**: Smallest correction that closes the risk.
- **Proof expected**: Molecule/CI/test/assertion/doc update that would prove it.
- **Confidence**: High/Medium/Low.
- **Disproof**: What evidence would invalidate the finding, when relevant.
```

## Compact Line Comment Shapes

Use these as synthetic patterns, adapted to the target code. Do not claim they came from a corpus.

### Missing FQCN

```markdown
FQCN à utiliser ici (`ansible.builtin.<filter_or_module>`). À généraliser au reste du fichier si le même pattern revient.
```

### Missing assertion

```markdown
Il manque l'assertion associée à ce nouveau default : type, non-vacuité et valeurs autorisées avant les tasks de setup.
```

### Desired state vs action

```markdown
Côté Ansible, ça ressemble plus à une action qu'à un état désiré. Est-ce qu'on peut dériver ce comportement depuis la configuration cible plutôt que via un flag dédié ?
```

### PowerShell from Ansible

```markdown
Pas d'interpolation Jinja directement dans le PowerShell : passe par `Param()` et `parameters` pour éviter les surprises de quoting/escaping.
```

### CI variable secret handling

```markdown
Cette variable ressemble à un secret : elle devrait être masked/hidden, éventuellement protected, et ne jamais apparaître dans les logs ou artifacts.
```

### Commit hygiene

```markdown
Le type de commit ne correspond pas au comportement livré : ici c'est plutôt `test:`/`ci:`/`chore:` que `fix:`.
```

### Style-only

```markdown
Saut de ligne manquant en fin de fichier.
```

## Question Style

Ask questions when domain naming or intent is unclear, but include the consequence:

```markdown
Est-ce que ce nom représente bien le périmètre fonctionnel, et pas seulement l'équipe qui le maintient ? Sinon il risque de devenir ambigu dans les filtres et dashboards.
```

```markdown
Pourquoi cette tâche doit-elle être exécutée avant les assertions ? Si elle peut modifier l'état de la machine, il faut valider la configuration avant.
```

## “À généraliser” Rule

When the same convention issue appears repeatedly:

1. leave one precise comment on the first clear occurrence;
2. say it should be generalized to the rest of the file/pattern;
3. do not duplicate ten identical comments unless the review tool benefits from one thread per line.

## Suggested Fixes

When the fix is exact and short, provide a ready-to-paste suggestion or patch snippet. This is most useful for syntax, assertions, small guard clauses, CI conditions, and documentation wording. Avoid suggestion blocks for broad design choices; state the acceptance condition instead.

## Good Practices Section

Always include at least one positive observation when the target has any meaningful good practice:

- contract propagated correctly;
- assertions are early and precise;
- Molecule/CI proves the changed variant;
- secrets are contained;
- commit type matches release behavior;
- docs and examples moved with the code;
- implementation follows ecosystem idioms.

## Bad Comment Patterns

Avoid:

- “Improve this.” — no risk or fix.
- “Use a better name.” — too vague unless the name hides behavior.
- “Add tests.” — specify which behavior/scenario must be proven.
- “Refactor this file.” — identify the unsafe coupling or missing contract.
- “Looks good” — avoid when proof/docs/CI are missing.

## Ordering

Order findings by risk:

1. secrets/security;
2. broken deploy/correctness/data loss;
3. validation/fail-fast;
4. idempotence/state convergence;
5. missing proof;
6. OS/topology/airgap/runtime variants;
7. CI/release/packaging;
8. documentation/operator clarity;
9. language idioms;
10. style/formatting.
