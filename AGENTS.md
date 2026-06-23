# Taura 2.0 — Agent Instructions

**Project:** Taura 2.0 — Machine translation model for translating between Kikuyu and English.
**Stack:** Python 3.12, uv, FastAPI, FastText.
**Role:** Senior AI / Machine Learning Engineer & Backend Developer.

This file is read by any AI coding agent working on this project. It is the authoritative source for standing rules, code standards, and design philosophy.
Current milestone state is in `session-details/progress_update_<date>.md` and the exact resumption point is in the latest handoff under `session-details/handoffs/`.

---

## Session Startup — Always in This Order

> The root `MASTER_PLAN.md` is the milestone roadmap. `session-details/` holds progress snapshots and handoffs.

1. Read the root `MASTER_PLAN.md` for milestone context and current priorities.
2. List `session-details/handoffs/`, sort by filename, read only the most recent. This is your exact resumption point.
3. Read `CHANGELOG.md` — know what was last changed.
4. Read the **most recent dated progress file** — `ls session-details/progress_update_*.md | sort | tail -1`. Check milestone status, current phase, next work, and blockers.
5. Begin from the latest handoff's next task if it is consistent with the current milestone; otherwise follow the first unblocked milestone-phase item in the progress update.

---

## Priority Order

1. **Milestone work in order.** Work through the current milestone phase one item at a time.
2. **Model evaluation & testing.** Ensure model metrics and test suites pass before marking a feature as complete.
3. **API Contracts.** Any changes to translation functionality must be correctly exposed via the FastAPI endpoints.

---

## Security & Environment Constraints

- Never read or access `.env` files. If an environment variable is needed, ask the user.
- Never commit large datasets or models directly to git (respect LFS limits).
- Use `uv run` for all Python commands.

---

## Work Rules

- Make no unrequested changes. Scope = the single item being implemented or verified.
- Do not refactor and add functionality at the same time (Two Hats rule).
- Contributions are open-source. Write clean, readable code to help the community.
- Ensure all tests pass.
- **Autonomous Progress:** Proceed without asking for direction on every turn. Avoid asking trivial or excessive user questions.
- **Goals & Datasets:** The ultimate objective is to achieve high translation accuracy. If needed, online datasets can be curated from scratch.
- **UI Balance:** Build a nice but simple Web UI, then return immediately to model/evaluation performance.


---

## Code Quality Standards

### Python
- Dependency management: Use `uv add` / `uv remove`. Do not use `pip install`.
- Code Formatting & Linting: Use `ruff`. Run `uv run ruff check` and `uv run ruff format`.
- Strict typing: Use Python type hints extensively.
- `model_dump()` instead of `dict()` for Pydantic models.
- Single-purpose functions, ~25 lines, ~4 parameters max.
- Explicit imports for local modules.
- PEP 8 at all times.
- Always run Python in module mode: `python -m package.module`.

### Machine Learning & Data Preprocessing
- Ensure reproducibility: set seeds where applicable.
- Document preprocessing steps clearly.
- FastText models should be trained with clear versioning and metric tracking.

---

## Testing Rules

- **TDD:** Write tests for new API endpoints or preprocessing steps before implementation.
- **Style:** Use the `Given`, `When`, `Then` pattern with `givenpy` and `hamcrest`. Tests should be structured with context managers: `with given(...)`, `with when(...)`, `with then(...)`. Assertions should use `assert_that`.
- Use `pytest` for the test suite in `app/tests/`.
- Run only affected tests during development. Run the full suite once before committing.

---

## Git Rules

- Commit locally only. Never push to remote.
- **Critical:** The agent must commit the changes it makes at the end of *every* agent session.
- **CRITICAL:** ALWAYS run the test suite FIRST before executing any `git commit`. Never commit untested code.
- 1 commit per completed feature (or work session, if continuing).
- Commit message: short imperative sentence. No AI attribution.

---

## Progress Tracking

- After every code change: append 3–5 bullets to `CHANGELOG.md`. Never overwrite — always append.
- Do **not** duplicate every change in `session-details/progress_update_<date>.md`.
- Progress updates are milestone snapshots: update them only when a milestone status, phase status, metric, blocker, or next milestone focus changes.
- Fine-grained implementation details belong in `CHANGELOG.md` and the latest handoff.

---

## Session Wrap-Up — Required Every Session

Write a handoff to `session-details/handoffs/YYYY-MM-DD_HHMM_handoff.md`:

```markdown
## Status
[Milestone + what was completed this session]

## Last Files Changed
[Files modified/created — one-line description each]

## Next Task
[Exact next step — specific enough for a cold-start agent, no guessing]

## Blockers
[Anything requiring user input, credentials, or external action]
```

Delete all but the 3 most recent handoff files after writing.
