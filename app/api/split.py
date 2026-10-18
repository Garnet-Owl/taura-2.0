"""Dataset splitting utilities."""

import hashlib
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


def _hash_fraction(item: tuple[str, str], seed: int) -> float:
    """Maps a (kikuyu, english) pair and a seed to a stable number in [0, 1)."""
    key = f"{seed}\x1f{item[0]}\x1f{item[1]}".encode("utf-8")
    digest = hashlib.sha256(key).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


def split_by_hash(
    data: list[tuple[str, str]],
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    seed: int = 42,
) -> tuple[list[tuple[str, str]], list[tuple[str, str]], list[tuple[str, str]]]:
    """Split pairs by a seeded hash of each pair, keeping input order in each split.

    Each pair's split depends only on its text and the seed, so adding new data
    never moves an existing pair to a different split. Proportions are approximate.
    """
    if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-9:
        raise ValueError("Ratios must sum to 1.0")

    train, val, test = [], [], []
    for item in data:
        fraction = _hash_fraction(item, seed)
        if fraction < train_ratio:
            train.append(item)
        elif fraction < train_ratio + val_ratio:
            val.append(item)
        else:
            test.append(item)
    return train, val, test
