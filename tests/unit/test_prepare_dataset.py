"""Unit tests for building the seeded train/validation/test split."""

import tempfile
import unittest
from pathlib import Path

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from scripts.prepare_dataset import load_parallel_pairs, write_split_tsv
from scripts.train_embeddings import load_train_val


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class TestLoadParallelPairs(unittest.TestCase):
    def test_reads_every_csv_recursively_in_sorted_order(self):
        """Pairs come from all CSVs, including sub-folders, as (kikuyu, english)."""
        with given([]) as _:
            tmp = tempfile.TemporaryDirectory()
            root = Path(tmp.name)
            _write(root / "b_aligned.csv", "Reference,Kikuyu,English\nB 1:1,kb,eb\n")
            _write(root / "agri" / "a.csv", "Kikuyu,English\nka,ea\n")

        with when("loading the pairs"):
            pairs = load_parallel_pairs(tmp.name)

        with then("both files are read in sorted path order"):
            assert_that(pairs, is_(equal_to([("ka", "ea"), ("kb", "eb")])))
        tmp.cleanup()

    def test_skips_empty_rows_and_drops_exact_duplicates(self):
        """Empty sides are skipped and repeated pairs kept once to avoid leakage."""
        with given([]) as _:
            tmp = tempfile.TemporaryDirectory()
            _write(
                Path(tmp.name) / "x.csv",
                "Kikuyu,English\n k1 , e1 \n,e2\nk3,\nk1,e1\nk1,e4\n",
            )

        with when("loading the pairs"):
            pairs = load_parallel_pairs(tmp.name)

        with then("only distinct, complete, stripped pairs remain"):
            assert_that(pairs, is_(equal_to([("k1", "e1"), ("k1", "e4")])))
        tmp.cleanup()


class TestSplitFilesRoundTrip(unittest.TestCase):
    def test_training_reads_back_the_written_train_and_val_splits(self):
        """Split TSVs written by prepare_dataset load unchanged in training."""
        with given([]) as _:
            tmp = tempfile.TemporaryDirectory()
            train_path = str(Path(tmp.name) / "splits" / "train.tsv")
            val_path = str(Path(tmp.name) / "splits" / "val.tsv")
            train = [("k\t1", "e\n1"), ("k2", "e2")]
            val = [("k3", "e3")]

        with when("writing the splits and loading them for training"):
            write_split_tsv(train, train_path)
            write_split_tsv(val, val_path)
            train_ki, train_en, val_ki, val_en = load_train_val(train_path, val_path)

        with then("training sees the same pairs with whitespace flattened"):
            assert_that(train_ki, is_(equal_to(["k 1", "k2"])))
            assert_that(train_en, is_(equal_to(["e 1", "e2"])))
            assert_that(val_ki, is_(equal_to(["k3"])))
            assert_that(val_en, is_(equal_to(["e3"])))
        tmp.cleanup()

    def test_straight_quotes_do_not_merge_rows(self):
        """A verse starting with a straight quote must not swallow later rows."""
        with given([]) as _:
            tmp = tempfile.TemporaryDirectory()
            path = str(Path(tmp.name) / "train.tsv")
            pairs = [('"Ũka," akiuga', '"Come," he said'), ("k2", "e2")]

        with when("writing and reading the split"):
            write_split_tsv(pairs, path)
            train_ki, train_en, _, _ = load_train_val(path, path)

        with then("every pair is read back separately and unchanged"):
            assert_that(train_ki, is_(equal_to(['"Ũka," akiuga', "k2"])))
            assert_that(train_en, is_(equal_to(['"Come," he said', "e2"])))
        tmp.cleanup()

    def test_missing_split_raises_with_rebuild_hint(self):
        """Training fails clearly when the split files have not been built."""
        with given([]) as _:
            tmp = tempfile.TemporaryDirectory()
            missing = str(Path(tmp.name) / "train.tsv")

        with when("loading the splits"):

            def action():
                load_train_val(missing, missing)

        with then("a FileNotFoundError tells the user to run prepare_dataset"):
            with self.assertRaisesRegex(FileNotFoundError, "prepare_dataset"):
                action()
        tmp.cleanup()
