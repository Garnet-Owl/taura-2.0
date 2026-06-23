"""Reads config.yaml from the project root and exposes typed settings."""

import os
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_PATH = _ROOT / "config.yaml"


def _load() -> dict:
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _abs(rel: str) -> str:
    """Resolve a path relative to the project root."""
    p = Path(rel)
    return str(p if p.is_absolute() else _ROOT / p)


# Expose root for consumers that need it
BASE_DIR: str = str(_ROOT)
DATA_DIR: str = str(_ROOT / "data")

_cfg = _load()
_paths = _cfg["paths"]
_train = _cfg["training"]
_ds = _cfg.get("datasets", {})

# ── Directories & files ───────────────────────────────────────────────────
PARALLEL_DATA_DIR: str = _abs(_paths["parallel_data_dir"])
MODELS_DIR: str = _abs(_paths["models_dir"])
MONOLINGUAL_DIR: str = _abs(_paths["monolingual_dir"])
SEED_DICTIONARY_PATH: str = _abs(_paths["seed_dictionary"])
FEEDBACK_FILE_PATH: str = _abs(_paths["feedback_file"])

TRAIN_KI_TXT: str = str(Path(MONOLINGUAL_DIR) / "train.kikuyu")
TRAIN_EN_TXT: str = str(Path(MONOLINGUAL_DIR) / "train.english")

# ── Training hyperparameters ──────────────────────────────────────────────
EMBEDDING_DIM: int = int(_train["embedding_dim"])
FASTTEXT_MODEL_TYPE: str = str(_train["fasttext_model_type"])
FASTTEXT_EPOCH: int = int(_train["fasttext_epoch"])
FASTTEXT_LR: float = float(_train["fasttext_lr"])
FASTTEXT_WS: int = int(_train["fasttext_ws"])
FASTTEXT_MIN_COUNT: int = int(_train["fasttext_min_count"])
ALIGNMENT_REFINEMENT_ITERS: int = int(_train["alignment_refinement_iters"])
FASTTEXT_MINN: int = int(_train.get("fasttext_minn", 3))
FASTTEXT_MAXN: int = int(_train.get("fasttext_maxn", 6))
VAL_SIZE: int = int(_train["val_size"])

# ── HuggingFace repos ─────────────────────────────────────────────────────
REPO_CGIAR: str = str(_ds.get("repo_cgiar", "CGIAR/KikuyuEnglish_translation"))
REPO_MICH: str = str(_ds.get("repo_mich", "michsethowusu/english-kikuyu_sentence-pairs"))


# ── Latest run helpers (derived at import time, mutable by scripts) ───────
def get_latest_run_dir() -> str:
    if not os.path.exists(MODELS_DIR):
        return MODELS_DIR
    runs = [
        d
        for d in os.listdir(MODELS_DIR)
        if d.startswith("run_") and os.path.isdir(os.path.join(MODELS_DIR, d))
    ]
    if not runs:
        return MODELS_DIR
    runs.sort(key=lambda d: os.path.getmtime(os.path.join(MODELS_DIR, d)), reverse=True)
    return os.path.join(MODELS_DIR, runs[0])


LATEST_RUN_DIR: str = get_latest_run_dir()

KI_MODEL_PATH: str = os.path.join(LATEST_RUN_DIR, "ki.bin")
EN_MODEL_PATH: str = os.path.join(LATEST_RUN_DIR, "en.bin")
PROJ_KI_EN_PATH: str = os.path.join(LATEST_RUN_DIR, "proj_ki_en.npy")
PROJ_EN_KI_PATH: str = os.path.join(LATEST_RUN_DIR, "proj_en_ki.npy")
TGT_EMBS_KI_PATH: str = os.path.join(LATEST_RUN_DIR, "tgt_embs_ki.npy")
TGT_EMBS_EN_PATH: str = os.path.join(LATEST_RUN_DIR, "tgt_embs_en.npy")
METRICS_JSON_PATH: str = os.path.join(LATEST_RUN_DIR, "evaluation_metrics.json")
SP_MODEL_PATH: str = os.path.join(LATEST_RUN_DIR, "sentencepiece.model")
MORFESSOR_KI_PATH: str = os.path.join(LATEST_RUN_DIR, "morfessor_ki.bin")
