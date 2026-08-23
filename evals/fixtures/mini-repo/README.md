# mini-widget

FIXTURE: input for the cli-cycle evaluation in evals/cases/. Unlike the other
fixtures, this one is not flawed. Its value is what it lacks: no CI config, no
Dockerfile, no SQL or migrations, no shell scripts, no CONTRACTS.md and no
tests directory. It exists to check that the orchestrator skips the skills that
do not apply instead of fanning out to all of them.

Do not add any of those artifacts: the evaluation depends on their absence.

A tiny Rust crate with two functions.
