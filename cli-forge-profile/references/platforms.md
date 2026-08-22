# Platform Rules

## Contents

- LinkedIn
- CV / Resume
- Reddit / Community Profile
- GitHub Profile / Portfolio
- Portfolio Case Study
- Freelance Service Profile
- Recommendation Request
- Cover Letter / Speaker Bio

---

Use these rules when writing or auditing profile content for a specific surface.

## LinkedIn

### Structure

- Headline: role + target niche + proof domain + core technologies.
- About: first 2-3 lines must stand alone before "see more".
- Experience: 2-4 high-signal bullets per recent role; shorter for older roles.
- Skills: prefer searchable labels LinkedIn suggests over niche phrasing; attach skills to the jobs, projects, credentials, or education where they were used.
- Featured: link to proof artifacts: company site, flagship repo, talk, CV PDF, demo.

### Limits

- Headline: keep under 220 characters.
- About: keep under 2600 characters.
- Skills: LinkedIn allows up to 100 skills; choose only skills that support the target role and can be connected to experience, projects, credentials, education, or proof.
- Top 3 pinned skills should match the mission target, not personal preference.
- Platform limits and labels change; verify in the LinkedIn UI before final publication.

### Copy Pattern

Use this as a diagnostic scaffold, not a sentence to paste everywhere.

```markdown
I help [target reader/company] solve [expensive problem] with [credible mechanism].

[Role], [years/scope] in [trusted environments]. I specialize in [3 pillars].

Results:
- [metric/outcome]
- [metric/outcome]
- [proof artifact]

Available for [mission types]. Contact: [email/site].
```

### SEO

Repeat strategic labels naturally in headline, About, experience, and skills.
Avoid keyword dumping; one clear occurrence in the right field beats five awkward ones.

### Proof Signals

LinkedIn has shifted away from standalone skill tests and toward examples of applied skills on profiles. Prefer:
- skills mapped to experience/project/education;
- Featured proof links;
- endorsements for the top 3 skills;
- verified or connected-app proof only when available and relevant in the user's UI.

## CV / Resume

### Structure

- Header: name, title, location, contact, LinkedIn, GitHub/portfolio.
- Profile: 3-5 lines maximum.
- Target missions or role fit: optional but useful for freelance profiles.
- Key achievements: 4-6 proof bullets.
- Skills: grouped by capability, not alphabet soup.
- Experience: recent high-signal roles first; older roles compressed.
- Open source/talks: include only if they strengthen the target role.

### ATS Rules

- Use standard section names when possible.
- Avoid complex tables, icons, and low-contrast formatting.
- Keep role titles recognizable.
- Extract 8-12 keywords from the target job or mission and place them naturally in the profile, skills, and relevant experience bullets.
- Put technologies near the roles where they were used.
- Keep dates and employers easy to parse.
- Tailor the CV to the role; keep a master CV separately and publish only the role-fit version.
- Write for fast human and machine scanning: active verbs, measurable outcomes, and role keywords.

### Bullet Formula

```text
Verb + scope + mechanism + result + constraint/proof.
```

Examples:
- Reduced offline deployment from 1 week to under 1 hour through reproducible packaging and runbooks.
- Built Terraform/OpenTofu foundations for 100+ application environments with CI/CD validation and vulnerability gates.

For CVs, avoid first-person narrative. For LinkedIn, first person is acceptable if it increases clarity and approachability.

For freelance or consulting careers with many short missions, group missions under the freelance entity when accurate, then use sub-bullets per mission. This preserves evidence without making the CV look like accidental job hopping.

## Reddit / Community Profile

Reddit profiles and posts should earn trust before promoting anything.

- Lead with a concrete use case, incident, result, or lesson learned.
- Avoid corporate slogans and "we built X" launch-post tone.
- Disclose affiliation when linking your own work.
- Prefer "here is the problem and what worked" over "try my tool".
- Keep profile bios human and narrow: who you are, what you build, what you discuss.
- Avoid repeated, unsolicited, or mass-posted promotional content; check community rules before posting links to your own work.
- Do not ask for votes, imply vote requests, sensationalize titles, or use all-caps titles.

### Reddit Bio Pattern

```markdown
DevSecOps / platform engineer working on regulated infra, air-gapped Kubernetes, and LLM traffic control.
Building [project] to solve [specific pain].
I mostly post about [topics].
```

## GitHub Profile / Portfolio

- Start with what you build, not a list of tools.
- Use a username-matching public repository with a root `README.md` for the profile README.
- Pin up to six repositories/gists that support the same narrative; do not pin empty skeletons, abandoned demos, or private-work placeholders that imply delivered public proof.
- Add one-line repository descriptions with outcome and audience.
- Keep badges minimal and meaningful.
- Link CV/LinkedIn/site only after proof projects are visible.

### GitHub Profile Pattern

```markdown
[Role / builder statement] for [audience/problem].

Proof projects:
- [repo]: [problem solved] for [audience], [maintenance status], [proof artifact]
- [repo]: [problem solved] for [audience], [maintenance status], [proof artifact]

Current focus: [narrow technical direction].
Contact / portfolio: [link]
```

## Portfolio Case Study

Use case studies when the user needs proof beyond a short profile.

```markdown
## [Project / mission]

Audience / problem: [who had the pain]
Constraints: [time, compliance, security, scale, team, budget]
Contribution: [what the candidate personally did]
Approach: [mechanisms, not buzzwords]
Outcome: [metric, artifact, adoption, audit, delivery]
Proof: [repo, demo, talk, screenshot, testimonial if approved]
Confidentiality: [what is anonymized or omitted]
```

## Freelance Service Profile

Use offer language, not employment language.

```markdown
I help [buyer] achieve [business outcome] through [technical service].

Best fit:
- [situation 1]
- [situation 2]
- [situation 3]

Typical deliverables:
- [audit/architecture/implementation/runbook/training]
```

Make the buyer's risk visible: data leakage, audit failure, downtime, cloud dependency, slow delivery, blocked deployment, failed compliance evidence.

Vary the opening proof by platform. A LinkedIn headline, freelance platform intro, GitHub profile, and portfolio page should not all reuse the same "I help..." sentence.

## Recommendation Request

Use this for LinkedIn recommendations or testimonial requests.

```markdown
Bonjour [Name],

Je mets a jour mon profil pour [target role/mission]. Si tu es d'accord, une courte recommandation sur [specific shared work] m'aiderait beaucoup.

Les points utiles a mentionner seraient [capability 1], [capability 2], or [capability 3], uniquement si cela correspond a ton experience directe.

Aucune obligation bien sur; je peux aussi te proposer un court brouillon factuel a corriger.
```

Never invent testimonials. Ask permission before naming a client, project, or confidential context.

## Cover Letter / Speaker Bio

- Cover letters: connect one target problem, two proof points, and one reason for fit; avoid repeating the CV.
- Speaker bios: one-line credibility, current work, relevant proof, and topic fit; keep the public audience in mind.
