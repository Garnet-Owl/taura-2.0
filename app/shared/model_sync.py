"""Keeps the locally served FastText and Marian models in sync with Hugging Face.

Always keeps exactly one deployed copy of each model family (no run_*
versioning for serving): config.FASTTEXT_DEPLOY_DIR and config.NEURAL_MODEL_DIR.
Staleness is checked against the Hub repo's own latest commit SHA, so nothing
needs a manual version bump to stay accurate.
"""

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from typing import Callable

from huggingface_hub import HfApi, snapshot_download

from app.shared import config
from app.shared.logger import setup_logger

logger = setup_logger(__name__)

_REVISION_FILE = ".hf_revision.json"
_LEGACY_DOWNLOAD_PATHS = ("models/run_hf_fasttext", "hf-download")


@dataclass(frozen=True)
class SyncResult:
    name: str
    updated: bool
    revision: str | None = None
    error: str | None = None


def _remote_revision(repo_id: str) -> str:
    info = HfApi().model_info(repo_id)
    return str(info.sha)


def _read_local_revision(deploy_dir: str) -> str | None:
    marker = os.path.join(deploy_dir, _REVISION_FILE)
    if not os.path.isfile(marker):
        return None
    try:
        with open(marker, "r", encoding="utf-8") as f:
            sha = json.load(f).get("sha")
        return str(sha) if sha is not None else None
    except (OSError, json.JSONDecodeError):
        return None


def _write_local_revision(deploy_dir: str, sha: str) -> None:
    with open(os.path.join(deploy_dir, _REVISION_FILE), "w", encoding="utf-8") as f:
        json.dump({"sha": sha}, f)


def _replace_dir(deploy_dir: str, staging_dir: str) -> None:
    """Swaps deploy_dir's contents for staging_dir's, keeping a single copy."""
    parent = os.path.dirname(deploy_dir) or "."
    os.makedirs(parent, exist_ok=True)
    if os.path.isdir(deploy_dir):
        shutil.rmtree(deploy_dir)
    shutil.move(staging_dir, deploy_dir)


def _sync(
    *,
    name: str,
    deploy_dir: str,
    allow_patterns: list[str],
    build_staging: Callable[[str, str], None],
    force: bool,
) -> SyncResult:
    try:
        remote_sha = _remote_revision(config.HF_MODEL_REPO)
    except Exception as exc:  # offline / Hub error must never crash startup
        logger.warning("Could not reach Hugging Face to check %s models: %s", name, exc)
        return SyncResult(name=name, updated=False, error=str(exc))

    local_sha = _read_local_revision(deploy_dir)
    if not force and local_sha == remote_sha and os.path.isdir(deploy_dir):
        logger.info("%s models already up to date (revision %s).", name, remote_sha[:8])
        return SyncResult(name=name, updated=False, revision=remote_sha)

    staging_dir = f"{deploy_dir}.staging"
    try:
        if os.path.isdir(staging_dir):
            shutil.rmtree(staging_dir)
        with tempfile.TemporaryDirectory(prefix=f"taura-{name}-snapshot-") as tmp:
            snapshot_download(
                repo_id=config.HF_MODEL_REPO, allow_patterns=allow_patterns, local_dir=tmp
            )
            build_staging(tmp, staging_dir)
        _replace_dir(deploy_dir, staging_dir)
    except Exception as exc:
        logger.warning("Failed to download %s models: %s", name, exc)
        shutil.rmtree(staging_dir, ignore_errors=True)
        return SyncResult(name=name, updated=False, error=str(exc))

    _write_local_revision(deploy_dir, remote_sha)
    logger.info("%s models updated to Hugging Face revision %s.", name, remote_sha[:8])
    return SyncResult(name=name, updated=True, revision=remote_sha)


def _flatten(src_dir: str, dst_dir: str) -> None:
    os.makedirs(dst_dir, exist_ok=True)
    for entry in os.listdir(src_dir):
        shutil.copy2(os.path.join(src_dir, entry), os.path.join(dst_dir, entry))


def sync_fasttext_models(force: bool = False) -> SyncResult:
    """Syncs the single deployed FastText + Procrustes model copy from the Hub."""

    def build_staging(tmp: str, staging_dir: str) -> None:
        _flatten(os.path.join(tmp, "fasttext"), staging_dir)

    return _sync(
        name="fasttext",
        deploy_dir=config.FASTTEXT_DEPLOY_DIR,
        allow_patterns=["fasttext/*"],
        build_staging=build_staging,
        force=force,
    )


def sync_marian_models(force: bool = False) -> SyncResult:
    """Syncs the single deployed Marian CTranslate2 int8 model copy from the Hub."""

    def build_staging(tmp: str, staging_dir: str) -> None:
        for direction in ("ki_en", "en_ki"):
            _flatten(
                os.path.join(tmp, direction, "ct2-int8"),
                os.path.join(staging_dir, direction),
            )

    return _sync(
        name="marian",
        deploy_dir=config.NEURAL_MODEL_DIR,
        allow_patterns=["ki_en/ct2-int8/*", "en_ki/ct2-int8/*"],
        build_staging=build_staging,
        force=force,
    )


def sync_all_deployed_models(force: bool = False) -> list[SyncResult]:
    """Syncs both deployed model families; never raises on network/Hub errors."""
    return [sync_marian_models(force=force), sync_fasttext_models(force=force)]


def cleanup_legacy_downloads() -> list[str]:
    """Removes known legacy manual-download folders, never touches run_* training dirs."""
    removed = []
    for rel in _LEGACY_DOWNLOAD_PATHS:
        path = os.path.join(config.BASE_DIR, rel)
        if os.path.isdir(path):
            shutil.rmtree(path)
            removed.append(path)
    return removed
