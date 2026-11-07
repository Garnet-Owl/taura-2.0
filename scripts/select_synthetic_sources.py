"""Picks the next English source sentences to translate into synthetic pairs.

Source: Tatoeba English sentences (CC BY 2.0 FR, https://tatoeba.org), downloaded
from downloads.tatoeba.org. The candidate order is a fixed seeded shuffle, so
"where we left off" is simply every Tatoeba id that already appears in a
`data/synthetic/batch_*.csv` file; the next run continues with the next ids.

Usage: python -m scripts.select_synthetic_sources --count 872 --out queue.tsv
"""

import argparse
import bz2
import csv
import random
import re
import urllib.request
from pathlib import Path

from scripts.evaluate import load_all_parallel_csvs

TATOEBA_URL = "https://downloads.tatoeba.org/exports/per_language/eng/eng_sentences.tsv.bz2"
SEED = 42
MIN_WORDS, MAX_WORDS = 5, 10
BLOCKED_WORDS = {"shit", "fuck", "fucking", "damn", "ass", "bitch", "sex", "kill"}
SIMILARITY_LIMIT = 0.8
SENTENCE = re.compile(r"^[A-Z][A-Za-z ,'\-]*[.?!]$")


def normalise(text: str) -> str:
    return re.sub(r"[^a-z ]", "", text.lower()).strip()


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a | b else 0.0


def load_tatoeba(path: Path) -> list[tuple[str, str]]:
    """Returns (id, sentence) rows from the downloaded bz2 export."""
    if not path.exists():
        urllib.request.urlretrieve(TATOEBA_URL, path)
    with bz2.open(path, "rt", encoding="utf-8") as handle:
        rows = csv.reader(handle, delimiter="\t", quoting=csv.QUOTE_NONE)
        return [(r[0], r[2]) for r in rows if len(r) >= 3]


def used_ids(synthetic_dir: Path) -> set[str]:
    ids: set[str] = set()
    for batch in synthetic_dir.glob("batch_*.csv"):
        with batch.open(encoding="utf-8", newline="") as handle:
            ids.update(r["Source"] for r in csv.DictReader(handle))
    return ids


def known_sentences(synthetic_dir: Path, parallel_dir: Path) -> set[str]:
    known = {normalise(e) for e in load_all_parallel_csvs(str(parallel_dir))[1]}
    for batch in synthetic_dir.glob("batch_*.csv"):
        with batch.open(encoding="utf-8", newline="") as handle:
            known.update(normalise(r["English"]) for r in csv.DictReader(handle))
    return known


def is_usable(sentence: str) -> bool:
    words = sentence.split()
    if BLOCKED_WORDS & set(normalise(sentence).split()):
        return False
    return bool(SENTENCE.match(sentence)) and MIN_WORDS <= len(words) <= MAX_WORDS


def select(
    rows: list[tuple[str, str]], skip_ids: set[str], known: set[str], count: int
) -> list[tuple[str, str]]:
    rows = sorted(rows)
    random.Random(SEED).shuffle(rows)
    chosen: list[tuple[str, str]] = []
    word_sets: list[set[str]] = []
    for sid, text in rows:
        key = f"tatoeba:{sid}"
        words = set(normalise(text).split())
        if key in skip_ids or not is_usable(text) or normalise(text) in known:
            continue
        if any(jaccard(words, other) >= SIMILARITY_LIMIT for other in word_sets):
            continue
        chosen.append((key, text))
        word_sets.append(words)
        if len(chosen) == count:
            break
    return chosen


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cache", type=Path, default=Path("/tmp/eng.tsv.bz2"))
    args = parser.parse_args()
    synthetic, parallel = Path("data/synthetic"), Path("data/parallel")
    picked = select(
        load_tatoeba(args.cache),
        used_ids(synthetic),
        known_sentences(synthetic, parallel),
        args.count,
    )
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        csv.writer(handle, delimiter="\t").writerows(picked)


if __name__ == "__main__":
    main()
