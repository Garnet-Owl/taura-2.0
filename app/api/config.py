import os

# Project Directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Model Paths
KI_MODEL_PATH = os.path.join(MODELS_DIR, "ki.bin")
EN_MODEL_PATH = os.path.join(MODELS_DIR, "en.bin")
PROJ_KI_EN_PATH = os.path.join(MODELS_DIR, "proj_ki_en.npy")
PROJ_EN_KI_PATH = os.path.join(MODELS_DIR, "proj_en_ki.npy")

# TSV Dataset Paths
TRAIN_TSV_PATH = os.path.join(DATA_DIR, "train.tsv")
VAL_TSV_PATH = os.path.join(DATA_DIR, "val.tsv")
TEST_TSV_PATH = os.path.join(DATA_DIR, "test.tsv")
METRICS_JSON_PATH = os.path.join(MODELS_DIR, "evaluation_metrics.json")
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
FASTTEXT_EPOCH = 1
FASTTEXT_LR = 0.1
FASTTEXT_WS = 8
FASTTEXT_MIN_COUNT = 1
