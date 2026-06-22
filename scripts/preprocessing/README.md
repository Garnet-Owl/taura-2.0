# Taura Project - Bible Preprocessing Utilities

This directory contains utilities for processing Bible data for the Taura Kikuyu-English translation project.

## Features

- Complete Bible structure with all 66 books (from Genesis to Revelation)
- Kikuyu and English book name mapping
- Bible reference parsing and validation
- Translation comparison and analysis tools
- CLI for working with Bible datasets

## Structure

- `bible_parser.py` - Bible PDF parsing utilities
- `bible_utils.py` - Utilities for working with Bible data
- `bible_cli.py` - Command-line interface for Bible utilities
- `generate_all_bible_structure.py` - Generate complete Bible structure
- `structure/` - Bible structure data and utilities
  - `bible_books.json` - Complete Bible structure in JSON format
  - `bible_structure.py` - Generated Python module with Bible structure
  - `generate_complete_structure.py` - Utility to generate Bible structure

## Usage

### Generating Complete Bible Structure

```bash
python -m src.data.preprocessing.generate_all_bible_structure
```

This will create a complete `bible_structure.py` with all 66 books, including Kikuyu names.

### Bible CLI

The Bible CLI provides several commands for working with Bible data:

```bash
# Generate complete Bible structure
python -m src.data.preprocessing.bible_cli generate-structure

# Analyze Bible translation data
python -m src.data.preprocessing.bible_cli analyze --input data/processed/bible_parallel.csv --output data/stats/bible_stats.json

# Compare two Bible datasets
python -m src.data.preprocessing.bible_cli compare --source data/source.csv --target data/target.csv --output data/missing.csv

# List books missing from the dataset
python -m src.data.preprocessing.bible_cli missing-books --input data/processed/bible_parallel.csv

# Get verse statistics by book
python -m src.data.preprocessing.bible_cli stats-by-book --input data/processed/bible_parallel.csv --output data/stats/book_stats.csv
```

### Bible Parsing

The Bible parser can extract and align verses from Kikuyu and English Bible PDFs:

```python
from src.data.preprocessing.bible_parser import process_bible_texts

# Process Bible texts
df = process_bible_texts(
    "data/kikuyu_bible.pdf",
    "data/english_bible.pdf",
    max_examples=None
)

# Save the dataset
df.to_csv("data/processed/bible_parallel.csv", index=False)
```

### Bible Utilities

The Bible utilities provide functions for working with Bible data:

```python
from src.data.preprocessing.bible_utils import (
    load_translation_data,
    compare_translations,
    get_stats_by_book,
    get_missing_books
)

# Load Bible data
df = load_translation_data("data/processed/bible_parallel.csv")

# Compare translations
stats = compare_translations(df)

# Get statistics by book
book_stats = get_stats_by_book(df)

# Get missing books
missing_books = get_missing_books(df)
```

## Testing

The Bible utilities and CLI are tested using pytest:

```bash
# Run all tests
pytest tests/data

# Run specific test file
pytest tests/data/test_bible_utils.py
```
