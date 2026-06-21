import logging
import os


LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logger(name: str = "default"):
    log_level_str = get_log_level()
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
    )
    logger = logging.getLogger(name)

    for lib in ["httpx", "httpcore", "fastapi"]:
        logging.getLogger(lib).setLevel(logging.WARNING)

    if log_level == logging.DEBUG:
        # quiet noisy libraries to avoid log flooding in debug mode
        for lib in ["urllib3", "asyncio"]:
            logging.getLogger(lib).setLevel(logging.WARNING)

    return logger


def get_log_level() -> str:
    env = os.getenv("ENV", "PROD").upper()
    log_level = "DEBUG" if (env == "DEV" or env == "TEST") else "INFO"

    return log_level
