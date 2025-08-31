# Copilot: House Rules & Project Conventions

## Mission
- Keep the working set minimal, well-structured, and buildable.
- Never delete artifacts; archive instead.
- Changes must be reproducible and reviewable.

## Branch & PR Workflow
- Use feature branches: `repo/<short-task>` (e.g., `repo/reorg-inventory`, `repo/reorg-execution`).
- First PR: plan-only (AUDIT.md, STRUCTURE.md, PLAN.md, move_map.json, scripts).
- Second PR: execution (moves, import updates, build/test fixes).
- Small, focused commits with clear messages.

## Folder Layout (target)
/src # application/library code
/tests # tests
/scripts # one-off or maintenance scripts
/docs # documentation
/notebooks # notebooks (read-only in CI)
/data # sample or small test data (no secrets)
/configs # config files (lint, format, build, CI)
/archive # legacy/unused kept for reference


## Archival Policy
- Prefer archiving to deletion.
- Every file moved to `/archive/` needs a short reason in `/archive/README.md`.
- Exclude `/archive/` from builds, tests, packaging:
  - Python: `tool.pytest.ini_options`, `pyproject.toml`, `setup.cfg`
  - Node/TS: `tsconfig`, `jest`, `eslint`, `vite/webpack`, `package.json` exports
  - Others as applicable

## Coding Conventions
- Update imports/paths after moves.
- Run linters/formatters (black/ruff or eslint/prettier, etc.).
- Keep LICENSE headers intact.
- No hard-coded secrets or tokens; respect `.env` and `.gitignore`.
- If generating code, include docstrings/comments for non-trivial logic.

## Documentation Requirements
- Always produce/refresh: `AUDIT.md`, `STRUCTURE.md`, `PLAN.md`.
- For significant reorganizations, add an ADR: `docs/adr/NNN-repo-reorg.md`.

## Safety & Testing
- Ensure builds pass locally before proposing file moves.
- Add/update smoke tests if paths/modules change.
- Provide a rollback note in PR descriptions.

## Tools Copilot May Create/Use
- `scripts/reorg/move_files.(py|ps1|sh)` with `--dry-run` support.
- `move_map.json` mapping `old_path -> new_path`.
- Graph or inventory exports (e.g., `scripts/reorg/list_unused.py`).

## Things to Avoid
- Don’t remove files permanently unless explicitly instructed.
- Don’t change public APIs without calling it out in PLAN.md.
- Don’t modify license text or author attributions.

## Running code
- If you decide to run python code make sure the conda environment `pyedgarai` is activated.