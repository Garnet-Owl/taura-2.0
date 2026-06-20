"""Dataset splitting utilities."""

import random
from typing import Any


def split_data(
    data: list[Any],
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    seed: int | None = None,
) -> tuple[list[Any], list[Any], list[Any]]:
    """Split a dataset into train, validation, and test sets.

    Ratios must sum to 1.0.
    """
    if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-9:
        raise ValueError("Ratios must sum to 1.0")

    shuffled_data = list(data)
    rng = random.Random(seed) if seed is not None else random.Random()
    rng.shuffle(shuffled_data)

    n = len(shuffled_data)
    train_end = int(round(n * train_ratio))
    val_end = train_end + int(round(n * val_ratio))

    train = shuffled_data[:train_end]
    val = shuffled_data[train_end:val_end]
    test = shuffled_data[val_end:]

    return train, val, test
