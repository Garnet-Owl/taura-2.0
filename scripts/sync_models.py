"""Manually syncs the deployed FastText and Marian models from Hugging Face.

The server already does this automatically on every startup; use this script
for offline prep (e.g. warming a deploy target before first boot) or to force
a re-download with --force.
"""

import argparse

from app.shared import model_sync
from app.shared.logger import setup_logger

logger = setup_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if the local copy already matches the Hub revision.",
    )
    args = parser.parse_args()

    model_sync.cleanup_legacy_downloads()
    model_sync.cleanup_stale_snapshot_dirs()
    for result in model_sync.sync_all_deployed_models(force=args.force):
        if result.error:
            logger.warning("%s: sync failed (%s)", result.name, result.error)
        elif result.updated:
            logger.info("%s: updated to revision %s", result.name, result.revision)
        else:
            logger.info(
                "%s: already up to date (revision %s)", result.name, result.revision
            )


if __name__ == "__main__":
    main()
