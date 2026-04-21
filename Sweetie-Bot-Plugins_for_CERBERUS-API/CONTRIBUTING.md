# Contributing

## Philosophy
This repository starts as an architecture and planning scaffold, but it is now organized to be publishable on GitHub with a sane default contributor workflow.
Contributions should improve clarity, structure, contracts, or carefully isolated implementation stubs.

## Contribution priorities
1. documentation quality
2. interface contracts
3. placeholder code structure
4. tests for schemas and loaders
5. tooling that helps inventory or package assets
6. GitHub hygiene, automation, and contributor experience

## Ground rules
- preserve mergeability
- avoid rewriting the runtime core in-place
- keep character content in assets when practical
- document assumptions
- prefer additive change over invasive refactors in this stage
- treat motion, proximity, and public-demo concerns as safety-sensitive work

## Local setup
```bash
python -m pip install -e .[dev]
pre-commit install
```

## Suggested workflow
1. create a focused branch
2. make one bounded change
3. run `ruff check .` and `pytest`
4. update docs or contracts if behavior changed
5. open a pull request using the provided template

## Commit style
Suggested prefixes:
- docs:
- feat:
- fix:
- chore:
- test:
- refactor:
- ci:

## Pull request checklist
- [ ] documents updated
- [ ] contracts updated if interfaces changed
- [ ] tests added or updated where appropriate
- [ ] no hidden safety regressions introduced
- [ ] no secrets or private tokens added

## Issue tracking
Use the issue forms in `.github/ISSUE_TEMPLATE/` whenever possible.
Use Discussions for broader architecture or roadmap conversation.
