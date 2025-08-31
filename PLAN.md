# PyEdgarAI Repository Reorganization Plan - Updated

**Date**: August 31, 2025  
**Scope**: Complete project reorganization and cleanup  
**Goal**: Clean, maintainable project structure following best practices

This document outlines the steps to refactor the `pyedgarai` repository.

## 1. Pre-computation Steps (Branch: `repo/reorg-inventory`)

These steps are performed on the `repo/reorg-inventory` branch and will be included in the first PR.

- [x] Create `AUDIT.md` with repository analysis.
- [x] Create `STRUCTURE.md` with the proposed file layout.
- [x] Create this `PLAN.md` file.
- [ ] Create `move_map.json` with the file move mappings.
- [ ] Create `scripts/reorg/move_files.py` to automate the file moves.
- [ ] Create `archive/` directory with `archive/README.md`.
- [ ] Update `.gitignore` to exclude `__pycache__/`, `geckodriver-*`, and other artifacts.
- [ ] Update `pyproject.toml` to exclude `/archive` from builds and tests.
- [ ] Open a pull request for review.

## 2. Execution Steps (Branch: `repo/reorg-execution`)

These steps will be performed after the initial PR is approved and merged.

1.  **Create and switch to the execution branch:**
    ```bash
    git checkout main
    git pull origin main
    git checkout -b repo/reorg-execution
    ```

2.  **Run the move script:**
    ```bash
    python scripts/reorg/move_files.py
    ```

3.  **Verify file moves and deletions:**
    - Manually check that files from `move_map.json` are in their new locations.
    - Ensure `geckodriver` directories are gone.

4.  **Update imports and file paths:**
    - Run `grep` or similar tools to find broken imports or file paths.
    - Manually fix any remaining broken paths in the code, especially in:
        - `notebooks/notebooks/tutorial.ipynb`
        - `scripts/*.py`
        - `src/pyedgarai/**/*.py`
        - `tests/test_pyedgarai.py`

5.  **Run linters and formatters:**
    ```bash
    # Example commands (adjust as needed)
    poetry run black .
    poetry run ruff . --fix
    ```

6.  **Run tests and build docs:**
    ```bash
    poetry install
    poetry run pytest
    cd docs
    make html
    cd ..
    ```

7.  **Commit changes:**
    - Commit file moves.
    - Commit import/path fixes.
    - Commit test and build fixes.

8.  **Open the second pull request for execution.**

## 3. Test Plan

- **Static Analysis:** Run linters (`black`, `ruff`) to catch syntax errors.
- **Unit Tests:** Execute the full `pytest` suite to ensure all existing tests pass.
- **Documentation Build:** Confirm that the Sphinx documentation builds without errors.
- **Notebook Execution:** Manually run through the `notebooks/notebooks/tutorial.ipynb` to ensure it executes from top to bottom without path-related errors.
