"""
Command-line interface for Bible utilities.

This script provides a CLI for working with Bible data, including:
- Generating Bible structure from JSON
- Analyzing and comparing translations
- Validating Bible structure data
"""

import argparse
import sys


from .structure.generate_complete_structure import generate_bible_structure
from .bible_utils import (
    load_translation_data,
    compare_translations,
    get_stats_by_book,
    get_missing_books,
    export_stats_to_json,
)


def main():
    """Main entry point for the Bible CLI."""
    parser = argparse.ArgumentParser(description="Taura Bible utilities CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Generate structure command
    generate_parser = subparsers.add_parser(
        "generate-structure", help="Generate Bible structure from JSON"
    )
    generate_parser

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze Bible translation data"
    )
    analyze_parser.add_argument(
        "--input", required=True, help="Input CSV file with Bible translations"
    )
    analyze_parser.add_argument("--output", help="Output JSON file for statistics")

    # Compare command
    compare_parser = subparsers.add_parser(
        "compare", help="Compare two Bible translation datasets"
    )
    compare_parser.add_argument(
        "--source", required=True, help="Source CSV file with Bible translations"
    )
    compare_parser.add_argument(
        "--target", required=True, help="Target CSV file to compare against"
    )
    compare_parser.add_argument("--output", help="Output CSV file for missing verses")

    # Missing books command
    missing_parser = subparsers.add_parser(
        "missing-books", help="List books missing from the dataset"
    )
    missing_parser.add_argument(
        "--input", required=True, help="Input CSV file with Bible translations"
    )

    # Stats by book command
    stats_parser = subparsers.add_parser(
        "stats-by-book", help="Get verse statistics by book"
    )
    stats_parser.add_argument(
        "--input", required=True, help="Input CSV file with Bible translations"
    )
    stats_parser.add_argument("--output", help="Output CSV file for book statistics")

    args = parser.parse_args()

    if args.command == "generate-structure":
        success = generate_bible_structure()
        if success:
            print("Successfully generated Bible structure")
        else:
            print("Failed to generate Bible structure")
            return 1

    elif args.command == "analyze":
        df = load_translation_data(args.input)
        if df.empty:
            print(f"Failed to load data from {args.input}")
            return 1

        print(f"Loaded {len(df)} verse pairs from {args.input}")
        stats = compare_translations(df)

        # Print summary statistics
        print("\nSummary Statistics:")
        print(f"Total verse pairs: {stats['total_verse_pairs']}")
        print(
            f"Books with data: {stats['books_with_data']} out of {stats['total_books']} ({stats['book_coverage_percent']:.2f}%)"
        )
        print(f"Average length ratio (Kikuyu/English): {stats['avg_len_ratio']:.2f}")
        print(f"Average word ratio (Kikuyu/English): {stats['avg_word_ratio']:.2f}")

        # Export statistics to JSON if requested
        if args.output:
            export_stats_to_json(stats, args.output)

    elif args.command == "compare":
        source_df = load_translation_data(args.source)
        target_df = load_translation_data(args.target)

        if source_df.empty:
            print(f"Failed to load source data from {args.source}")
            return 1

        if target_df.empty:
            print(f"Failed to load target data from {args.target}")
            return 1

        print(f"Loaded {len(source_df)} verse pairs from {args.source}")
        print(f"Loaded {len(target_df)} verse pairs from {args.target}")

        # Find verses present in source but not in target
        missing_df = source_df[~source_df["Reference"].isin(target_df["Reference"])]

        print(
            f"Found {len(missing_df)} verse pairs present in source but not in target"
        )

        # Export missing verses to CSV if requested
        if args.output and not missing_df.empty:
            missing_df.to_csv(args.output, index=False)
            print(f"Exported missing verses to {args.output}")

    elif args.command == "missing-books":
        df = load_translation_data(args.input)
        if df.empty:
            print(f"Failed to load data from {args.input}")
            return 1

        missing_books = get_missing_books(df)

        print(f"\nMissing Books ({len(missing_books)} out of 66):")
        for book in missing_books:
            print(f"  - {book}")

    elif args.command == "stats-by-book":
        df = load_translation_data(args.input)
        if df.empty:
            print(f"Failed to load data from {args.input}")
            return 1

        book_stats = get_stats_by_book(df)

        # Print book coverage statistics
        print("\nVerse Coverage by Book:")
        print(book_stats.to_string(index=False))

        # Export book statistics to CSV if requested
        if args.output:
            book_stats.to_csv(args.output, index=False)
            print(f"Exported book statistics to {args.output}")

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
