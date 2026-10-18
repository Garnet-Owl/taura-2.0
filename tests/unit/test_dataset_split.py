"""Unit tests for building the seeded train/validation/test split and loading it."""

import tempfile
import unittest
from pathlib import Path

from givenpy import given, then, when
from hamcrest import assert_that, close_to, empty, equal_to, greater_than, is_

from scripts.prepare_dataset import build_splits, load_parallel_pairs
from scripts.train_embeddings import load_sentences, load_train_and_val


def _write_csv(path: Path, rows: list[tuple[str, str]]) -> None:
    lines = ["Reference,Kikuyu,English"]
    lines += [f"1:{i},{ki},{en}" for i, (ki, en) in enumerate(rows, start=1)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class TestLoadParallelPairs(unittest.TestCase):
    def test_reads_all_csvs_and_drops_duplicate_pairs(self):
        """Exact duplicate pairs across books must not leak between splits."""
        with given([]) as _:
            tmp = Path(tempfile.mkdtemp())
            (tmp / "sub").mkdir()
            _write_csv(tmp / "a.csv", [("ki1", "en1"), ("ki2", "en2")])
            _write_csv(tmp / "sub" / "b.csv", [("ki1", "en1"), ("ki3", "en3")])

        with when("loading every parallel CSV"):
            pairs = load_parallel_pairs(str(tmp))

        with then("each unique pair appears once, in file order"):
            assert_that(
                pairs, is_(equal_to([("ki1", "en1"), ("ki2", "en2"), ("ki3", "en3")]))
            )


class TestBuildSplits(unittest.TestCase):
    def test_writes_disjoint_80_10_10_split(self):
        """The split covers every pair once with roughly 80/10/10 proportions."""
        with given([]) as _:
            tmp = Path(tempfile.mkdtemp())
            rows = [(f"ki{i}", f"en{i}") for i in range(2000)]
            _write_csv(tmp / "book.csv", rows)
            splits_dir = tmp / "splits"

        with when("building the splits"):
            build_splits(str(tmp), str(splits_dir), seed=42)
            train_ki, _, val_ki, _ = load_train_and_val(
                str(splits_dir / "train.tsv"), str(splits_dir / "val.tsv")
            )
            test_ki, _ = load_sentences(str(splits_dir / "test.tsv"))

        with then("every pair lands once and no sentence is shared between splits"):
            assert_that(len(train_ki) + len(val_ki) + len(test_ki), is_(2000))
            assert_that(len(train_ki), is_(close_to(1600, 60)))
            assert_that(len(val_ki), is_(close_to(200, 40)))
            assert_that(len(test_ki), is_(close_to(200, 40)))
            assert_that(set(train_ki) & set(val_ki), is_(empty()))
            assert_that(set(train_ki) & set(test_ki), is_(empty()))
            assert_that(set(val_ki) & set(test_ki), is_(empty()))

    def test_adding_a_book_keeps_existing_pairs_in_place(self):
        """A new book only adds pairs; no existing pair changes split."""
        with given([]) as _:
            tmp = Path(tempfile.mkdtemp())
            _write_csv(tmp / "a.csv", [(f"ki{i}", f"en{i}") for i in range(300)])
            build_splits(str(tmp), str(tmp / "before"), seed=42)
            _write_csv(tmp / "b.csv", [(f"new{i}", f"neu{i}") for i in range(300)])

        with when("rebuilding the splits with the new book"):
            build_splits(str(tmp), str(tmp / "after"), seed=42)

        with then("each old split is contained in the new one"):
            for name in ["train", "val", "test"]:
                before, _ = load_sentences(str(tmp / "before" / f"{name}.tsv"))
                after, _ = load_sentences(str(tmp / "after" / f"{name}.tsv"))
                assert_that(set(before) - set(after), is_(empty()))
                assert_that(len(after), is_(greater_than(len(before))))

    def test_split_is_reproducible_with_seed(self):
        """Rebuilding with the same seed gives an identical validation file."""
        with given([]) as _:
            tmp = Path(tempfile.mkdtemp())
            _write_csv(tmp / "book.csv", [(f"ki{i}", f"en{i}") for i in range(50)])

        with when("building the splits twice"):
            build_splits(str(tmp), str(tmp / "s1"), seed=42)
            build_splits(str(tmp), str(tmp / "s2"), seed=42)

        with then("the validation files are identical"):
            first = (tmp / "s1" / "val.tsv").read_text(encoding="utf-8")
            second = (tmp / "s2" / "val.tsv").read_text(encoding="utf-8")
            assert_that(first, is_(equal_to(second)))


class TestLoadSentencesQuotes(unittest.TestCase):
    def test_sentences_starting_with_quotes_are_kept_whole(self):
        """Quote marks are text in the split TSVs, not CSV field delimiters."""
        with given([]) as _:
            tmp = Path(tempfile.mkdtemp())
            tsv = tmp / "val.tsv"
            tsv.write_text(
                'kikuyu\tenglish\n"Ũkĩrĩ, mũtumia\t"Woman, rise\nki2\ten2\n',
                encoding="utf-8",
            )

        with when("loading the TSV"):
            ki, en = load_sentences(str(tsv))

        with then("both rows load with the quote mark intact"):
            assert_that(ki, is_(equal_to(['"Ũkĩrĩ, mũtumia', "ki2"])))
            assert_that(en, is_(equal_to(['"Woman, rise', "en2"])))
