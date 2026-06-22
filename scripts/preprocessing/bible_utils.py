"""
Bible utilities for the Taura project.

This module provides utilities for working with Bible data,
including comparing translations, finding differences, and
generating statistical insights about the translations.
"""

import json
import pandas as pd
from typing import Dict, List, Tuple, Any

from scripts.preprocessing.structure.bible_structure import (
    BIBLE_BOOKS,
    get_book_by_name,
    kikuyu_to_english_book_name,
)


def load_translation_data(csv_path: str) -> pd.DataFrame:
    """
    Load Bible translation data from a CSV file.

    Args:
        csv_path: Path to CSV file with columns [Reference, Kikuyu, English]

    Returns:
        DataFrame with translation data
    """
    df = pd.DataFrame()
    try:
        df = pd.read_csv(csv_path)
        required_cols = ["Reference", "Kikuyu", "English"]
        for col in required_cols:
            if col not in df.columns:
                print(f"Error: {csv_path} is missing required column: {col}")
                return pd.DataFrame()
    except Exception as e:
        print(f"Error loading translation data: {e}")

    return df


def parse_reference(reference: str) -> Tuple[str, int, int]:
    """
    Parse a Bible reference into book, chapter, and verse.

    Args:
        reference: Reference string in format "Book Chapter:Verse"

    Returns:
        Tuple of (book_name, chapter_no, verse_no)
    """
    try:
        # Split by space for the book name and chapter:verse
        parts = reference.split(" ")

        # Handle multi-word book names
        if len(parts) > 2:
            book_name = " ".join(parts[:-1])
            chapter_verse = parts[-1]
        else:
            book_name = parts[0]
            chapter_verse = parts[1]

        # Split chapter and verse
        chapter, verse = chapter_verse.split(":")

        return book_name, int(chapter), int(verse)
    except Exception as e:
        print(f"Error parsing reference '{reference}': {e}")
        return "", 0, 0


def get_stats_by_book(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate statistics about verse counts by book.

    Args:
        df: DataFrame with Reference, Kikuyu, English columns

    Returns:
        DataFrame with verse count statistics by book
    """
    stats = []

    # Extract book names from references
    df["book_name"] = df["Reference"].apply(lambda x: parse_reference(x)[0])

    # Group by book and count verses
    book_counts = df.groupby("book_name").size().reset_index(name="verse_count")

    # Get total verses for each book (from structure)
    for _, row in book_counts.iterrows():
        kikuyu_book = row["book_name"]
        english_book = kikuyu_to_english_book_name(kikuyu_book)

        book_info = get_book_by_name(english_book) if english_book else None

        if book_info:
            total_verses = sum(
                chapter["num_verses"] for chapter in book_info["chapters"]
            )
            coverage = row["verse_count"] / total_verses * 100

            stats.append(
                {
                    "kikuyu_name": kikuyu_book,
                    "english_name": english_book,
                    "verses_available": row["verse_count"],
                    "total_verses": total_verses,
                    "coverage_percent": coverage,
                }
            )

    stats_df = pd.DataFrame(stats)
    return stats_df.sort_values("coverage_percent", ascending=False)


def compare_translations(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compare Kikuyu and English translations.

    Args:
        df: DataFrame with Reference, Kikuyu, English columns

    Returns:
        Dictionary with comparison statistics
    """
    stats = {}

    # Basic statistics
    stats["total_verse_pairs"] = len(df)

    # Length statistics
    df["kikuyu_len"] = df["Kikuyu"].str.len()
    df["english_len"] = df["English"].str.len()
    df["len_ratio"] = df["kikuyu_len"] / df["english_len"]

    stats["avg_kikuyu_len"] = df["kikuyu_len"].mean()
    stats["avg_english_len"] = df["english_len"].mean()
    stats["avg_len_ratio"] = df["len_ratio"].mean()

    # Word count statistics
    df["kikuyu_words"] = df["Kikuyu"].str.split().str.len()
    df["english_words"] = df["English"].str.split().str.len()
    df["word_ratio"] = df["kikuyu_words"] / df["english_words"]

    stats["avg_kikuyu_words"] = df["kikuyu_words"].mean()
    stats["avg_english_words"] = df["english_words"].mean()
    stats["avg_word_ratio"] = df["word_ratio"].mean()

    # By book statistics
    book_stats = get_stats_by_book(df)
    stats["book_coverage"] = book_stats.to_dict("records")

    # Coverage statistics
    stats["total_books"] = len(BIBLE_BOOKS)
    stats["books_with_data"] = book_stats.shape[0]
    stats["book_coverage_percent"] = (
        stats["books_with_data"] / stats["total_books"] * 100
    )

    return stats


def get_missing_books(df: pd.DataFrame) -> List[str]:
    """
    Get a list of books missing from the dataset.

    Args:
        df: DataFrame with Reference, Kikuyu, English columns

    Returns:
        List of missing book names (English)
    """
    # Extract book names from references
    df["book_name"] = df["Reference"].apply(lambda x: parse_reference(x)[0])

    # Get present Kikuyu book names
    present_kikuyu_books = set(df["book_name"].unique())

    # Convert to English names
    present_english_books = set()
    for kikuyu_book in present_kikuyu_books:
        english_book = kikuyu_to_english_book_name(kikuyu_book)
        if english_book:
            present_english_books.add(english_book)

    # Get all books from structure
    all_english_books = set(book["book_name"] for book in BIBLE_BOOKS)

    # Find missing books
    missing_books = all_english_books - present_english_books

    return sorted(list(missing_books))


def export_stats_to_json(stats: Dict[str, Any], output_path: str) -> None:
    """
    Export statistics to a JSON file.

    Args:
        stats: Dictionary with statistics
        output_path: Path to save the JSON file
    """
    try:
        # Convert DataFrame in book_coverage to list of dicts
        if "book_coverage" in stats and isinstance(
            stats["book_coverage"], pd.DataFrame
        ):
            stats["book_coverage"] = stats["book_coverage"].to_dict("records")

        # Convert any float values to rounded strings for readability
        for key, value in stats.items():
            if isinstance(value, float):
                stats[key] = round(value, 2)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        print(f"Exported statistics to {output_path}")

    except Exception as e:
        print(f"Error exporting statistics: {e}")


def find_candidate_verses(
    source_df: pd.DataFrame, target_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Find verses that exist in source but not in target dataset.
    Useful for identifying verses to add to a training dataset.

    Args:
        source_df: Source DataFrame with References present
        target_df: Target DataFrame to check against

    Returns:
        DataFrame with verses present in source but not in target
    """
    # Get references from both datasets
    source_refs = set(source_df["Reference"])
    target_refs = set(target_df["Reference"])

    # Find references present in source but not in target
    missing_refs = source_refs - target_refs

    # Filter source DataFrame to only those references
    return source_df[source_df["Reference"].isin(missing_refs)]
