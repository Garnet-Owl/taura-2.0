# Migrate Poetry to uv Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the project's dependency and virtual environment management from Poetry to uv, aligning the repository with modern Python packaging standards (PEP 621) and the project's backend development guidelines.

**Architecture:** We will replace the Poetry configuration in `pyproject.toml` with standard PEP 621 metadata using Hatchling as the build backend. We will delete the `poetry.lock` file, generate a `uv.lock` lockfile, update all project documentation (`README.md`, `INSTALL.md`), transition the CI/CD workflow to use `setup-uv`, and update `AGENTS.md` to establish `uv` as the default runtime tool.

**Tech Stack:** Python 3.12, uv, Hatchling, Ruff, Pytest.

---

### Task 1: Update pyproject.toml and Migrate to PEP 621

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Replace Poetry sections in `pyproject.toml` with PEP 621 metadata**
  Edit `pyproject.toml` to delete `[tool.poetry]` and its sub-sections, replacing them with `[project]`, `[dependency-groups]`, `[tool.hatch]`, and `[build-system]` tables. Define all required runtime and development dependencies explicitly.

  Expected file content:
  ```toml
  [project]
  name = "taura"
  version = "2.0.0"
  description = "Machine translation model for translating Kikuyu to English"
  authors = [{ name = "James Wanjku", email = "james544wanjiku@gmail.com" }]
  requires-python = ">=3.12,<4"
  readme = "README.md"
  license = "MIT"
  dependencies = [
      "sacrebleu>=2.6.0",
      "fastapi>=0.110.0",
      "fasttext-wheel>=0.9.2",
      "numpy>=1.26.0",
      "pydantic>=2.0.0",
      "uvicorn>=0.28.0",
      "httpx>=0.27.0",
      "jinja2>=3.1.0",
      "tabulate>=0.9.0",
  ]
  classifiers = [
      "Programming Language :: Python :: 3",
      "Programming Language :: Python :: 3.12",
  ]

  [project.urls]
  Repository = "https://github.com/garnet-owl/taura-2.0"

  [dependency-groups]
  dev = [
      "pytest>=8.0.2,<9",
      "mypy>=1.8.0,<2",
      "pytest-cov>=4.1.0,<5",
      "pre-commit>=3.6.2,<4",
      "ruff==0.11.5",
      "givenpy>=1.0.5",
      "pyhamcrest>=2.1.0",
  ]
  docs = [
      "sphinx>=7.2.6,<8",
      "sphinx-rtd-theme>=2.0.0,<3",
  ]

  [tool.hatch.build.targets.wheel]
  packages = ["app"]

  [build-system]
  requires = ["hatchling"]
  build-backend = "hatchling.build"

  [tool.mypy]
  python_version = "3.12"
  warn_return_any = true
  warn_unused_configs = true
  disallow_untyped_defs = true
  disallow_incomplete_defs = true
  ignore_missing_imports = true
  exclude = ["app/tests/"]

  [tool.pytest.ini_options]
  testpaths = ["app/tests"]
  python_files = "test_*.py"
  python_functions = "test_*"
  python_classes = "Test*"
  ```

- [ ] **Step 2: Delete poetry.lock**
  Delete the obsolete lockfile:
  Run: `rm poetry.lock` (or `Remove-Item poetry.lock` in powershell)

- [ ] **Step 3: Generate the uv.lock lockfile**
  Run: `uv lock`
  Expected output: Lock file generated successfully.

- [ ] **Step 4: Sync the uv environment**
  Synchronize the local virtual environment and install all packages:
  Run: `uv sync`
  Expected output: Environment successfully synchronized, installing all dependencies.

- [ ] **Step 5: Run tests using uv to verify environment**
  Verify the test suite passes under uv:
  Run: `uv run pytest`
  Expected output: 22 passed.

- [ ] **Step 6: Run lint and type checking**
  Verify linting and Mypy:
  Run: `uv run ruff check .`
  Run: `uv run mypy app scripts`
  Expected output: Clean exit (no issues).

- [ ] **Step 7: Commit changes**
  Commit the files:
  ```bash
  git add pyproject.toml uv.lock
  git rm poetry.lock
  git commit -m "migrate: replace Poetry with uv and adopt PEP 621 metadata"
  ```

---

### Task 2: Migrate CI/CD pipeline to use uv

**Files:**
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Update `.github/workflows/ci.yml` to use `setup-uv`**
  Modify `.github/workflows/ci.yml` to replace the Snok Poetry setup and caching steps with the official `astral-sh/setup-uv` GitHub action, and update all run commands from `poetry run` to `uv run`.

  Target change in `.github/workflows/ci.yml`:
  ```yaml
  # Replace Snok Poetry installation with:
        - name: Install uv
          uses: astral-sh/setup-uv@v5
          with:
            enable-cache: true
            version: "latest"

  # Replace install dependencies step with:
        - name: Install dependencies
          run: |
            uv sync --all-groups

  # Update lint and test commands to use uv run:
        - name: Basic Lint with Ruff
          run: |
            uv run ruff check --select E,F --ignore E501,E741 --exclude "notebooks/*" .

        - name: Format check with Ruff
          run: |
            uv run ruff format --check --exclude "notebooks/*" .

        - name: Run tests with pytest
          run: |
            uv run pytest
  ```

- [ ] **Step 2: Commit workflow changes**
  Commit the CI workflow update:
  ```bash
  git add .github/workflows/ci.yml
  git commit -m "ci: migrate github actions workflow from Poetry to uv"
  ```

---

### Task 3: Update Project Documentation (README, INSTALL)

**Files:**
- Modify: `README.md`
- Modify: `INSTALL.md`

- [ ] **Step 1: Replace poetry command references in `README.md`**
  Search for `poetry run` in `README.md` and replace with `uv run`. Remove references to manual precompiled wheel installations on Windows since `uv` handles it natively.

  Target replacements:
  - `poetry install` -> `uv sync`
  - `poetry run python -m scripts.prepare_dataset` -> `uv run python -m scripts.prepare_dataset`
  - `poetry run python -m scripts.train_embeddings` -> `uv run python -m scripts.train_embeddings`
  - `poetry run uvicorn app.serve.main:app --reload` -> `uv run uvicorn app.serve.main:app --reload`
  - `poetry run pytest` -> `uv run pytest`

- [ ] **Step 2: Replace poetry setup references in `INSTALL.md`**
  Edit `INSTALL.md` to remove Poetry installation steps, replacing them with `uv` installation and environment setup instructions.

- [ ] **Step 3: Commit documentation updates**
  Commit the modified documentation files:
  ```bash
  git add README.md INSTALL.md
  git commit -m "docs: update install and run instructions to use uv"
  ```

---

### Task 4: Align AGENTS.md and Progress Tracking

**Files:**
- Modify: `AGENTS.md`
- Modify: `session-details/progress_update_2026-06-21.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update package manager rules in `AGENTS.md`**
  Modify references to Poetry in `AGENTS.md` to `uv`.
  - Replace `Stack: Python 3.12, Poetry, FastAPI, FastText.` with `Stack: Python 3.12, uv, FastAPI, FastText.`
  - Replace `Use poetry run or poetry shell for all Python commands.` with `Use uv run for all Python commands.`
  - Replace `Dependency management: Use poetry add / poetry remove. Do not use pip install.` with `Dependency management: Use uv add / uv remove. Do not use pip install.`

- [ ] **Step 2: Update the latest progress update file**
  Add a new section for Phase 3 (Poetry to uv migration) in `session-details/progress_update_2026-06-21.md` and mark the tasks completed.

- [ ] **Step 3: Update `CHANGELOG.md`**
  Append 3-5 bullet points under `[Unreleased]` for the migration tasks completed in this session.

- [ ] **Step 4: Commit changes**
  Commit `AGENTS.md` and `CHANGELOG.md`:
  ```bash
  git add AGENTS.md CHANGELOG.md
  git commit -m "chore: align developer guidelines and changelog with uv migration"
  ```
