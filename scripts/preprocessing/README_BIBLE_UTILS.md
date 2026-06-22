# Bible Utilities for Taura

This module provides utilities for working with Bible data in the Taura translation project. It includes tools for analyzing, comparing, and processing Bible translations between Kikuyu and English.

## Features

1. Bible structure management
2. Translation analysis and comparison
3. Statistics generation
4. Missing book/verse identification
5. Dataset creation and manipulation

## CLI Commands

The Bible utilities include a command-line interface (CLI) for performing common tasks:

### Generate Bible Structure

Generate the complete Bible structure Python module from the JSON file:

```bash
python -m src.data.preprocessing.bible_cli generate-structure
```

### Analyze Bible Translation Data

Analyze a Bible translation dataset to get statistics:

```bash
python -m src.data.preprocessing.bible_cli analyze --input <csv_file> [--output <json_file>]
```

Example output:
```
Loaded 2000 verse pairs from bible_parallel.csv

Summary Statistics:
Total verse pairs: 2000
Books with data: 15 out of 66 (22.73%)
Average length ratio (Kikuyu/English): 1.23
Average word ratio (Kikuyu/English): 0.87
```

### Compare Two Datasets

Compare two Bible translation datasets to find differences:

```bash
python -m src.data.preprocessing.bible_cli compare --source <source_csv> --target <target_csv> [--output <output_csv>]
```

Example output:
```
Loaded 2000 verse pairs from source.csv
Loaded 1800 verse pairs from target.csv
Found 200 verse pairs present in source but not in target
Exported missing verses to missing.csv
```

### List Missing Books

List books that are missing from a Bible translation dataset:

```bash
python -m src.data.preprocessing.bible_cli missing-books --input <csv_file>
```

Example output:
```
Missing Books (51 out of 66):
  - Leviticus
  - Numbers
  - Deuteronomy
  ...
```

### Get Statistics by Book

Get verse coverage statistics by book:

```bash
python -m src.data.preprocessing.bible_cli stats-by-book --input <csv_file> [--output <output_csv>]
```

Example output:
```
Verse Coverage by Book:
kikuyu_name    english_name  verses_available  total_verses  coverage_percent
Kĩambĩrĩria    Genesis                   600          1533             39.14
Mathayo        Matthew                   550          1071             51.35
Johana         John                      350           879             39.82
...
```

## Python API

The Bible utilities can also be used programmatically in Python:

```python
from src.data.preprocessing.bible_utils import (
    load_translation_data,
    compare_translations,
    get_stats_by_book,
    get_missing_books,
    parse_reference
)

# Load Bible translation data
df = load_translation_data('bible_parallel.csv')

# Get statistics about the translations
stats = compare_translations(df)

# Get statistics by book
book_stats = get_stats_by_book(df)

# Get missing books
missing_books = get_missing_books(df)

# Parse a Bible reference
book, chapter, verse = parse_reference('Kĩambĩrĩria 1:1')
```

## Bible Structure

The Bible utilities rely on a comprehensive Bible structure that includes:

- All 66 books of the Bible
- Kikuyu and English book names
- Chapter counts for each book
- Verse counts for each chapter

This structure serves as the source of truth for Bible organization and is used for validation throughout the Taura project.

For more information on the Bible structure, see the [Bible Structure README](structure/README.md).
