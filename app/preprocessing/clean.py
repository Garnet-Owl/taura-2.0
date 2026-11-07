"""Removes footnote marks and Psalms layout leftovers from extracted verse text."""

import re

_FOOTNOTE_MARKS = re.compile(r"[*†‡]")
_LEADING_VERSE_NUMBER = re.compile(r"^\d{1,3}\s+(?=[^\W\d])")
_PSALMS_BOOK_MARKER = re.compile(r"\s+BOOK \d+(?:\s+\d{1,3}\s+A\b.*)?$")
_PSALMS_NEXT_TITLE = re.compile(
    r"\s+\d{1,3}\s+(?:For the Chief Musician|A (?:Psalm|Song|contemplation|poem|prayer)|Thaburi)\b.*$"
)


def clean_sentence(text: str) -> str:
    """Drops footnote marks, a stray leading verse number and glued Psalms headings."""
    text = _FOOTNOTE_MARKS.sub("", text)
    text = " ".join(text.split())
    text = _LEADING_VERSE_NUMBER.sub("", text)
    text = _PSALMS_BOOK_MARKER.sub("", text)
    return _PSALMS_NEXT_TITLE.sub("", text).strip()
