# Privacy and Anonymization Rules

> **When to read:** Before creating or updating the skill, and before generating any report that may mention methodology origins.

---

## Non-Negotiable Rule

This skill must never disclose personal or private source information. It is a neutral methodology, not a biographical or corpus-extraction artifact.

## Never Include

- personal names;
- usernames or handles;
- e-mail addresses;
- private/internal URLs;
- organization names from the training data;
- repository/project names from the training data;
- commit hashes;
- issue/MR IDs from the training data;
- private labels/team names;
- raw excerpts from training comments;
- screenshots or copied terminal logs from training data;
- references like “the reviewer usually says...” or “in the corpus...”.

## Allowed

- generalized technical conventions;
- neutral examples created from scratch;
- public product/tool names such as Ansible, Molecule, GitLab CI, Go, PowerShell, Kubernetes, Podman, Terraform/OpenTofu;
- generic placeholder names like `project`, `component`, `apiBaseURL`, `PROJECT_PREFIX_`, `path/to/file.yml`;
- synthetic snippets that do not reproduce private identifiers.

## Report Privacy

When reviewing a user-provided repository, cite only paths, identifiers, and code from the target under review. Do not mention where this skill’s conventions came from.

## Pre-Release Scan for Skill Files

Before packaging the skill, scan generated files for:

```text
[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}
https?://
private organization names from the source corpus
known personal names/usernames from the source corpus
[0-9a-f]{7,40} commit-like hashes
```

A match is not automatically wrong when it is a generic code example, but inspect and remove anything that could identify a person, repository, organization, or private source.

## Wording Guidance

Prefer:

- “This methodology prioritizes...”
- “The review should check...”
- “Use this convention...”

Avoid:

- “The reviewer likes...”
- “The corpus shows...”
- “In the original MR...”
- “As X said...”
