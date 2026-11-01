"""Unit tests for syncing deployed models from Hugging Face."""

import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_, is_not

from app.shared import config, model_sync


def _fake_model_info(sha: str) -> MagicMock:
    info = MagicMock()
    info.sha = sha
    return info


def _write_marker(deploy_dir: str, sha: str) -> None:
    os.makedirs(deploy_dir, exist_ok=True)
    with open(os.path.join(deploy_dir, model_sync._REVISION_FILE), "w") as f:
        json.dump({"sha": sha}, f)


class TestFastTextSync(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="taura-test-")
        self.deploy_dir = os.path.join(self.tmp, "fasttext-deployed")
        self._patches = [
            patch.object(config, "FASTTEXT_DEPLOY_DIR", self.deploy_dir),
            patch.object(config, "HF_MODEL_REPO", "org/fake-repo"),
        ]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in self._patches:
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_skips_download_when_local_revision_matches_remote(self):
        """No network transfer happens when the cached revision is current."""
        with given([]) as _:
            _write_marker(self.deploy_dir, "sha-abc")
            hf_api = MagicMock()
            hf_api.model_info.return_value = _fake_model_info("sha-abc")

        with when("syncing with a patched HfApi and snapshot_download"):
            with (
                patch.object(model_sync, "HfApi", return_value=hf_api),
                patch.object(model_sync, "snapshot_download") as fake_download,
            ):
                result = model_sync.sync_fasttext_models()

        with then("snapshot_download is never called and nothing changed"):
            fake_download.assert_not_called()
            assert_that(result.updated, is_(False))
            assert_that(result.revision, is_(equal_to("sha-abc")))

    def test_downloads_and_replaces_when_revision_differs(self):
        """A stale local revision triggers a download that replaces the deploy dir."""
        with given([]) as _:
            _write_marker(self.deploy_dir, "sha-old")
            with open(os.path.join(self.deploy_dir, "ki.bin"), "w") as f:
                f.write("stale-content")

            hf_api = MagicMock()
            hf_api.model_info.return_value = _fake_model_info("sha-new")

            def fake_snapshot_download(repo_id, allow_patterns, local_dir):
                fasttext_dir = os.path.join(local_dir, "fasttext")
                os.makedirs(fasttext_dir, exist_ok=True)
                with open(os.path.join(fasttext_dir, "ki.bin"), "w") as f:
                    f.write("fresh-content")
                with open(os.path.join(fasttext_dir, "en.bin"), "w") as f:
                    f.write("fresh-content-en")
                return local_dir

        with when("syncing fasttext models"):
            with (
                patch.object(model_sync, "HfApi", return_value=hf_api),
                patch.object(
                    model_sync, "snapshot_download", side_effect=fake_snapshot_download
                ) as fake_download,
            ):
                result = model_sync.sync_fasttext_models()

        with then("the deploy dir now holds only the fresh files"):
            fake_download.assert_called_once()
            assert_that(result.updated, is_(True))
            assert_that(result.revision, is_(equal_to("sha-new")))
            with open(os.path.join(self.deploy_dir, "ki.bin")) as f:
                assert_that(f.read(), is_(equal_to("fresh-content")))
            assert_that(os.path.isfile(os.path.join(self.deploy_dir, "en.bin")), is_(True))

        with then("the local revision marker is updated"):
            with open(os.path.join(self.deploy_dir, model_sync._REVISION_FILE)) as f:
                assert_that(json.load(f)["sha"], is_(equal_to("sha-new")))

    def test_force_redownloads_even_when_up_to_date(self):
        """force=True bypasses the revision check."""
        with given([]) as _:
            _write_marker(self.deploy_dir, "sha-abc")
            hf_api = MagicMock()
            hf_api.model_info.return_value = _fake_model_info("sha-abc")

            def fake_snapshot_download(repo_id, allow_patterns, local_dir):
                fasttext_dir = os.path.join(local_dir, "fasttext")
                os.makedirs(fasttext_dir, exist_ok=True)
                with open(os.path.join(fasttext_dir, "ki.bin"), "w") as f:
                    f.write("re-downloaded")
                return local_dir

        with when("syncing with force=True"):
            with (
                patch.object(model_sync, "HfApi", return_value=hf_api),
                patch.object(
                    model_sync, "snapshot_download", side_effect=fake_snapshot_download
                ) as fake_download,
            ):
                result = model_sync.sync_fasttext_models(force=True)

        with then("snapshot_download runs despite the matching revision"):
            fake_download.assert_called_once()
            assert_that(result.updated, is_(True))

    def test_network_failure_does_not_raise_and_leaves_local_copy_untouched(self):
        """A Hugging Face lookup failure degrades gracefully instead of crashing."""
        with given([]) as _:
            _write_marker(self.deploy_dir, "sha-abc")
            with open(os.path.join(self.deploy_dir, "ki.bin"), "w") as f:
                f.write("existing-content")

            hf_api = MagicMock()
            hf_api.model_info.side_effect = OSError("network unreachable")

        with when("syncing while Hugging Face is unreachable"):
            with (
                patch.object(model_sync, "HfApi", return_value=hf_api),
                patch.object(model_sync, "snapshot_download") as fake_download,
            ):
                result = model_sync.sync_fasttext_models()

        with then("no exception propagates and the existing files are untouched"):
            fake_download.assert_not_called()
            assert_that(result.updated, is_(False))
            assert_that(result.error, is_not(None))
            with open(os.path.join(self.deploy_dir, "ki.bin")) as f:
                assert_that(f.read(), is_(equal_to("existing-content")))


class TestMarianSync(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="taura-test-")
        self.deploy_dir = os.path.join(self.tmp, "marian-ct2-int8")
        self._patches = [
            patch.object(config, "NEURAL_MODEL_DIR", self.deploy_dir),
            patch.object(config, "HF_MODEL_REPO", "org/fake-repo"),
        ]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in self._patches:
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_flattens_ct2_int8_subfolders_per_direction(self):
        """ki_en/ct2-int8/model.bin on the Hub lands at ki_en/model.bin locally."""
        with given([]) as _:
            hf_api = MagicMock()
            hf_api.model_info.return_value = _fake_model_info("sha-marian-1")

            def fake_snapshot_download(repo_id, allow_patterns, local_dir):
                for direction in ("ki_en", "en_ki"):
                    nested = os.path.join(local_dir, direction, "ct2-int8")
                    os.makedirs(nested, exist_ok=True)
                    with open(os.path.join(nested, "model.bin"), "w") as f:
                        f.write(f"{direction}-weights")
                return local_dir

        with when("syncing marian models"):
            with (
                patch.object(model_sync, "HfApi", return_value=hf_api),
                patch.object(
                    model_sync, "snapshot_download", side_effect=fake_snapshot_download
                ),
            ):
                result = model_sync.sync_marian_models()

        with then("each direction's model.bin sits directly under its folder"):
            assert_that(result.updated, is_(True))
            for direction in ("ki_en", "en_ki"):
                path = os.path.join(self.deploy_dir, direction, "model.bin")
                assert_that(os.path.isfile(path), is_(True))
                with open(path) as f:
                    assert_that(f.read(), is_(equal_to(f"{direction}-weights")))
            nested_leftover = os.path.join(self.deploy_dir, "ki_en", "ct2-int8")
            assert_that(os.path.isdir(nested_leftover), is_(False))


class TestCleanupLegacyDownloads(unittest.TestCase):
    def test_removes_known_legacy_dirs_but_ignores_missing_ones(self):
        """Only the known legacy manual-download paths are removed, never run_* training dirs."""
        with given([]) as _:
            tmp = tempfile.mkdtemp(prefix="taura-test-")
            self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)

            legacy_dir = os.path.join(tmp, "models", "run_hf_fasttext")
            os.makedirs(legacy_dir)
            scratch_dir = os.path.join(tmp, "hf-download")
            os.makedirs(scratch_dir)

            real_run_dir = os.path.join(tmp, "models", "run_20261101_120000")
            os.makedirs(real_run_dir)
            with open(os.path.join(real_run_dir, "ki.bin"), "w") as f:
                f.write("real training output")

        with when("cleaning up legacy downloads"):
            with patch.object(config, "BASE_DIR", tmp):
                removed = model_sync.cleanup_legacy_downloads()

        with then("only the legacy download paths are gone"):
            assert_that(os.path.isdir(legacy_dir), is_(False))
            assert_that(os.path.isdir(scratch_dir), is_(False))
            assert_that(len(removed), is_(equal_to(2)))

        with then("the real training run directory is left alone"):
            assert_that(os.path.isdir(real_run_dir), is_(True))
            assert_that(os.path.isfile(os.path.join(real_run_dir, "ki.bin")), is_(True))


class TestCleanupStaleSnapshotDirs(unittest.TestCase):
    def test_removes_orphaned_snapshot_dirs_but_ignores_unrelated_entries(self):
        """A killed sync leaves its temp snapshot dir behind; the next sync clears it."""
        with given([]) as _:
            fake_temp_root = tempfile.mkdtemp(prefix="taura-test-temproot-")
            self.addCleanup(shutil.rmtree, fake_temp_root, ignore_errors=True)

            orphaned_fasttext = os.path.join(
                fake_temp_root, "taura-fasttext-snapshot-abc123"
            )
            os.makedirs(orphaned_fasttext)
            with open(os.path.join(orphaned_fasttext, "ki.bin"), "w") as f:
                f.write("partial download from a killed process")

            orphaned_marian = os.path.join(fake_temp_root, "taura-marian-snapshot-xyz789")
            os.makedirs(orphaned_marian)

            unrelated_dir = os.path.join(fake_temp_root, "some-other-apps-temp-dir")
            os.makedirs(unrelated_dir)
            unrelated_file = os.path.join(
                fake_temp_root, "taura-fasttext-snapshot-notadir.txt"
            )
            with open(unrelated_file, "w") as f:
                f.write("not a directory, must be left alone")

        with when("cleaning up stale snapshot dirs"):
            removed = model_sync.cleanup_stale_snapshot_dirs(temp_root=fake_temp_root)

        with then("only the orphaned snapshot directories are gone"):
            assert_that(os.path.isdir(orphaned_fasttext), is_(False))
            assert_that(os.path.isdir(orphaned_marian), is_(False))
            assert_that(len(removed), is_(equal_to(2)))

        with then("unrelated entries are left alone"):
            assert_that(os.path.isdir(unrelated_dir), is_(True))
            assert_that(os.path.isfile(unrelated_file), is_(True))

    def test_does_nothing_when_temp_root_has_no_leftovers(self):
        """A clean temp dir (normal exit already cleaned up) is a no-op."""
        with given([]) as _:
            fake_temp_root = tempfile.mkdtemp(prefix="taura-test-temproot-")
            self.addCleanup(shutil.rmtree, fake_temp_root, ignore_errors=True)

        with when("cleaning up stale snapshot dirs"):
            removed = model_sync.cleanup_stale_snapshot_dirs(temp_root=fake_temp_root)

        with then("nothing was removed"):
            assert_that(removed, is_(equal_to([])))


if __name__ == "__main__":
    unittest.main()
