# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
- Initialized `CHANGELOG.md` and `session-details/progress_update_2026-06-20.md`.
- Completed directory scaffolding for `app/serve` and `models`.
- Added `CONTRIBUTING.md` and verified CI pipeline presence.
- Implemented robust tokenization and text normalization scripts (`app/api/preprocessing.py`).
- Resolved environment issue by disabling keyring configuration to prevent Poetry commands from hanging on Windows.
- Installed test dependencies (`givenpy`, `pyhamcrest`) and verified the preprocessing tests.
- Implemented dataset splitting logic (`app/api/split.py`) with unit tests, achieving 100% test pass rate.
