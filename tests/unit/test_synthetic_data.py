"""Checks that synthetic pairs are well formed and kept out of the real splits."""

import csv
import unittest
from pathlib import Path

from givenpy import given, then, when
from hamcrest import assert_that, empty, equal_to, is_, not_

SYNTHETIC_DIR = Path("data/synthetic")
PARALLEL_DIR = Path("data/parallel")


def _read_batches() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(SYNTHETIC_DIR.glob("batch_*.csv")):
        with path.open(encoding="utf-8", newline="") as handle:
            rows.extend(csv.DictReader(handle))
    return rows


class TestSyntheticData(unittest.TestCase):
    def test_synthetic_pairs_have_both_sides_and_a_status(self) -> None:
        with given([]) as _:
            rows = _read_batches()
        with when("looking for empty or unmarked pairs"):
            bad = [
                r
                for r in rows
                if not r["English"].strip()
                or not r["Kikuyu"].strip()
                or r["Status"] not in {"unreviewed", "reviewed"}
            ]
        with then("none exist"):
            assert_that(rows, not_(empty()))
            assert_that(bad, is_(empty()))

    def test_synthetic_pairs_are_not_duplicated(self) -> None:
        with given([]) as _:
            rows = _read_batches()
        with when("counting distinct English sentences"):
            distinct = {r["English"].strip().lower() for r in rows}
        with then("each appears once"):
            assert_that(len(distinct), equal_to(len(rows)))

    def test_synthetic_files_are_outside_the_parallel_folder(self) -> None:
        with given([]) as _:
            names = [p.name for p in PARALLEL_DIR.glob("*.csv")]
        with then("no synthetic batch is in it"):
            assert_that([n for n in names if n.startswith("batch_")], is_(empty()))
