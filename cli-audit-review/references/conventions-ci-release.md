# CI, Release, Packaging and Commit Conventions

> **When to read:** For `.gitlab-ci.yml`, templates, semantic-release, release scripts, package metadata, Galaxy, container build jobs, commit messages, branch rules, and CI variables.

---

## CI Is Production Behavior

Review CI/CD as code that deploys, releases, publishes, signs, tests, or gates production artifacts.

Check:

- workflow rules do not start useless pipelines or skip required ones;
- MR, default branch, tag, scheduled, and manual pipeline behavior are explicit;
- branch names and release rules match the repository workflow;
- artifacts are scoped, retained, and safe;
- generated credentials or tokens do not appear in logs;
- job names are understandable and not duplicated unnecessarily;
- matrix jobs are used instead of duplicate near-identical jobs;
- lints run on the files they claim to lint.

## CI Variables and Secrets

Custom environment variables should be namespaced with a project/component prefix unless they are standard CI variables.

For secrets:

- use masked or masked+hidden CI variables where supported;
- use protected variables when only protected branches/tags should access them;
- never echo secrets through shell tracing, command output, error output, or generated files;
- avoid embedding credentials in URLs when a safer credential helper/token mechanism exists;
- make token scope explicit and minimal;
- ensure variables used by release jobs are available only in the intended pipeline contexts.

Block if a token/password/key can leak or if a release job can run with the wrong credentials.

## Semantic Release and Commit Messages

Use conventional commits deliberately:

| Change | Preferred type |
|---|---|
| New user-visible behavior | `feat:` |
| User-visible bug fix | `fix:` |
| Pipeline-only change | `ci:` |
| Tests/scenarios only | `test:` |
| Documentation only | `docs:` |
| Maintenance, template sync, dependency bump | `chore:` |
| Internal restructuring without behavior change | `refactor:` |
| Formatting only | `style:` |
| Breaking compatibility or dropped support | `feat!:` or breaking-change footer |

Review comments should flag:

- WIP subjects such as temporary rebase/squash markers in final MR history;
- vague subjects like `fix: lint` when the actual change is a formatting/test/CI cleanup;
- missing `!` for removed platform support or compatibility breaks;
- commit body missing a short explanation when the fix is operationally subtle;
- release commits/version bumps as weak evidence for implementation conventions.

## Packaging and Galaxy-like Artifacts

Check:

- package metadata includes files needed for install/build/publish;
- runtime metadata and dependency files are not stale;
- dependency sources work in the intended environment, including offline/airgapped contexts;
- README and package metadata describe the same role/collection/component;
- build/publish jobs use the right tokens and branch/tag rules;
- generated docs or release notes do not publish internal-only details.

## Download and Dependency Sources

For CI tools and downloaded binaries:

- prefer maintained packages or pinned versions from trusted sources;
- avoid dead/unmaintained packages unless the MR documents why they remain acceptable;
- when direct internet is not available, make mirror/base URL variables explicit;
- consider transitive dependency compatibility with the project’s test environment;
- include checksum/signature verification where appropriate.

## Pipeline Matrix

When a change introduces a variant, the matrix should prove it:

- OS image/version,
- architecture/CPU model when relevant,
- container runtime,
- backend selection,
- HA vs single-node,
- airgap/offline vs online,
- feature flags,
- package source/mirror.

Do not duplicate jobs that a single `parallel.matrix` can express clearly.

## Release Scripts

Release hooks and success/failure scripts must be reviewed like deploy scripts:

- shellcheck/lint applies;
- tokens are not printed;
- branch/tag assumptions are explicit;
- generated files are deterministic;
- failure behavior is safe;
- scripts are named according to their semantic-release phase.

## Documentation and CI Sync

When a scenario, path, image, package, role, or job is renamed, update:

- README links and examples,
- Molecule paths,
- CI job names and matrix variables,
- lint exclusions,
- package metadata,
- release configuration,
- docs snippets and badges.

A rename that leaves old CI/docs paths behind is a methodology finding even if code compiles.
