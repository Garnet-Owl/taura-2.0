"""Re-exports all config from app.shared.config — single source of truth is config.yaml."""

from app.shared.config import *  # noqa: F401, F403

# Legacy TSV paths — kept so old references don't break at import time
TRAIN_TSV_PATH: str = ""
VAL_TSV_PATH: str = ""
TEST_TSV_PATH: str = ""
