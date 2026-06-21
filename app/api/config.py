import os

# Project Directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Model Paths
def get_latest_run_dir() -> str:
    if not os.path.exists(MODELS_DIR):
        return MODELS_DIR
    runs = [d for d in os.listdir(MODELS_DIR) if d.startswith("run_") and os.path.isdir(os.path.join(MODELS_DIR, d))]
    if not runs:
        return MODELS_DIR
    runs.sort(reverse=True)
    return os.path.join(MODELS_DIR, runs[0])

LATEST_RUN_DIR = get_latest_run_dir()

KI_MODEL_PATH = os.path.join(LATEST_RUN_DIR, "ki.bin")
EN_MODEL_PATH = os.path.join(LATEST_RUN_DIR, "en.bin")
PROJ_KI_EN_PATH = os.path.join(LATEST_RUN_DIR, "proj_ki_en.npy")
PROJ_EN_KI_PATH = os.path.join(LATEST_RUN_DIR, "proj_en_ki.npy")
TGT_EMBS_KI_PATH = os.path.join(LATEST_RUN_DIR, "tgt_embs_ki.npy")
TGT_EMBS_EN_PATH = os.path.join(LATEST_RUN_DIR, "tgt_embs_en.npy")
METRICS_JSON_PATH = os.path.join(LATEST_RUN_DIR, "evaluation_metrics.json")
SP_MODEL_PATH = os.path.join(MODELS_DIR, "sentencepiece.model")

# TSV Dataset Paths
TRAIN_TSV_PATH = os.path.join(DATA_DIR, "train.tsv")
VAL_TSV_PATH = os.path.join(DATA_DIR, "val.tsv")
TEST_TSV_PATH = os.path.join(DATA_DIR, "test.tsv")
FEEDBACK_FILE_PATH = os.path.join(DATA_DIR, "feedback.jsonl")

# Monolingual Training Paths
TRAIN_KI_TXT = os.path.join(DATA_DIR, "train.kikuyu")
TRAIN_EN_TXT = os.path.join(DATA_DIR, "train.english")

# Hugging Face Repositories
REPO_CGIAR = "CGIAR/KikuyuEnglish_translation"
REPO_MICH = "michsethowusu/english-kikuyu_sentence-pairs"

# Hyperparameters
EMBEDDING_DIM = 150
FASTTEXT_MODEL_TYPE = "skipgram"
FASTTEXT_EPOCH = 35
FASTTEXT_LR = 0.1
FASTTEXT_WS = 8
FASTTEXT_MIN_COUNT = 2
ALIGNMENT_REFINEMENT_ITERS = 5
SP_VOCAB_SIZE = 8000
