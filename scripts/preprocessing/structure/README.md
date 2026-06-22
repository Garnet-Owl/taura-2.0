# Bible Structure Module for Taura

This module provides the structure for the Bible in both English and Kikuyu, to be used for the Taura translation project. It consists of a comprehensive data structure that includes all 66 books of the Bible, with their chapter counts and verse counts.

## Key Features

1. Complete Bible structure with all 66 books
2. Mapping between English and Kikuyu book names
3. Utilities for validating Bible references
4. Tools for finding missing verses and books

## Files

- `bible_books.json`: The complete Bible structure in JSON format
- `bible_structure.py`: Python module generated from the JSON file
- `generate_complete_structure.py`: Script to regenerate the Python module from JSON
- `__init__.py`: Package initialization file

## Usage

### Generating the Structure

To regenerate the Bible structure Python module from the JSON file:

```bash
python -m src.data.preprocessing.bible_cli generate-structure
```

### Accessing Book Information

```python
from src.data.preprocessing.structure.bible_structure import (
    get_book_by_name,
    get_book_by_kikuyu_name,
    kikuyu_to_english_book_name,
    english_to_kikuyu_book_name
)

# Get book by English name
genesis = get_book_by_name("Genesis")
# {'book_name': 'Genesis', 'kikuyu_name': 'Kĩambĩrĩria', 'num_chapters': 50, 'chapters': [...]}

# Get book by Kikuyu name
genesis = get_book_by_kikuyu_name("Kĩambĩrĩria")
# {'book_name': 'Genesis', 'kikuyu_name': 'Kĩambĩrĩria', 'num_chapters': 50, 'chapters': [...]}

# Convert between English and Kikuyu book names
kikuyu_name = english_to_kikuyu_book_name("Genesis")  # Returns "Kĩambĩrĩria"
english_name = kikuyu_to_english_book_name("Kĩambĩrĩria")  # Returns "Genesis"
```

### Validating References

```python
from src.data.preprocessing.structure.bible_structure import is_valid_reference

# Check if a reference is valid
is_valid = is_valid_reference("Genesis", 1, 31)  # Returns True
is_valid = is_valid_reference("Genesis", 1, 32)  # Returns False (Genesis 1 has 31 verses)
```

### Additional Utilities

The module provides several other utilities for working with Bible data:

- `get_verse_count(book_name, chapter_no)`: Get the number of verses in a chapter
- `get_verse_id(book_name, chapter_no, verse_no)`: Generate a unique ID for a verse
- `get_all_books()`: Get a list of all book names (English)
- `get_all_kikuyu_books()`: Get a list of all Kikuyu book names
- `get_all_chapter_numbers(book_name)`: Get all chapter numbers for a book
- `get_all_verse_numbers(book_name, chapter_no)`: Get all verse numbers for a chapter
- `get_missing_verses(parsed_verses, book_name)`: Get missing verses for a book
- `get_extra_verses(parsed_verses, book_name)`: Get extra verses that shouldn't exist

## Data Structure

Each book in the Bible structure has the following format:

```python
{
    "book_name": "Genesis",  # English name
    "kikuyu_name": "Kĩambĩrĩria",  # Kikuyu name
    "num_chapters": 50,  # Number of chapters
    "chapters": [
        {"chapter_no": 1, "num_verses": 31},
        {"chapter_no": 2, "num_verses": 25},
        # ...
    ]
}
```

This structure serves as the source of truth for the Bible's organization and is used for validation throughout the Taura project.
