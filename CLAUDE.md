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
- **Train on all data, every time (owner rule, 2026-11-01).** Every model (FastText + Procrustes, Marian/NLLB fine-tunes, any future method) is trained from scratch on the whole current corpus: all old books plus every new book, never only the new data and never by continuing from the previous model on new data alone. Rebuild the splits with `scripts.prepare_dataset` first, so the train split contains every book. Validation (10%) is for comparing runs; test (10%) is for final comparisons only. For a release/published model, do one final pass trained on train + validation + test together, and report its scores as the quality reference of the matching held-out run, not as new scores.
- **Refresh the public models regularly (owner rule, 2026-11-01).** After every 4 new books (or a comparable amount of new data pairs), retrain and evaluate on the held-out split, then do the full train+val+test pass (for public release only) and replace the outdated published FastText and neural (Marian) models on Hugging Face with the new ones. Report CPU latency and size with them, and record in README that the published models were refreshed and which corpus they cover.
- Ensure reproducibility: set seeds where applicable.
- Document preprocessing steps clearly.
- FastText models should be trained with clear versioning and metric tracking.

### README
- **Keep the README short and ordered** (intro, screenshot, what's inside, performance, quick start, API, tests, contributing, license). No long per-run commentary there.
- **The README Performance table holds only the latest 3 evaluated metric rows** (drop the oldest when adding one). Full history lives in `CHANGELOG.md` and git history.
- **Refresh the README UI screenshot** (`data/assets/taura-iu-screenshot.png`) whenever the web UI changes.

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
- **CRITICAL:** Never commit temporary scratch scripts or scratch data files to git. Keep the git history clean.
- 1 commit per completed feature (or work session, if continuing).
- Commit message: short imperative sentence. No AI attribution.

---

## Progress Tracking

- After every change: append 1–2 concise bullets to `CHANGELOG.md`. Write for a normal user: what changed and why it matters. Never overwrite — always append.
- Do **not** duplicate every change in `session-details/progress_update_<date>.md`.
- Progress updates are milestone snapshots: update them only when a milestone status, phase status, metric, blocker, or next milestone focus changes.
- Fine-grained implementation details belong in the latest handoff, not the changelog.

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
- **CRITICAL:** Missing verses are unacceptable without strict investigation! If a verse is missing, it implies that the matching of the other verses might be misaligned. Always verify PDF integrity.

---

## Owner Authorisations (added 2026-10-18)

- **Free to choose the method.** Agents may try any technique that improves translation accuracy beyond FastText + Procrustes (for example fine-tuning a pretrained multilingual model, LoRA, back-translation), provided results are recorded honestly in README's Performance Progression table and compared against the previous run.
- **Free to grow the corpus.** Agents may find, verify and add more Kikuyu-English parallel or monolingual data from public sources whose licence allows open-source use. Record the source, licence and cleaning rules, and never add data the project cannot legally redistribute. Verify alignment (no missing or empty pairs) before committing.
- **Free GPU providers allowed.** If credentials exist in the environment, agents may train on a free provider (Kaggle preferred; Lightning AI or Modal are alternatives), using all data including newly extracted books. Never read or print credential values; check only that the variable is set (`[ -n "$KAGGLE_KEY" ]`). Large models and datasets go to Hugging Face or the provider, never git. This lifts the "no GPU work while Milestone 3 is open" limit for experiments that leave the existing FastText pipeline unchanged.

### How the owner provides Kaggle credentials (free GPU)

1. Create a free account at https://www.kaggle.com and verify your phone number (required for GPU and internet access).
2. Open https://www.kaggle.com/settings, find the **API** section and click **Create New Token**. It downloads `kaggle.json` with your `username` and `key`. If the page shows a single token string instead, copy that.
3. In Claude Code on the web, edit the environment this routine uses and add environment variables `KAGGLE_USERNAME` (the username) and `KAGGLE_KEY` (the key), or `KAGGLE_API_TOKEN` for the single-string token.
4. In the same environment, allow network access to `kaggle.com` and `www.kaggle.com` (custom or full access, or add them to the allowlist).
5. Never paste the key into chat, git or any repo file. If it leaks, rotate it from the Kaggle settings page.
6. Agents then use `uv add kaggle` and `kaggle kernels push/status/output` to run GPU notebooks and fetch results.

### Kaggle status (updated 2026-10-18)

- The owner has added `KAGGLE_API_TOKEN` to the cloud environment. Only check that it is set (`[ -n "$KAGGLE_API_TOKEN" ]`); never print it. If it is unset, the session predates the change, so record that in the handoff and carry on without GPU.
- Use it through the Kaggle client (`uv add kaggle`, then `uv run kaggle kernels push/status/output`). The client reads `KAGGLE_API_TOKEN` automatically; no `kaggle.json` is needed.
- No standing script is kept in the repo. Write a short throwaway script in the scratchpad for each GPU job and never commit it. Only commit reusable training code that the project itself needs, and keep tokens out of notebooks and logs.

### GPU and compute hygiene (added 2026-10-18)

- **Before starting a GPU job, make sure the GPU is free.** Run `uv run --with kaggle kaggle kernels status <kernel>` for every Taura kernel named in the latest handoff, and do not push a new kernel while another Taura kernel is `RUNNING` or `QUEUED`. The Kaggle CLI has no stop command, so a stale run can only be cancelled from the kernel's page on kaggle.com (cancel the running version); if one is still running from an earlier session and its results are not needed, record it in the handoff for the owner and wait for it or the 12-hour limit rather than starting a second job.
- **Retraining and training happen on the Kaggle GPU only (owner rule, 2026-10-31).** Never run `scripts.train_embeddings` or any other training or retraining on the cloud container's CPU, even though older handoffs gave container timings. Evaluating or serving an already-trained model on CPU is fine. Check at the start and end of every run that nothing is training or serving: `pgrep -af "train_embeddings|uvicorn"`, and stop leftovers. Do not record a score from a container-trained model.
- **Every GPU job must end on its own.** Kernels run as batch scripts that exit when training and evaluation finish: no interactive sessions, no idle waits, and a fixed number of epochs so GPU hours are not wasted. Download the outputs as soon as the kernel finishes.
- **After every run, stop local work too.** When a session ends, no training or conversion process may be left running in the container; check with `pgrep -f train_embeddings` and similar, and stop leftovers before wrap-up.
- Lessons so far: full NLLB-600M fine-tuning with AdamW runs out of memory on a 16 GB T4; use Adafactor plus gradient checkpointing. In a status loop, match the status text (`grep -q "RUNNING\|QUEUED"`), not `grep -v`, because uv prints warning lines.
- **Keep public.** The GitHub repository and every Hugging Face repo for Kikuyu-English translation (models and datasets) must stay public. Never make them private.
