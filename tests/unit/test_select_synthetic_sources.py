"""Unit tests for picking the next English sentences to translate."""

import bz2
import tempfile
import unittest
from pathlib import Path

from givenpy import given, then, when
from hamcrest import assert_that, contains_exactly, equal_to, is_

from scripts.select_synthetic_sources import (
    is_usable,
    jaccard,
    load_tatoeba,
    select,
    used_ids,
)


class TestSelect(unittest.TestCase):
    def test_skips_used_ids_known_sentences_and_near_duplicates(self) -> None:
        with given([]) as _:
            rows = [
                ("1", "We should look after our parents."),
                ("2", "We should look after our parents well."),
                ("3", "The children are brushing their teeth."),
                ("4", "Do you want to have some tea?"),
                ("5", "Do you want some coffee or something?"),
            ]
        with when("selecting with id 3 used and the tea sentence known"):
            chosen = select(rows, {"tatoeba:3"}, {"do you want to have some tea"}, 10)
        with then("only fresh, distinct sentences remain"):
            texts = {text for _, text in chosen}
            assert_that("The children are brushing their teeth." in texts, is_(False))
            assert_that("Do you want to have some tea?" in texts, is_(False))
            assert_that(
                len(texts & {rows[0][1], rows[1][1]}), equal_to(1)
            )  # near duplicates

    def test_is_usable_filters_length_and_blocked_words(self) -> None:
        with given([]) as _:
            cases = [
                "Hi there.",
                "This is a good sentence for us.",
                "What the shit is this?",
            ]
        with when("checking each"):
            results = [is_usable(c) for c in cases]
        with then("only the middle one passes"):
            assert_that(results, contains_exactly(False, True, False))

    def test_jaccard_of_identical_sets_is_one(self) -> None:
        with given([]) as _:
            words = {"a", "b"}
        with then("similarity is 1"):
            assert_that(jaccard(words, words), equal_to(1.0))


class TestSourceFiles(unittest.TestCase):
    def test_used_ids_reads_every_batch_file(self) -> None:
        with given([]) as _:
            tmp = Path(tempfile.mkdtemp(prefix="taura-synth-"))
            header = "English,Kikuyu,Confidence,Source\n"
            (tmp / "batch_001.csv").write_text(header + "A b,C d,1,tatoeba:1\n")
            (tmp / "batch_002.csv").write_text(header + "E f,G h,0.5,tatoeba:2\n")
        with when("collecting the used ids"):
            ids = used_ids(tmp)
        with then("both batches are included"):
            assert_that(ids, equal_to({"tatoeba:1", "tatoeba:2"}))

    def test_load_tatoeba_returns_id_and_sentence(self) -> None:
        with given([]) as _:
            tmp = Path(tempfile.mkdtemp(prefix="taura-synth-")) / "eng.tsv.bz2"
            with bz2.open(tmp, "wt", encoding="utf-8") as handle:
                handle.write("7\teng\tHello there my friend.\nbad\n")
        with when("loading the export"):
            rows = load_tatoeba(tmp)
        with then("short malformed lines are skipped"):
            assert_that(rows, equal_to([("7", "Hello there my friend.")]))
