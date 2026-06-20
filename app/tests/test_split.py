"""Unit tests for dataset splitting."""

import unittest

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.api.split import split_data


class TestSplit(unittest.TestCase):
    def test_split_data_correct_proportions(self):
        """Dataset should be split into train, val, and test according to ratios."""
        with given([]) as _:
            # 10 pairs of data
            data = [(f"kikuyu_{i}", f"english_{i}") for i in range(10)]
            train_ratio = 0.8
            val_ratio = 0.1
            test_ratio = 0.1

        with when("splitting the dataset"):
            train, val, test = split_data(
                data=data,
                train_ratio=train_ratio,
                val_ratio=val_ratio,
                test_ratio=test_ratio,
                seed=42,
            )

        with then("the lengths of splits match the ratios"):
            assert_that(len(train), is_(equal_to(8)))
            assert_that(len(val), is_(equal_to(1)))
            assert_that(len(test), is_(equal_to(1)))

    def test_split_data_invalid_ratios_raises_error(self):
        """ValueError should be raised if ratios do not sum to 1.0."""
        with given([]) as _:
            data = [("ki", "en")]
            train_ratio = 0.5
            val_ratio = 0.2
            test_ratio = 0.2

        with when("splitting with invalid ratios"):

            def action():
                split_data(data, train_ratio, val_ratio, test_ratio)

        with then("a ValueError is raised"):
            self.assertRaises(ValueError, action)

    def test_split_data_reproducible(self):
        """Splits should be identical when using the same seed."""
        with given([]) as _:
            data = [(f"kikuyu_{i}", f"english_{i}") for i in range(100)]
            seed = 42

        with when("splitting twice with the same seed"):
            train1, val1, test1 = split_data(data, 0.8, 0.1, 0.1, seed=seed)
            train2, val2, test2 = split_data(data, 0.8, 0.1, 0.1, seed=seed)

        with then("the splits are identical"):
            assert_that(train1, is_(equal_to(train2)))
            assert_that(val1, is_(equal_to(val2)))
            assert_that(test1, is_(equal_to(test2)))
