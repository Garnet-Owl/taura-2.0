"""Unit tests for the manual model sync script."""

import sys
import unittest
from unittest.mock import patch

from givenpy import given, then, when
from hamcrest import assert_that, equal_to

from app.shared.model_sync import SyncResult
from scripts import sync_models


class TestSyncModelsScript(unittest.TestCase):
    def test_force_flag_is_passed_to_sync(self) -> None:
        with given([]) as _:
            results = [
                SyncResult("fasttext", True, "abc"),
                SyncResult("marian", False, "abc"),
                SyncResult("other", False, error="offline"),
            ]
        with when("running the script with --force"):
            with (
                patch.object(sys, "argv", ["sync_models", "--force"]),
                patch.object(sync_models.model_sync, "cleanup_legacy_downloads"),
                patch.object(sync_models.model_sync, "cleanup_stale_snapshot_dirs"),
                patch.object(
                    sync_models.model_sync,
                    "sync_all_deployed_models",
                    return_value=results,
                ) as sync,
            ):
                sync_models.main()
        with then("the sync is forced"):
            assert_that(sync.call_args.kwargs, equal_to({"force": True}))
