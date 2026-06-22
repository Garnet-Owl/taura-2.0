"""
Bible structure module.

This module provides a source of truth for the structure of the Bible,
including book names, chapter counts, and verse counts for each chapter.
This data will be used for validating and organizing the parsed Bible verses.
"""

from typing import Dict, List, Optional, Tuple

# Bible structure data
# This structure contains information about each book in the Bible,
# including the number of chapters and the number of verses in each chapter.
BIBLE_BOOKS = [
    {
        "book_name": "Genesis",
        "kikuyu_name": "Kĩambĩrĩria",
        "num_chapters": 50,
        "chapters": [
            {"chapter_no": 1, "num_verses": 31},
            {"chapter_no": 2, "num_verses": 25},
            {"chapter_no": 3, "num_verses": 24},
            {"chapter_no": 4, "num_verses": 26},
            {"chapter_no": 5, "num_verses": 32},
            {"chapter_no": 6, "num_verses": 22},
            {"chapter_no": 7, "num_verses": 24},
            {"chapter_no": 8, "num_verses": 22},
            {"chapter_no": 9, "num_verses": 29},
            {"chapter_no": 10, "num_verses": 32},
            {"chapter_no": 11, "num_verses": 32},
            {"chapter_no": 12, "num_verses": 20},
            {"chapter_no": 13, "num_verses": 18},
            {"chapter_no": 14, "num_verses": 24},
            {"chapter_no": 15, "num_verses": 21},
            {"chapter_no": 16, "num_verses": 16},
            {"chapter_no": 17, "num_verses": 27},
            {"chapter_no": 18, "num_verses": 33},
            {"chapter_no": 19, "num_verses": 38},
            {"chapter_no": 20, "num_verses": 18},
            {"chapter_no": 21, "num_verses": 34},
            {"chapter_no": 22, "num_verses": 24},
            {"chapter_no": 23, "num_verses": 20},
            {"chapter_no": 24, "num_verses": 67},
            {"chapter_no": 25, "num_verses": 34},
            {"chapter_no": 26, "num_verses": 35},
            {"chapter_no": 27, "num_verses": 46},
            {"chapter_no": 28, "num_verses": 22},
            {"chapter_no": 29, "num_verses": 35},
            {"chapter_no": 30, "num_verses": 43},
            {"chapter_no": 31, "num_verses": 55},
            {"chapter_no": 32, "num_verses": 32},
            {"chapter_no": 33, "num_verses": 20},
            {"chapter_no": 34, "num_verses": 31},
            {"chapter_no": 35, "num_verses": 29},
            {"chapter_no": 36, "num_verses": 43},
            {"chapter_no": 37, "num_verses": 36},
            {"chapter_no": 38, "num_verses": 30},
            {"chapter_no": 39, "num_verses": 23},
            {"chapter_no": 40, "num_verses": 23},
            {"chapter_no": 41, "num_verses": 57},
            {"chapter_no": 42, "num_verses": 38},
            {"chapter_no": 43, "num_verses": 34},
            {"chapter_no": 44, "num_verses": 34},
            {"chapter_no": 45, "num_verses": 28},
            {"chapter_no": 46, "num_verses": 34},
            {"chapter_no": 47, "num_verses": 31},
            {"chapter_no": 48, "num_verses": 22},
            {"chapter_no": 49, "num_verses": 33},
            {"chapter_no": 50, "num_verses": 26},
        ],
    },
    {
        "book_name": "Exodus",
        "kikuyu_name": "Woima",
        "num_chapters": 40,
        "chapters": [
            {"chapter_no": 1, "num_verses": 22},
            {"chapter_no": 2, "num_verses": 25},
            {"chapter_no": 3, "num_verses": 22},
            {"chapter_no": 4, "num_verses": 31},
            {"chapter_no": 5, "num_verses": 23},
            {"chapter_no": 6, "num_verses": 30},
            {"chapter_no": 7, "num_verses": 25},
            {"chapter_no": 8, "num_verses": 32},
            {"chapter_no": 9, "num_verses": 35},
            {"chapter_no": 10, "num_verses": 29},
            {"chapter_no": 11, "num_verses": 10},
            {"chapter_no": 12, "num_verses": 51},
            {"chapter_no": 13, "num_verses": 22},
            {"chapter_no": 14, "num_verses": 31},
            {"chapter_no": 15, "num_verses": 27},
            {"chapter_no": 16, "num_verses": 36},
            {"chapter_no": 17, "num_verses": 16},
            {"chapter_no": 18, "num_verses": 27},
            {"chapter_no": 19, "num_verses": 25},
            {"chapter_no": 20, "num_verses": 26},
            {"chapter_no": 21, "num_verses": 36},
            {"chapter_no": 22, "num_verses": 31},
            {"chapter_no": 23, "num_verses": 33},
            {"chapter_no": 24, "num_verses": 18},
            {"chapter_no": 25, "num_verses": 40},
            {"chapter_no": 26, "num_verses": 37},
            {"chapter_no": 27, "num_verses": 21},
            {"chapter_no": 28, "num_verses": 43},
            {"chapter_no": 29, "num_verses": 46},
            {"chapter_no": 30, "num_verses": 38},
            {"chapter_no": 31, "num_verses": 18},
            {"chapter_no": 32, "num_verses": 35},
            {"chapter_no": 33, "num_verses": 23},
            {"chapter_no": 34, "num_verses": 35},
            {"chapter_no": 35, "num_verses": 35},
            {"chapter_no": 36, "num_verses": 38},
            {"chapter_no": 37, "num_verses": 29},
            {"chapter_no": 38, "num_verses": 31},
            {"chapter_no": 39, "num_verses": 43},
            {"chapter_no": 40, "num_verses": 38},
        ],
    },
    {
        "book_name": "Leviticus",
        "kikuyu_name": "Alawii",
        "num_chapters": 27,
        "chapters": [
            {"chapter_no": 1, "num_verses": 17},
            {"chapter_no": 2, "num_verses": 16},
            {"chapter_no": 3, "num_verses": 17},
            {"chapter_no": 4, "num_verses": 35},
            {"chapter_no": 5, "num_verses": 19},
            {"chapter_no": 6, "num_verses": 30},
            {"chapter_no": 7, "num_verses": 38},
            {"chapter_no": 8, "num_verses": 36},
            {"chapter_no": 9, "num_verses": 24},
            {"chapter_no": 10, "num_verses": 20},
            {"chapter_no": 11, "num_verses": 47},
            {"chapter_no": 12, "num_verses": 8},
            {"chapter_no": 13, "num_verses": 59},
            {"chapter_no": 14, "num_verses": 57},
            {"chapter_no": 15, "num_verses": 33},
            {"chapter_no": 16, "num_verses": 34},
            {"chapter_no": 17, "num_verses": 16},
            {"chapter_no": 18, "num_verses": 30},
            {"chapter_no": 19, "num_verses": 37},
            {"chapter_no": 20, "num_verses": 27},
            {"chapter_no": 21, "num_verses": 24},
            {"chapter_no": 22, "num_verses": 33},
            {"chapter_no": 23, "num_verses": 44},
            {"chapter_no": 24, "num_verses": 23},
            {"chapter_no": 25, "num_verses": 55},
            {"chapter_no": 26, "num_verses": 46},
            {"chapter_no": 27, "num_verses": 34},
        ],
    },
    {
        "book_name": "Numbers",
        "kikuyu_name": "Ndari",
        "num_chapters": 36,
        "chapters": [
            {"chapter_no": 1, "num_verses": 54},
            {"chapter_no": 2, "num_verses": 34},
            {"chapter_no": 3, "num_verses": 51},
            {"chapter_no": 4, "num_verses": 49},
            {"chapter_no": 5, "num_verses": 31},
            {"chapter_no": 6, "num_verses": 27},
            {"chapter_no": 7, "num_verses": 89},
            {"chapter_no": 8, "num_verses": 26},
            {"chapter_no": 9, "num_verses": 23},
            {"chapter_no": 10, "num_verses": 36},
            {"chapter_no": 11, "num_verses": 35},
            {"chapter_no": 12, "num_verses": 16},
            {"chapter_no": 13, "num_verses": 33},
            {"chapter_no": 14, "num_verses": 45},
            {"chapter_no": 15, "num_verses": 41},
            {"chapter_no": 16, "num_verses": 50},
            {"chapter_no": 17, "num_verses": 13},
            {"chapter_no": 18, "num_verses": 32},
            {"chapter_no": 19, "num_verses": 22},
            {"chapter_no": 20, "num_verses": 29},
            {"chapter_no": 21, "num_verses": 35},
            {"chapter_no": 22, "num_verses": 41},
            {"chapter_no": 23, "num_verses": 30},
            {"chapter_no": 24, "num_verses": 25},
            {"chapter_no": 25, "num_verses": 18},
            {"chapter_no": 26, "num_verses": 65},
            {"chapter_no": 27, "num_verses": 23},
            {"chapter_no": 28, "num_verses": 31},
            {"chapter_no": 29, "num_verses": 40},
            {"chapter_no": 30, "num_verses": 16},
            {"chapter_no": 31, "num_verses": 54},
            {"chapter_no": 32, "num_verses": 42},
            {"chapter_no": 33, "num_verses": 56},
            {"chapter_no": 34, "num_verses": 29},
            {"chapter_no": 35, "num_verses": 34},
            {"chapter_no": 36, "num_verses": 13},
        ],
    },
    {
        "book_name": "Deuteronomy",
        "kikuyu_name": "Gũcookerithia Watho",
        "num_chapters": 34,
        "chapters": [
            {"chapter_no": 1, "num_verses": 46},
            {"chapter_no": 2, "num_verses": 37},
            {"chapter_no": 3, "num_verses": 29},
            {"chapter_no": 4, "num_verses": 49},
            {"chapter_no": 5, "num_verses": 33},
            {"chapter_no": 6, "num_verses": 25},
            {"chapter_no": 7, "num_verses": 26},
            {"chapter_no": 8, "num_verses": 20},
            {"chapter_no": 9, "num_verses": 29},
            {"chapter_no": 10, "num_verses": 22},
            {"chapter_no": 11, "num_verses": 32},
            {"chapter_no": 12, "num_verses": 32},
            {"chapter_no": 13, "num_verses": 18},
            {"chapter_no": 14, "num_verses": 29},
            {"chapter_no": 15, "num_verses": 23},
            {"chapter_no": 16, "num_verses": 22},
            {"chapter_no": 17, "num_verses": 20},
            {"chapter_no": 18, "num_verses": 22},
            {"chapter_no": 19, "num_verses": 21},
            {"chapter_no": 20, "num_verses": 20},
            {"chapter_no": 21, "num_verses": 23},
            {"chapter_no": 22, "num_verses": 30},
            {"chapter_no": 23, "num_verses": 25},
            {"chapter_no": 24, "num_verses": 22},
            {"chapter_no": 25, "num_verses": 19},
            {"chapter_no": 26, "num_verses": 19},
            {"chapter_no": 27, "num_verses": 26},
            {"chapter_no": 28, "num_verses": 68},
            {"chapter_no": 29, "num_verses": 29},
            {"chapter_no": 30, "num_verses": 20},
            {"chapter_no": 31, "num_verses": 30},
            {"chapter_no": 32, "num_verses": 52},
            {"chapter_no": 33, "num_verses": 29},
            {"chapter_no": 34, "num_verses": 12},
        ],
    },
    {
        "book_name": "Joshua",
        "kikuyu_name": "Joshua",
        "num_chapters": 24,
        "chapters": [
            {"chapter_no": 1, "num_verses": 18},
            {"chapter_no": 2, "num_verses": 24},
            {"chapter_no": 3, "num_verses": 17},
            {"chapter_no": 4, "num_verses": 24},
            {"chapter_no": 5, "num_verses": 15},
            {"chapter_no": 6, "num_verses": 27},
            {"chapter_no": 7, "num_verses": 26},
            {"chapter_no": 8, "num_verses": 35},
            {"chapter_no": 9, "num_verses": 27},
            {"chapter_no": 10, "num_verses": 43},
            {"chapter_no": 11, "num_verses": 23},
            {"chapter_no": 12, "num_verses": 24},
            {"chapter_no": 13, "num_verses": 33},
            {"chapter_no": 14, "num_verses": 15},
            {"chapter_no": 15, "num_verses": 63},
            {"chapter_no": 16, "num_verses": 10},
            {"chapter_no": 17, "num_verses": 18},
            {"chapter_no": 18, "num_verses": 28},
            {"chapter_no": 19, "num_verses": 51},
            {"chapter_no": 20, "num_verses": 9},
            {"chapter_no": 21, "num_verses": 45},
            {"chapter_no": 22, "num_verses": 34},
            {"chapter_no": 23, "num_verses": 16},
            {"chapter_no": 24, "num_verses": 33},
        ],
    },
    {
        "book_name": "Judges",
        "kikuyu_name": "Atiirĩrĩri",
        "num_chapters": 21,
        "chapters": [
            {"chapter_no": 1, "num_verses": 36},
            {"chapter_no": 2, "num_verses": 23},
            {"chapter_no": 3, "num_verses": 31},
            {"chapter_no": 4, "num_verses": 24},
            {"chapter_no": 5, "num_verses": 31},
            {"chapter_no": 6, "num_verses": 40},
            {"chapter_no": 7, "num_verses": 25},
            {"chapter_no": 8, "num_verses": 35},
            {"chapter_no": 9, "num_verses": 57},
            {"chapter_no": 10, "num_verses": 18},
            {"chapter_no": 11, "num_verses": 40},
            {"chapter_no": 12, "num_verses": 15},
            {"chapter_no": 13, "num_verses": 25},
            {"chapter_no": 14, "num_verses": 20},
            {"chapter_no": 15, "num_verses": 20},
            {"chapter_no": 16, "num_verses": 31},
            {"chapter_no": 17, "num_verses": 13},
            {"chapter_no": 18, "num_verses": 31},
            {"chapter_no": 19, "num_verses": 30},
            {"chapter_no": 20, "num_verses": 48},
            {"chapter_no": 21, "num_verses": 25},
        ],
    },
    {
        "book_name": "Ruth",
        "kikuyu_name": "Ruthu",
        "num_chapters": 4,
        "chapters": [
            {"chapter_no": 1, "num_verses": 22},
            {"chapter_no": 2, "num_verses": 23},
            {"chapter_no": 3, "num_verses": 18},
            {"chapter_no": 4, "num_verses": 22},
        ],
    },
    {
        "book_name": "1 Samuel",
        "kikuyu_name": "1 Samũeli",
        "num_chapters": 31,
        "chapters": [
            {"chapter_no": 1, "num_verses": 28},
            {"chapter_no": 2, "num_verses": 36},
            {"chapter_no": 3, "num_verses": 21},
            {"chapter_no": 4, "num_verses": 22},
            {"chapter_no": 5, "num_verses": 12},
            {"chapter_no": 6, "num_verses": 21},
            {"chapter_no": 7, "num_verses": 17},
            {"chapter_no": 8, "num_verses": 22},
            {"chapter_no": 9, "num_verses": 27},
            {"chapter_no": 10, "num_verses": 27},
            {"chapter_no": 11, "num_verses": 15},
            {"chapter_no": 12, "num_verses": 25},
            {"chapter_no": 13, "num_verses": 23},
            {"chapter_no": 14, "num_verses": 52},
            {"chapter_no": 15, "num_verses": 35},
            {"chapter_no": 16, "num_verses": 23},
            {"chapter_no": 17, "num_verses": 58},
            {"chapter_no": 18, "num_verses": 30},
            {"chapter_no": 19, "num_verses": 24},
            {"chapter_no": 20, "num_verses": 42},
            {"chapter_no": 21, "num_verses": 15},
            {"chapter_no": 22, "num_verses": 23},
            {"chapter_no": 23, "num_verses": 29},
            {"chapter_no": 24, "num_verses": 22},
            {"chapter_no": 25, "num_verses": 44},
            {"chapter_no": 26, "num_verses": 25},
            {"chapter_no": 27, "num_verses": 12},
            {"chapter_no": 28, "num_verses": 25},
            {"chapter_no": 29, "num_verses": 11},
            {"chapter_no": 30, "num_verses": 31},
            {"chapter_no": 31, "num_verses": 13},
        ],
    },
    {
        "book_name": "2 Samuel",
        "kikuyu_name": "2 Samũeli",
        "num_chapters": 24,
        "chapters": [
            {"chapter_no": 1, "num_verses": 27},
            {"chapter_no": 2, "num_verses": 32},
            {"chapter_no": 3, "num_verses": 39},
            {"chapter_no": 4, "num_verses": 12},
            {"chapter_no": 5, "num_verses": 25},
            {"chapter_no": 6, "num_verses": 23},
            {"chapter_no": 7, "num_verses": 29},
            {"chapter_no": 8, "num_verses": 18},
            {"chapter_no": 9, "num_verses": 13},
            {"chapter_no": 10, "num_verses": 19},
            {"chapter_no": 11, "num_verses": 27},
            {"chapter_no": 12, "num_verses": 31},
            {"chapter_no": 13, "num_verses": 39},
            {"chapter_no": 14, "num_verses": 33},
            {"chapter_no": 15, "num_verses": 37},
            {"chapter_no": 16, "num_verses": 23},
            {"chapter_no": 17, "num_verses": 29},
            {"chapter_no": 18, "num_verses": 33},
            {"chapter_no": 19, "num_verses": 43},
            {"chapter_no": 20, "num_verses": 26},
            {"chapter_no": 21, "num_verses": 22},
            {"chapter_no": 22, "num_verses": 51},
            {"chapter_no": 23, "num_verses": 39},
            {"chapter_no": 24, "num_verses": 25},
        ],
    },
    {
        "book_name": "1 Kings",
        "kikuyu_name": "1 Athamaki",
        "num_chapters": 22,
        "chapters": [
            {"chapter_no": 1, "num_verses": 53},
            {"chapter_no": 2, "num_verses": 46},
            {"chapter_no": 3, "num_verses": 28},
            {"chapter_no": 4, "num_verses": 34},
            {"chapter_no": 5, "num_verses": 18},
            {"chapter_no": 6, "num_verses": 38},
            {"chapter_no": 7, "num_verses": 51},
            {"chapter_no": 8, "num_verses": 66},
            {"chapter_no": 9, "num_verses": 28},
            {"chapter_no": 10, "num_verses": 29},
            {"chapter_no": 11, "num_verses": 43},
            {"chapter_no": 12, "num_verses": 33},
            {"chapter_no": 13, "num_verses": 34},
            {"chapter_no": 14, "num_verses": 31},
            {"chapter_no": 15, "num_verses": 34},
            {"chapter_no": 16, "num_verses": 34},
            {"chapter_no": 17, "num_verses": 24},
            {"chapter_no": 18, "num_verses": 46},
            {"chapter_no": 19, "num_verses": 21},
            {"chapter_no": 20, "num_verses": 43},
            {"chapter_no": 21, "num_verses": 29},
            {"chapter_no": 22, "num_verses": 53},
        ],
    },
    {
        "book_name": "2 Kings",
        "kikuyu_name": "2 Athamaki",
        "num_chapters": 25,
        "chapters": [
            {"chapter_no": 1, "num_verses": 18},
            {"chapter_no": 2, "num_verses": 25},
            {"chapter_no": 3, "num_verses": 27},
            {"chapter_no": 4, "num_verses": 44},
            {"chapter_no": 5, "num_verses": 27},
            {"chapter_no": 6, "num_verses": 33},
            {"chapter_no": 7, "num_verses": 20},
            {"chapter_no": 8, "num_verses": 29},
            {"chapter_no": 9, "num_verses": 37},
            {"chapter_no": 10, "num_verses": 36},
            {"chapter_no": 11, "num_verses": 21},
            {"chapter_no": 12, "num_verses": 21},
            {"chapter_no": 13, "num_verses": 25},
            {"chapter_no": 14, "num_verses": 29},
            {"chapter_no": 15, "num_verses": 38},
            {"chapter_no": 16, "num_verses": 20},
            {"chapter_no": 17, "num_verses": 41},
            {"chapter_no": 18, "num_verses": 37},
            {"chapter_no": 19, "num_verses": 37},
            {"chapter_no": 20, "num_verses": 21},
            {"chapter_no": 21, "num_verses": 26},
            {"chapter_no": 22, "num_verses": 20},
            {"chapter_no": 23, "num_verses": 37},
            {"chapter_no": 24, "num_verses": 20},
            {"chapter_no": 25, "num_verses": 30},
        ],
    },
    {
        "book_name": "1 Chronicles",
        "kikuyu_name": "1 Maũndũ ma Matukũ",
        "num_chapters": 29,
        "chapters": [
            {"chapter_no": 1, "num_verses": 54},
            {"chapter_no": 2, "num_verses": 55},
            {"chapter_no": 3, "num_verses": 24},
            {"chapter_no": 4, "num_verses": 43},
            {"chapter_no": 5, "num_verses": 26},
            {"chapter_no": 6, "num_verses": 81},
            {"chapter_no": 7, "num_verses": 40},
            {"chapter_no": 8, "num_verses": 40},
            {"chapter_no": 9, "num_verses": 44},
            {"chapter_no": 10, "num_verses": 14},
            {"chapter_no": 11, "num_verses": 47},
            {"chapter_no": 12, "num_verses": 40},
            {"chapter_no": 13, "num_verses": 14},
            {"chapter_no": 14, "num_verses": 17},
            {"chapter_no": 15, "num_verses": 29},
            {"chapter_no": 16, "num_verses": 43},
            {"chapter_no": 17, "num_verses": 27},
            {"chapter_no": 18, "num_verses": 17},
            {"chapter_no": 19, "num_verses": 19},
            {"chapter_no": 20, "num_verses": 8},
            {"chapter_no": 21, "num_verses": 30},
            {"chapter_no": 22, "num_verses": 19},
            {"chapter_no": 23, "num_verses": 32},
            {"chapter_no": 24, "num_verses": 31},
            {"chapter_no": 25, "num_verses": 31},
            {"chapter_no": 26, "num_verses": 32},
            {"chapter_no": 27, "num_verses": 34},
            {"chapter_no": 28, "num_verses": 21},
            {"chapter_no": 29, "num_verses": 30},
        ],
    },
    {
        "book_name": "2 Chronicles",
        "kikuyu_name": "2 Maũndũ ma Matukũ",
        "num_chapters": 36,
        "chapters": [
            {"chapter_no": 1, "num_verses": 17},
            {"chapter_no": 2, "num_verses": 18},
            {"chapter_no": 3, "num_verses": 17},
            {"chapter_no": 4, "num_verses": 22},
            {"chapter_no": 5, "num_verses": 14},
            {"chapter_no": 6, "num_verses": 42},
            {"chapter_no": 7, "num_verses": 22},
            {"chapter_no": 8, "num_verses": 18},
            {"chapter_no": 9, "num_verses": 31},
            {"chapter_no": 10, "num_verses": 19},
            {"chapter_no": 11, "num_verses": 23},
            {"chapter_no": 12, "num_verses": 16},
            {"chapter_no": 13, "num_verses": 22},
            {"chapter_no": 14, "num_verses": 15},
            {"chapter_no": 15, "num_verses": 19},
            {"chapter_no": 16, "num_verses": 14},
            {"chapter_no": 17, "num_verses": 19},
            {"chapter_no": 18, "num_verses": 34},
            {"chapter_no": 19, "num_verses": 11},
            {"chapter_no": 20, "num_verses": 37},
            {"chapter_no": 21, "num_verses": 20},
            {"chapter_no": 22, "num_verses": 12},
            {"chapter_no": 23, "num_verses": 21},
            {"chapter_no": 24, "num_verses": 27},
            {"chapter_no": 25, "num_verses": 28},
            {"chapter_no": 26, "num_verses": 23},
            {"chapter_no": 27, "num_verses": 9},
            {"chapter_no": 28, "num_verses": 27},
            {"chapter_no": 29, "num_verses": 36},
            {"chapter_no": 30, "num_verses": 27},
            {"chapter_no": 31, "num_verses": 21},
            {"chapter_no": 32, "num_verses": 33},
            {"chapter_no": 33, "num_verses": 25},
            {"chapter_no": 34, "num_verses": 33},
            {"chapter_no": 35, "num_verses": 27},
            {"chapter_no": 36, "num_verses": 23},
        ],
    },
    {
        "book_name": "Ezra",
        "kikuyu_name": "Ezira",
        "num_chapters": 10,
        "chapters": [
            {"chapter_no": 1, "num_verses": 11},
            {"chapter_no": 2, "num_verses": 70},
            {"chapter_no": 3, "num_verses": 13},
            {"chapter_no": 4, "num_verses": 24},
            {"chapter_no": 5, "num_verses": 17},
            {"chapter_no": 6, "num_verses": 22},
            {"chapter_no": 7, "num_verses": 28},
            {"chapter_no": 8, "num_verses": 36},
            {"chapter_no": 9, "num_verses": 15},
            {"chapter_no": 10, "num_verses": 44},
        ],
    },
    {
        "book_name": "Nehemiah",
        "kikuyu_name": "Nehemia",
        "num_chapters": 13,
        "chapters": [
            {"chapter_no": 1, "num_verses": 11},
            {"chapter_no": 2, "num_verses": 20},
            {"chapter_no": 3, "num_verses": 32},
            {"chapter_no": 4, "num_verses": 23},
            {"chapter_no": 5, "num_verses": 19},
            {"chapter_no": 6, "num_verses": 19},
            {"chapter_no": 7, "num_verses": 73},
            {"chapter_no": 8, "num_verses": 18},
            {"chapter_no": 9, "num_verses": 38},
            {"chapter_no": 10, "num_verses": 39},
            {"chapter_no": 11, "num_verses": 36},
            {"chapter_no": 12, "num_verses": 47},
            {"chapter_no": 13, "num_verses": 31},
        ],
    },
    {
        "book_name": "Esther",
        "kikuyu_name": "Esiteri",
        "num_chapters": 10,
        "chapters": [
            {"chapter_no": 1, "num_verses": 22},
            {"chapter_no": 2, "num_verses": 23},
            {"chapter_no": 3, "num_verses": 15},
            {"chapter_no": 4, "num_verses": 17},
            {"chapter_no": 5, "num_verses": 14},
            {"chapter_no": 6, "num_verses": 14},
            {"chapter_no": 7, "num_verses": 10},
            {"chapter_no": 8, "num_verses": 17},
            {"chapter_no": 9, "num_verses": 32},
            {"chapter_no": 10, "num_verses": 3},
        ],
    },
    {
        "book_name": "Job",
        "kikuyu_name": "Ayubu",
        "num_chapters": 42,
        "chapters": [
            {"chapter_no": 1, "num_verses": 22},
            {"chapter_no": 2, "num_verses": 13},
            {"chapter_no": 3, "num_verses": 26},
            {"chapter_no": 4, "num_verses": 21},
            {"chapter_no": 5, "num_verses": 27},
            {"chapter_no": 6, "num_verses": 30},
            {"chapter_no": 7, "num_verses": 21},
            {"chapter_no": 8, "num_verses": 22},
            {"chapter_no": 9, "num_verses": 35},
            {"chapter_no": 10, "num_verses": 22},
            {"chapter_no": 11, "num_verses": 20},
            {"chapter_no": 12, "num_verses": 25},
            {"chapter_no": 13, "num_verses": 28},
            {"chapter_no": 14, "num_verses": 22},
            {"chapter_no": 15, "num_verses": 35},
            {"chapter_no": 16, "num_verses": 22},
            {"chapter_no": 17, "num_verses": 16},
            {"chapter_no": 18, "num_verses": 21},
            {"chapter_no": 19, "num_verses": 29},
            {"chapter_no": 20, "num_verses": 29},
            {"chapter_no": 21, "num_verses": 34},
            {"chapter_no": 22, "num_verses": 30},
            {"chapter_no": 23, "num_verses": 17},
            {"chapter_no": 24, "num_verses": 25},
            {"chapter_no": 25, "num_verses": 6},
            {"chapter_no": 26, "num_verses": 14},
            {"chapter_no": 27, "num_verses": 23},
            {"chapter_no": 28, "num_verses": 28},
            {"chapter_no": 29, "num_verses": 25},
            {"chapter_no": 30, "num_verses": 31},
            {"chapter_no": 31, "num_verses": 40},
            {"chapter_no": 32, "num_verses": 22},
            {"chapter_no": 33, "num_verses": 33},
            {"chapter_no": 34, "num_verses": 37},
            {"chapter_no": 35, "num_verses": 16},
            {"chapter_no": 36, "num_verses": 33},
            {"chapter_no": 37, "num_verses": 24},
            {"chapter_no": 38, "num_verses": 41},
            {"chapter_no": 39, "num_verses": 30},
            {"chapter_no": 40, "num_verses": 24},
            {"chapter_no": 41, "num_verses": 34},
            {"chapter_no": 42, "num_verses": 17},
        ],
    },
    {
        "book_name": "Psalms",
        "kikuyu_name": "Thaburi",
        "num_chapters": 150,
        "chapters": [
            {"chapter_no": 1, "num_verses": 6},
            {"chapter_no": 2, "num_verses": 12},
            {"chapter_no": 3, "num_verses": 8},
            {"chapter_no": 4, "num_verses": 8},
            {"chapter_no": 5, "num_verses": 12},
            {"chapter_no": 6, "num_verses": 10},
            {"chapter_no": 7, "num_verses": 17},
            {"chapter_no": 8, "num_verses": 9},
            {"chapter_no": 9, "num_verses": 20},
            {"chapter_no": 10, "num_verses": 18},
            {"chapter_no": 11, "num_verses": 7},
            {"chapter_no": 12, "num_verses": 8},
            {"chapter_no": 13, "num_verses": 6},
            {"chapter_no": 14, "num_verses": 7},
            {"chapter_no": 15, "num_verses": 5},
            {"chapter_no": 16, "num_verses": 11},
            {"chapter_no": 17, "num_verses": 15},
            {"chapter_no": 18, "num_verses": 50},
            {"chapter_no": 19, "num_verses": 14},
            {"chapter_no": 20, "num_verses": 9},
            {"chapter_no": 21, "num_verses": 13},
            {"chapter_no": 22, "num_verses": 31},
            {"chapter_no": 23, "num_verses": 6},
            {"chapter_no": 24, "num_verses": 10},
            {"chapter_no": 25, "num_verses": 22},
            {"chapter_no": 26, "num_verses": 12},
            {"chapter_no": 27, "num_verses": 14},
            {"chapter_no": 28, "num_verses": 9},
            {"chapter_no": 29, "num_verses": 11},
            {"chapter_no": 30, "num_verses": 12},
            {"chapter_no": 31, "num_verses": 24},
            {"chapter_no": 32, "num_verses": 11},
            {"chapter_no": 33, "num_verses": 22},
            {"chapter_no": 34, "num_verses": 22},
            {"chapter_no": 35, "num_verses": 28},
            {"chapter_no": 36, "num_verses": 12},
            {"chapter_no": 37, "num_verses": 40},
            {"chapter_no": 38, "num_verses": 22},
            {"chapter_no": 39, "num_verses": 13},
            {"chapter_no": 40, "num_verses": 17},
            {"chapter_no": 41, "num_verses": 13},
            {"chapter_no": 42, "num_verses": 11},
            {"chapter_no": 43, "num_verses": 5},
            {"chapter_no": 44, "num_verses": 26},
            {"chapter_no": 45, "num_verses": 17},
            {"chapter_no": 46, "num_verses": 11},
            {"chapter_no": 47, "num_verses": 9},
            {"chapter_no": 48, "num_verses": 14},
            {"chapter_no": 49, "num_verses": 20},
            {"chapter_no": 50, "num_verses": 23},
            {"chapter_no": 51, "num_verses": 19},
            {"chapter_no": 52, "num_verses": 9},
            {"chapter_no": 53, "num_verses": 6},
            {"chapter_no": 54, "num_verses": 7},
            {"chapter_no": 55, "num_verses": 23},
            {"chapter_no": 56, "num_verses": 13},
            {"chapter_no": 57, "num_verses": 11},
            {"chapter_no": 58, "num_verses": 11},
            {"chapter_no": 59, "num_verses": 17},
            {"chapter_no": 60, "num_verses": 12},
            {"chapter_no": 61, "num_verses": 8},
            {"chapter_no": 62, "num_verses": 12},
            {"chapter_no": 63, "num_verses": 11},
            {"chapter_no": 64, "num_verses": 10},
            {"chapter_no": 65, "num_verses": 13},
            {"chapter_no": 66, "num_verses": 20},
            {"chapter_no": 67, "num_verses": 7},
            {"chapter_no": 68, "num_verses": 35},
            {"chapter_no": 69, "num_verses": 36},
            {"chapter_no": 70, "num_verses": 5},
            {"chapter_no": 71, "num_verses": 24},
            {"chapter_no": 72, "num_verses": 20},
            {"chapter_no": 73, "num_verses": 28},
            {"chapter_no": 74, "num_verses": 23},
            {"chapter_no": 75, "num_verses": 10},
            {"chapter_no": 76, "num_verses": 12},
            {"chapter_no": 77, "num_verses": 20},
            {"chapter_no": 78, "num_verses": 72},
            {"chapter_no": 79, "num_verses": 13},
            {"chapter_no": 80, "num_verses": 19},
            {"chapter_no": 81, "num_verses": 16},
            {"chapter_no": 82, "num_verses": 8},
            {"chapter_no": 83, "num_verses": 18},
            {"chapter_no": 84, "num_verses": 12},
            {"chapter_no": 85, "num_verses": 13},
            {"chapter_no": 86, "num_verses": 17},
            {"chapter_no": 87, "num_verses": 7},
            {"chapter_no": 88, "num_verses": 18},
            {"chapter_no": 89, "num_verses": 52},
            {"chapter_no": 90, "num_verses": 17},
            {"chapter_no": 91, "num_verses": 16},
            {"chapter_no": 92, "num_verses": 15},
            {"chapter_no": 93, "num_verses": 5},
            {"chapter_no": 94, "num_verses": 23},
            {"chapter_no": 95, "num_verses": 11},
            {"chapter_no": 96, "num_verses": 13},
            {"chapter_no": 97, "num_verses": 12},
            {"chapter_no": 98, "num_verses": 9},
            {"chapter_no": 99, "num_verses": 9},
            {"chapter_no": 100, "num_verses": 5},
            {"chapter_no": 101, "num_verses": 8},
            {"chapter_no": 102, "num_verses": 28},
            {"chapter_no": 103, "num_verses": 22},
            {"chapter_no": 104, "num_verses": 35},
            {"chapter_no": 105, "num_verses": 45},
            {"chapter_no": 106, "num_verses": 48},
            {"chapter_no": 107, "num_verses": 43},
            {"chapter_no": 108, "num_verses": 13},
            {"chapter_no": 109, "num_verses": 31},
            {"chapter_no": 110, "num_verses": 7},
            {"chapter_no": 111, "num_verses": 10},
            {"chapter_no": 112, "num_verses": 10},
            {"chapter_no": 113, "num_verses": 9},
            {"chapter_no": 114, "num_verses": 8},
            {"chapter_no": 115, "num_verses": 18},
            {"chapter_no": 116, "num_verses": 19},
            {"chapter_no": 117, "num_verses": 2},
            {"chapter_no": 118, "num_verses": 29},
            {"chapter_no": 119, "num_verses": 176},
            {"chapter_no": 120, "num_verses": 7},
            {"chapter_no": 121, "num_verses": 8},
            {"chapter_no": 122, "num_verses": 9},
            {"chapter_no": 123, "num_verses": 4},
            {"chapter_no": 124, "num_verses": 8},
            {"chapter_no": 125, "num_verses": 5},
            {"chapter_no": 126, "num_verses": 6},
            {"chapter_no": 127, "num_verses": 5},
            {"chapter_no": 128, "num_verses": 6},
            {"chapter_no": 129, "num_verses": 8},
            {"chapter_no": 130, "num_verses": 8},
            {"chapter_no": 131, "num_verses": 3},
            {"chapter_no": 132, "num_verses": 18},
            {"chapter_no": 133, "num_verses": 3},
            {"chapter_no": 134, "num_verses": 3},
            {"chapter_no": 135, "num_verses": 21},
            {"chapter_no": 136, "num_verses": 26},
            {"chapter_no": 137, "num_verses": 9},
            {"chapter_no": 138, "num_verses": 8},
            {"chapter_no": 139, "num_verses": 24},
            {"chapter_no": 140, "num_verses": 13},
            {"chapter_no": 141, "num_verses": 10},
            {"chapter_no": 142, "num_verses": 7},
            {"chapter_no": 143, "num_verses": 12},
            {"chapter_no": 144, "num_verses": 15},
            {"chapter_no": 145, "num_verses": 21},
            {"chapter_no": 146, "num_verses": 10},
            {"chapter_no": 147, "num_verses": 20},
            {"chapter_no": 148, "num_verses": 14},
            {"chapter_no": 149, "num_verses": 9},
            {"chapter_no": 150, "num_verses": 6},
        ],
    },
    {
        "book_name": "Proverbs",
        "kikuyu_name": "Thimo",
        "num_chapters": 31,
        "chapters": [
            {"chapter_no": 1, "num_verses": 33},
            {"chapter_no": 2, "num_verses": 22},
            {"chapter_no": 3, "num_verses": 35},
            {"chapter_no": 4, "num_verses": 27},
            {"chapter_no": 5, "num_verses": 23},
            {"chapter_no": 6, "num_verses": 35},
            {"chapter_no": 7, "num_verses": 27},
            {"chapter_no": 8, "num_verses": 36},
            {"chapter_no": 9, "num_verses": 18},
            {"chapter_no": 10, "num_verses": 32},
            {"chapter_no": 11, "num_verses": 31},
            {"chapter_no": 12, "num_verses": 28},
            {"chapter_no": 13, "num_verses": 25},
            {"chapter_no": 14, "num_verses": 35},
            {"chapter_no": 15, "num_verses": 33},
            {"chapter_no": 16, "num_verses": 33},
            {"chapter_no": 17, "num_verses": 28},
            {"chapter_no": 18, "num_verses": 24},
            {"chapter_no": 19, "num_verses": 29},
            {"chapter_no": 20, "num_verses": 30},
            {"chapter_no": 21, "num_verses": 31},
            {"chapter_no": 22, "num_verses": 29},
            {"chapter_no": 23, "num_verses": 35},
            {"chapter_no": 24, "num_verses": 34},
            {"chapter_no": 25, "num_verses": 28},
            {"chapter_no": 26, "num_verses": 28},
            {"chapter_no": 27, "num_verses": 27},
            {"chapter_no": 28, "num_verses": 28},
            {"chapter_no": 29, "num_verses": 27},
            {"chapter_no": 30, "num_verses": 33},
            {"chapter_no": 31, "num_verses": 31},
        ],
    },
    {
        "book_name": "Ecclesiastes",
        "kikuyu_name": "Mũhubĩri",
        "num_chapters": 12,
        "chapters": [
            {"chapter_no": 1, "num_verses": 18},
            {"chapter_no": 2, "num_verses": 26},
            {"chapter_no": 3, "num_verses": 22},
            {"chapter_no": 4, "num_verses": 16},
            {"chapter_no": 5, "num_verses": 20},
            {"chapter_no": 6, "num_verses": 12},
            {"chapter_no": 7, "num_verses": 29},
            {"chapter_no": 8, "num_verses": 17},
            {"chapter_no": 9, "num_verses": 18},
            {"chapter_no": 10, "num_verses": 20},
            {"chapter_no": 11, "num_verses": 10},
            {"chapter_no": 12, "num_verses": 14},
        ],
    },
    {
        "book_name": "Song of Solomon",
        "kikuyu_name": "Rwĩmbo rwa Solomoni",
        "num_chapters": 8,
        "chapters": [
            {"chapter_no": 1, "num_verses": 17},
            {"chapter_no": 2, "num_verses": 17},
            {"chapter_no": 3, "num_verses": 11},
            {"chapter_no": 4, "num_verses": 16},
            {"chapter_no": 5, "num_verses": 16},
            {"chapter_no": 6, "num_verses": 13},
            {"chapter_no": 7, "num_verses": 13},
            {"chapter_no": 8, "num_verses": 14},
        ],
    },
    {
        "book_name": "Isaiah",
        "kikuyu_name": "Isaia",
        "num_chapters": 66,
        "chapters": [
            {"chapter_no": 1, "num_verses": 31},
            {"chapter_no": 2, "num_verses": 22},
            {"chapter_no": 3, "num_verses": 26},
            {"chapter_no": 4, "num_verses": 6},
            {"chapter_no": 5, "num_verses": 30},
            {"chapter_no": 6, "num_verses": 13},
            {"chapter_no": 7, "num_verses": 25},
            {"chapter_no": 8, "num_verses": 22},
            {"chapter_no": 9, "num_verses": 21},
            {"chapter_no": 10, "num_verses": 34},
            {"chapter_no": 11, "num_verses": 16},
            {"chapter_no": 12, "num_verses": 6},
            {"chapter_no": 13, "num_verses": 22},
            {"chapter_no": 14, "num_verses": 32},
            {"chapter_no": 15, "num_verses": 9},
            {"chapter_no": 16, "num_verses": 14},
            {"chapter_no": 17, "num_verses": 14},
            {"chapter_no": 18, "num_verses": 7},
            {"chapter_no": 19, "num_verses": 25},
            {"chapter_no": 20, "num_verses": 6},
            {"chapter_no": 21, "num_verses": 17},
            {"chapter_no": 22, "num_verses": 25},
            {"chapter_no": 23, "num_verses": 18},
            {"chapter_no": 24, "num_verses": 23},
            {"chapter_no": 25, "num_verses": 12},
            {"chapter_no": 26, "num_verses": 21},
            {"chapter_no": 27, "num_verses": 13},
            {"chapter_no": 28, "num_verses": 29},
            {"chapter_no": 29, "num_verses": 24},
            {"chapter_no": 30, "num_verses": 33},
            {"chapter_no": 31, "num_verses": 9},
            {"chapter_no": 32, "num_verses": 20},
            {"chapter_no": 33, "num_verses": 24},
            {"chapter_no": 34, "num_verses": 17},
            {"chapter_no": 35, "num_verses": 10},
            {"chapter_no": 36, "num_verses": 22},
            {"chapter_no": 37, "num_verses": 38},
            {"chapter_no": 38, "num_verses": 22},
            {"chapter_no": 39, "num_verses": 8},
            {"chapter_no": 40, "num_verses": 31},
            {"chapter_no": 41, "num_verses": 29},
            {"chapter_no": 42, "num_verses": 25},
            {"chapter_no": 43, "num_verses": 28},
            {"chapter_no": 44, "num_verses": 28},
            {"chapter_no": 45, "num_verses": 25},
            {"chapter_no": 46, "num_verses": 13},
            {"chapter_no": 47, "num_verses": 15},
            {"chapter_no": 48, "num_verses": 22},
            {"chapter_no": 49, "num_verses": 26},
            {"chapter_no": 50, "num_verses": 11},
            {"chapter_no": 51, "num_verses": 23},
            {"chapter_no": 52, "num_verses": 15},
            {"chapter_no": 53, "num_verses": 12},
            {"chapter_no": 54, "num_verses": 17},
            {"chapter_no": 55, "num_verses": 13},
            {"chapter_no": 56, "num_verses": 12},
            {"chapter_no": 57, "num_verses": 21},
            {"chapter_no": 58, "num_verses": 14},
            {"chapter_no": 59, "num_verses": 21},
            {"chapter_no": 60, "num_verses": 22},
            {"chapter_no": 61, "num_verses": 11},
            {"chapter_no": 62, "num_verses": 12},
            {"chapter_no": 63, "num_verses": 19},
            {"chapter_no": 64, "num_verses": 12},
            {"chapter_no": 65, "num_verses": 25},
            {"chapter_no": 66, "num_verses": 24},
        ],
    },
    {
        "book_name": "Jeremiah",
        "kikuyu_name": "Jeremia",
        "num_chapters": 52,
        "chapters": [
            {"chapter_no": 1, "num_verses": 19},
            {"chapter_no": 2, "num_verses": 37},
            {"chapter_no": 3, "num_verses": 25},
            {"chapter_no": 4, "num_verses": 31},
            {"chapter_no": 5, "num_verses": 31},
            {"chapter_no": 6, "num_verses": 30},
            {"chapter_no": 7, "num_verses": 34},
            {"chapter_no": 8, "num_verses": 22},
            {"chapter_no": 9, "num_verses": 26},
            {"chapter_no": 10, "num_verses": 25},
            {"chapter_no": 11, "num_verses": 23},
            {"chapter_no": 12, "num_verses": 17},
            {"chapter_no": 13, "num_verses": 27},
            {"chapter_no": 14, "num_verses": 22},
            {"chapter_no": 15, "num_verses": 21},
            {"chapter_no": 16, "num_verses": 21},
            {"chapter_no": 17, "num_verses": 27},
            {"chapter_no": 18, "num_verses": 23},
            {"chapter_no": 19, "num_verses": 15},
            {"chapter_no": 20, "num_verses": 18},
            {"chapter_no": 21, "num_verses": 14},
            {"chapter_no": 22, "num_verses": 30},
            {"chapter_no": 23, "num_verses": 40},
            {"chapter_no": 24, "num_verses": 10},
            {"chapter_no": 25, "num_verses": 38},
            {"chapter_no": 26, "num_verses": 24},
            {"chapter_no": 27, "num_verses": 22},
            {"chapter_no": 28, "num_verses": 17},
            {"chapter_no": 29, "num_verses": 32},
            {"chapter_no": 30, "num_verses": 24},
            {"chapter_no": 31, "num_verses": 40},
            {"chapter_no": 32, "num_verses": 44},
            {"chapter_no": 33, "num_verses": 26},
            {"chapter_no": 34, "num_verses": 22},
            {"chapter_no": 35, "num_verses": 19},
            {"chapter_no": 36, "num_verses": 32},
            {"chapter_no": 37, "num_verses": 21},
            {"chapter_no": 38, "num_verses": 28},
            {"chapter_no": 39, "num_verses": 18},
            {"chapter_no": 40, "num_verses": 16},
            {"chapter_no": 41, "num_verses": 18},
            {"chapter_no": 42, "num_verses": 22},
            {"chapter_no": 43, "num_verses": 13},
            {"chapter_no": 44, "num_verses": 30},
            {"chapter_no": 45, "num_verses": 5},
            {"chapter_no": 46, "num_verses": 28},
            {"chapter_no": 47, "num_verses": 7},
            {"chapter_no": 48, "num_verses": 47},
            {"chapter_no": 49, "num_verses": 39},
            {"chapter_no": 50, "num_verses": 46},
            {"chapter_no": 51, "num_verses": 64},
            {"chapter_no": 52, "num_verses": 34},
        ],
    },
    {
        "book_name": "Lamentations",
        "kikuyu_name": "Macakaya",
        "num_chapters": 5,
        "chapters": [
            {"chapter_no": 1, "num_verses": 22},
            {"chapter_no": 2, "num_verses": 22},
            {"chapter_no": 3, "num_verses": 66},
            {"chapter_no": 4, "num_verses": 22},
            {"chapter_no": 5, "num_verses": 22},
        ],
    },
    {
        "book_name": "Ezekiel",
        "kikuyu_name": "Ezekieli",
        "num_chapters": 48,
        "chapters": [
            {"chapter_no": 1, "num_verses": 28},
            {"chapter_no": 2, "num_verses": 10},
            {"chapter_no": 3, "num_verses": 27},
            {"chapter_no": 4, "num_verses": 17},
            {"chapter_no": 5, "num_verses": 17},
            {"chapter_no": 6, "num_verses": 14},
            {"chapter_no": 7, "num_verses": 27},
            {"chapter_no": 8, "num_verses": 18},
            {"chapter_no": 9, "num_verses": 11},
            {"chapter_no": 10, "num_verses": 22},
            {"chapter_no": 11, "num_verses": 25},
            {"chapter_no": 12, "num_verses": 28},
            {"chapter_no": 13, "num_verses": 23},
            {"chapter_no": 14, "num_verses": 23},
            {"chapter_no": 15, "num_verses": 8},
            {"chapter_no": 16, "num_verses": 63},
            {"chapter_no": 17, "num_verses": 24},
            {"chapter_no": 18, "num_verses": 32},
            {"chapter_no": 19, "num_verses": 14},
            {"chapter_no": 20, "num_verses": 49},
            {"chapter_no": 21, "num_verses": 32},
            {"chapter_no": 22, "num_verses": 31},
            {"chapter_no": 23, "num_verses": 49},
            {"chapter_no": 24, "num_verses": 27},
            {"chapter_no": 25, "num_verses": 17},
            {"chapter_no": 26, "num_verses": 21},
            {"chapter_no": 27, "num_verses": 36},
            {"chapter_no": 28, "num_verses": 26},
            {"chapter_no": 29, "num_verses": 21},
            {"chapter_no": 30, "num_verses": 26},
            {"chapter_no": 31, "num_verses": 18},
            {"chapter_no": 32, "num_verses": 32},
            {"chapter_no": 33, "num_verses": 33},
            {"chapter_no": 34, "num_verses": 31},
            {"chapter_no": 35, "num_verses": 15},
            {"chapter_no": 36, "num_verses": 38},
            {"chapter_no": 37, "num_verses": 28},
            {"chapter_no": 38, "num_verses": 23},
            {"chapter_no": 39, "num_verses": 29},
            {"chapter_no": 40, "num_verses": 49},
            {"chapter_no": 41, "num_verses": 26},
            {"chapter_no": 42, "num_verses": 20},
            {"chapter_no": 43, "num_verses": 27},
            {"chapter_no": 44, "num_verses": 31},
            {"chapter_no": 45, "num_verses": 25},
            {"chapter_no": 46, "num_verses": 24},
            {"chapter_no": 47, "num_verses": 23},
            {"chapter_no": 48, "num_verses": 35},
        ],
    },
    {
        "book_name": "Daniel",
        "kikuyu_name": "Danieli",
        "num_chapters": 12,
        "chapters": [
            {"chapter_no": 1, "num_verses": 21},
            {"chapter_no": 2, "num_verses": 49},
            {"chapter_no": 3, "num_verses": 30},
            {"chapter_no": 4, "num_verses": 37},
            {"chapter_no": 5, "num_verses": 31},
            {"chapter_no": 6, "num_verses": 28},
            {"chapter_no": 7, "num_verses": 28},
            {"chapter_no": 8, "num_verses": 27},
            {"chapter_no": 9, "num_verses": 27},
            {"chapter_no": 10, "num_verses": 21},
            {"chapter_no": 11, "num_verses": 45},
            {"chapter_no": 12, "num_verses": 13},
        ],
    },
    {
        "book_name": "Hosea",
        "kikuyu_name": "Hosea",
        "num_chapters": 14,
        "chapters": [
            {"chapter_no": 1, "num_verses": 11},
            {"chapter_no": 2, "num_verses": 23},
            {"chapter_no": 3, "num_verses": 5},
            {"chapter_no": 4, "num_verses": 19},
            {"chapter_no": 5, "num_verses": 15},
            {"chapter_no": 6, "num_verses": 11},
            {"chapter_no": 7, "num_verses": 16},
            {"chapter_no": 8, "num_verses": 14},
            {"chapter_no": 9, "num_verses": 17},
            {"chapter_no": 10, "num_verses": 15},
            {"chapter_no": 11, "num_verses": 12},
            {"chapter_no": 12, "num_verses": 14},
            {"chapter_no": 13, "num_verses": 16},
            {"chapter_no": 14, "num_verses": 9},
        ],
    },
    {
        "book_name": "Joel",
        "kikuyu_name": "Joeli",
        "num_chapters": 3,
        "chapters": [
            {"chapter_no": 1, "num_verses": 20},
            {"chapter_no": 2, "num_verses": 32},
            {"chapter_no": 3, "num_verses": 21},
        ],
    },
    {
        "book_name": "Amos",
        "kikuyu_name": "Amosi",
        "num_chapters": 9,
        "chapters": [
            {"chapter_no": 1, "num_verses": 15},
            {"chapter_no": 2, "num_verses": 16},
            {"chapter_no": 3, "num_verses": 15},
            {"chapter_no": 4, "num_verses": 13},
            {"chapter_no": 5, "num_verses": 27},
            {"chapter_no": 6, "num_verses": 14},
            {"chapter_no": 7, "num_verses": 17},
            {"chapter_no": 8, "num_verses": 14},
            {"chapter_no": 9, "num_verses": 15},
        ],
    },
    {
        "book_name": "Obadiah",
        "kikuyu_name": "Obadia",
        "num_chapters": 1,
        "chapters": [
            {"chapter_no": 1, "num_verses": 21},
        ],
    },
    {
        "book_name": "Jonah",
        "kikuyu_name": "Jona",
        "num_chapters": 4,
        "chapters": [
            {"chapter_no": 1, "num_verses": 17},
            {"chapter_no": 2, "num_verses": 10},
            {"chapter_no": 3, "num_verses": 10},
            {"chapter_no": 4, "num_verses": 11},
        ],
    },
    {
        "book_name": "Micah",
        "kikuyu_name": "Mika",
        "num_chapters": 7,
        "chapters": [
            {"chapter_no": 1, "num_verses": 16},
            {"chapter_no": 2, "num_verses": 13},
            {"chapter_no": 3, "num_verses": 12},
            {"chapter_no": 4, "num_verses": 13},
            {"chapter_no": 5, "num_verses": 15},
            {"chapter_no": 6, "num_verses": 16},
            {"chapter_no": 7, "num_verses": 20},
        ],
    },
    {
        "book_name": "Nahum",
        "kikuyu_name": "Nahumu",
        "num_chapters": 3,
        "chapters": [
            {"chapter_no": 1, "num_verses": 15},
            {"chapter_no": 2, "num_verses": 13},
            {"chapter_no": 3, "num_verses": 19},
        ],
    },
    {
        "book_name": "Habakkuk",
        "kikuyu_name": "Habakuku",
        "num_chapters": 3,
        "chapters": [
            {"chapter_no": 1, "num_verses": 17},
            {"chapter_no": 2, "num_verses": 20},
            {"chapter_no": 3, "num_verses": 19},
        ],
    },
    {
        "book_name": "Zephaniah",
        "kikuyu_name": "Zefania",
        "num_chapters": 3,
        "chapters": [
            {"chapter_no": 1, "num_verses": 18},
            {"chapter_no": 2, "num_verses": 15},
            {"chapter_no": 3, "num_verses": 20},
        ],
    },
    {
        "book_name": "Haggai",
        "kikuyu_name": "Hagai",
        "num_chapters": 2,
        "chapters": [
            {"chapter_no": 1, "num_verses": 15},
            {"chapter_no": 2, "num_verses": 23},
        ],
    },
    {
        "book_name": "Zechariah",
        "kikuyu_name": "Zekaria",
        "num_chapters": 14,
        "chapters": [
            {"chapter_no": 1, "num_verses": 21},
            {"chapter_no": 2, "num_verses": 13},
            {"chapter_no": 3, "num_verses": 10},
            {"chapter_no": 4, "num_verses": 14},
            {"chapter_no": 5, "num_verses": 11},
            {"chapter_no": 6, "num_verses": 15},
            {"chapter_no": 7, "num_verses": 14},
            {"chapter_no": 8, "num_verses": 23},
            {"chapter_no": 9, "num_verses": 17},
            {"chapter_no": 10, "num_verses": 12},
            {"chapter_no": 11, "num_verses": 17},
            {"chapter_no": 12, "num_verses": 14},
            {"chapter_no": 13, "num_verses": 9},
            {"chapter_no": 14, "num_verses": 21},
        ],
    },
    {
        "book_name": "Malachi",
        "kikuyu_name": "Malaki",
        "num_chapters": 4,
        "chapters": [
            {"chapter_no": 1, "num_verses": 14},
            {"chapter_no": 2, "num_verses": 17},
            {"chapter_no": 3, "num_verses": 18},
            {"chapter_no": 4, "num_verses": 6},
        ],
    },
    {
        "book_name": "Matthew",
        "kikuyu_name": "Mathayo",
        "num_chapters": 28,
        "chapters": [
            {"chapter_no": 1, "num_verses": 25},
            {"chapter_no": 2, "num_verses": 23},
            {"chapter_no": 3, "num_verses": 17},
            {"chapter_no": 4, "num_verses": 25},
            {"chapter_no": 5, "num_verses": 48},
            {"chapter_no": 6, "num_verses": 34},
            {"chapter_no": 7, "num_verses": 29},
            {"chapter_no": 8, "num_verses": 34},
            {"chapter_no": 9, "num_verses": 38},
            {"chapter_no": 10, "num_verses": 42},
            {"chapter_no": 11, "num_verses": 30},
            {"chapter_no": 12, "num_verses": 50},
            {"chapter_no": 13, "num_verses": 58},
            {"chapter_no": 14, "num_verses": 36},
            {"chapter_no": 15, "num_verses": 39},
            {"chapter_no": 16, "num_verses": 28},
            {"chapter_no": 17, "num_verses": 27},
            {"chapter_no": 18, "num_verses": 35},
            {"chapter_no": 19, "num_verses": 30},
            {"chapter_no": 20, "num_verses": 34},
            {"chapter_no": 21, "num_verses": 46},
            {"chapter_no": 22, "num_verses": 46},
            {"chapter_no": 23, "num_verses": 39},
            {"chapter_no": 24, "num_verses": 51},
            {"chapter_no": 25, "num_verses": 46},
            {"chapter_no": 26, "num_verses": 75},
            {"chapter_no": 27, "num_verses": 66},
            {"chapter_no": 28, "num_verses": 20},
        ],
    },
    {
        "book_name": "Mark",
        "kikuyu_name": "Mariko",
        "num_chapters": 16,
        "chapters": [
            {"chapter_no": 1, "num_verses": 45},
            {"chapter_no": 2, "num_verses": 28},
            {"chapter_no": 3, "num_verses": 35},
            {"chapter_no": 4, "num_verses": 41},
            {"chapter_no": 5, "num_verses": 43},
            {"chapter_no": 6, "num_verses": 56},
            {"chapter_no": 7, "num_verses": 37},
            {"chapter_no": 8, "num_verses": 38},
            {"chapter_no": 9, "num_verses": 50},
            {"chapter_no": 10, "num_verses": 52},
            {"chapter_no": 11, "num_verses": 33},
            {"chapter_no": 12, "num_verses": 44},
            {"chapter_no": 13, "num_verses": 37},
            {"chapter_no": 14, "num_verses": 72},
            {"chapter_no": 15, "num_verses": 47},
            {"chapter_no": 16, "num_verses": 20},
        ],
    },
    {
        "book_name": "Luke",
        "kikuyu_name": "Luka",
        "num_chapters": 24,
        "chapters": [
            {"chapter_no": 1, "num_verses": 80},
            {"chapter_no": 2, "num_verses": 52},
            {"chapter_no": 3, "num_verses": 38},
            {"chapter_no": 4, "num_verses": 44},
            {"chapter_no": 5, "num_verses": 39},
            {"chapter_no": 6, "num_verses": 49},
            {"chapter_no": 7, "num_verses": 50},
            {"chapter_no": 8, "num_verses": 56},
            {"chapter_no": 9, "num_verses": 62},
            {"chapter_no": 10, "num_verses": 42},
            {"chapter_no": 11, "num_verses": 54},
            {"chapter_no": 12, "num_verses": 59},
            {"chapter_no": 13, "num_verses": 35},
            {"chapter_no": 14, "num_verses": 35},
            {"chapter_no": 15, "num_verses": 32},
            {"chapter_no": 16, "num_verses": 31},
            {"chapter_no": 17, "num_verses": 37},
            {"chapter_no": 18, "num_verses": 43},
            {"chapter_no": 19, "num_verses": 48},
            {"chapter_no": 20, "num_verses": 47},
            {"chapter_no": 21, "num_verses": 38},
            {"chapter_no": 22, "num_verses": 71},
            {"chapter_no": 23, "num_verses": 56},
            {"chapter_no": 24, "num_verses": 53},
        ],
    },
    {
        "book_name": "John",
        "kikuyu_name": "Johana",
        "num_chapters": 21,
        "chapters": [
            {"chapter_no": 1, "num_verses": 51},
            {"chapter_no": 2, "num_verses": 25},
            {"chapter_no": 3, "num_verses": 36},
            {"chapter_no": 4, "num_verses": 54},
            {"chapter_no": 5, "num_verses": 47},
            {"chapter_no": 6, "num_verses": 71},
            {"chapter_no": 7, "num_verses": 53},
            {"chapter_no": 8, "num_verses": 59},
            {"chapter_no": 9, "num_verses": 41},
            {"chapter_no": 10, "num_verses": 42},
            {"chapter_no": 11, "num_verses": 57},
            {"chapter_no": 12, "num_verses": 50},
            {"chapter_no": 13, "num_verses": 38},
            {"chapter_no": 14, "num_verses": 31},
            {"chapter_no": 15, "num_verses": 27},
            {"chapter_no": 16, "num_verses": 33},
            {"chapter_no": 17, "num_verses": 26},
            {"chapter_no": 18, "num_verses": 40},
            {"chapter_no": 19, "num_verses": 42},
            {"chapter_no": 20, "num_verses": 31},
            {"chapter_no": 21, "num_verses": 25},
        ],
    },
    {
        "book_name": "Acts",
        "kikuyu_name": "Atũmwo",
        "num_chapters": 28,
        "chapters": [
            {"chapter_no": 1, "num_verses": 26},
            {"chapter_no": 2, "num_verses": 47},
            {"chapter_no": 3, "num_verses": 26},
            {"chapter_no": 4, "num_verses": 37},
            {"chapter_no": 5, "num_verses": 42},
            {"chapter_no": 6, "num_verses": 15},
            {"chapter_no": 7, "num_verses": 60},
            {"chapter_no": 8, "num_verses": 40},
            {"chapter_no": 9, "num_verses": 43},
            {"chapter_no": 10, "num_verses": 48},
            {"chapter_no": 11, "num_verses": 30},
            {"chapter_no": 12, "num_verses": 25},
            {"chapter_no": 13, "num_verses": 52},
            {"chapter_no": 14, "num_verses": 28},
            {"chapter_no": 15, "num_verses": 41},
            {"chapter_no": 16, "num_verses": 40},
            {"chapter_no": 17, "num_verses": 34},
            {"chapter_no": 18, "num_verses": 28},
            {"chapter_no": 19, "num_verses": 41},
            {"chapter_no": 20, "num_verses": 38},
            {"chapter_no": 21, "num_verses": 40},
            {"chapter_no": 22, "num_verses": 30},
            {"chapter_no": 23, "num_verses": 35},
            {"chapter_no": 24, "num_verses": 27},
            {"chapter_no": 25, "num_verses": 27},
            {"chapter_no": 26, "num_verses": 32},
            {"chapter_no": 27, "num_verses": 44},
            {"chapter_no": 28, "num_verses": 31},
        ],
    },
    {
        "book_name": "Romans",
        "kikuyu_name": "Aroma",
        "num_chapters": 16,
        "chapters": [
            {"chapter_no": 1, "num_verses": 32},
            {"chapter_no": 2, "num_verses": 29},
            {"chapter_no": 3, "num_verses": 31},
            {"chapter_no": 4, "num_verses": 25},
            {"chapter_no": 5, "num_verses": 21},
            {"chapter_no": 6, "num_verses": 23},
            {"chapter_no": 7, "num_verses": 25},
            {"chapter_no": 8, "num_verses": 39},
            {"chapter_no": 9, "num_verses": 33},
            {"chapter_no": 10, "num_verses": 21},
            {"chapter_no": 11, "num_verses": 36},
            {"chapter_no": 12, "num_verses": 21},
            {"chapter_no": 13, "num_verses": 14},
            {"chapter_no": 14, "num_verses": 23},
            {"chapter_no": 15, "num_verses": 33},
            {"chapter_no": 16, "num_verses": 27},
        ],
    },
    {
        "book_name": "1 Corinthians",
        "kikuyu_name": "1 Akorintho",
        "num_chapters": 16,
        "chapters": [
            {"chapter_no": 1, "num_verses": 31},
            {"chapter_no": 2, "num_verses": 16},
            {"chapter_no": 3, "num_verses": 23},
            {"chapter_no": 4, "num_verses": 21},
            {"chapter_no": 5, "num_verses": 13},
            {"chapter_no": 6, "num_verses": 20},
            {"chapter_no": 7, "num_verses": 40},
            {"chapter_no": 8, "num_verses": 13},
            {"chapter_no": 9, "num_verses": 27},
            {"chapter_no": 10, "num_verses": 33},
            {"chapter_no": 11, "num_verses": 34},
            {"chapter_no": 12, "num_verses": 31},
            {"chapter_no": 13, "num_verses": 13},
            {"chapter_no": 14, "num_verses": 40},
            {"chapter_no": 15, "num_verses": 58},
            {"chapter_no": 16, "num_verses": 24},
        ],
    },
    {
        "book_name": "2 Corinthians",
        "kikuyu_name": "2 Akorintho",
        "num_chapters": 13,
        "chapters": [
            {"chapter_no": 1, "num_verses": 24},
            {"chapter_no": 2, "num_verses": 17},
            {"chapter_no": 3, "num_verses": 18},
            {"chapter_no": 4, "num_verses": 18},
            {"chapter_no": 5, "num_verses": 21},
            {"chapter_no": 6, "num_verses": 18},
            {"chapter_no": 7, "num_verses": 16},
            {"chapter_no": 8, "num_verses": 24},
            {"chapter_no": 9, "num_verses": 15},
            {"chapter_no": 10, "num_verses": 18},
            {"chapter_no": 11, "num_verses": 33},
            {"chapter_no": 12, "num_verses": 21},
            {"chapter_no": 13, "num_verses": 14},
        ],
    },
    {
        "book_name": "Galatians",
        "kikuyu_name": "Agalatia",
        "num_chapters": 6,
        "chapters": [
            {"chapter_no": 1, "num_verses": 24},
            {"chapter_no": 2, "num_verses": 21},
            {"chapter_no": 3, "num_verses": 29},
            {"chapter_no": 4, "num_verses": 31},
            {"chapter_no": 5, "num_verses": 26},
            {"chapter_no": 6, "num_verses": 18},
        ],
    },
    {
        "book_name": "Ephesians",
        "kikuyu_name": "Aefeso",
        "num_chapters": 6,
        "chapters": [
            {"chapter_no": 1, "num_verses": 23},
            {"chapter_no": 2, "num_verses": 22},
            {"chapter_no": 3, "num_verses": 21},
            {"chapter_no": 4, "num_verses": 32},
            {"chapter_no": 5, "num_verses": 33},
            {"chapter_no": 6, "num_verses": 24},
        ],
    },
    {
        "book_name": "Philippians",
        "kikuyu_name": "Afilipi",
        "num_chapters": 4,
        "chapters": [
            {"chapter_no": 1, "num_verses": 30},
            {"chapter_no": 2, "num_verses": 30},
            {"chapter_no": 3, "num_verses": 21},
            {"chapter_no": 4, "num_verses": 23},
        ],
    },
    {
        "book_name": "Colossians",
        "kikuyu_name": "Akolosai",
        "num_chapters": 4,
        "chapters": [
            {"chapter_no": 1, "num_verses": 29},
            {"chapter_no": 2, "num_verses": 23},
            {"chapter_no": 3, "num_verses": 25},
            {"chapter_no": 4, "num_verses": 18},
        ],
    },
    {
        "book_name": "1 Thessalonians",
        "kikuyu_name": "1 Athesalonike",
        "num_chapters": 5,
        "chapters": [
            {"chapter_no": 1, "num_verses": 10},
            {"chapter_no": 2, "num_verses": 20},
            {"chapter_no": 3, "num_verses": 13},
            {"chapter_no": 4, "num_verses": 18},
            {"chapter_no": 5, "num_verses": 28},
        ],
    },
    {
        "book_name": "2 Thessalonians",
        "kikuyu_name": "2 Athesalonike",
        "num_chapters": 3,
        "chapters": [
            {"chapter_no": 1, "num_verses": 12},
            {"chapter_no": 2, "num_verses": 17},
            {"chapter_no": 3, "num_verses": 18},
        ],
    },
    {
        "book_name": "1 Timothy",
        "kikuyu_name": "1 Timotheo",
        "num_chapters": 6,
        "chapters": [
            {"chapter_no": 1, "num_verses": 20},
            {"chapter_no": 2, "num_verses": 15},
            {"chapter_no": 3, "num_verses": 16},
            {"chapter_no": 4, "num_verses": 16},
            {"chapter_no": 5, "num_verses": 25},
            {"chapter_no": 6, "num_verses": 21},
        ],
    },
    {
        "book_name": "2 Timothy",
        "kikuyu_name": "2 Timotheo",
        "num_chapters": 4,
        "chapters": [
            {"chapter_no": 1, "num_verses": 18},
            {"chapter_no": 2, "num_verses": 26},
            {"chapter_no": 3, "num_verses": 17},
            {"chapter_no": 4, "num_verses": 22},
        ],
    },
    {
        "book_name": "Titus",
        "kikuyu_name": "Tito",
        "num_chapters": 3,
        "chapters": [
            {"chapter_no": 1, "num_verses": 16},
            {"chapter_no": 2, "num_verses": 15},
            {"chapter_no": 3, "num_verses": 15},
        ],
    },
    {
        "book_name": "Philemon",
        "kikuyu_name": "Filemoni",
        "num_chapters": 1,
        "chapters": [
            {"chapter_no": 1, "num_verses": 25},
        ],
    },
    {
        "book_name": "Hebrews",
        "kikuyu_name": "Ahibrania",
        "num_chapters": 13,
        "chapters": [
            {"chapter_no": 1, "num_verses": 14},
            {"chapter_no": 2, "num_verses": 18},
            {"chapter_no": 3, "num_verses": 19},
            {"chapter_no": 4, "num_verses": 16},
            {"chapter_no": 5, "num_verses": 14},
            {"chapter_no": 6, "num_verses": 20},
            {"chapter_no": 7, "num_verses": 28},
            {"chapter_no": 8, "num_verses": 13},
            {"chapter_no": 9, "num_verses": 28},
            {"chapter_no": 10, "num_verses": 39},
            {"chapter_no": 11, "num_verses": 40},
            {"chapter_no": 12, "num_verses": 29},
            {"chapter_no": 13, "num_verses": 25},
        ],
    },
    {
        "book_name": "James",
        "kikuyu_name": "Jakubu",
        "num_chapters": 5,
        "chapters": [
            {"chapter_no": 1, "num_verses": 27},
            {"chapter_no": 2, "num_verses": 26},
            {"chapter_no": 3, "num_verses": 18},
            {"chapter_no": 4, "num_verses": 17},
            {"chapter_no": 5, "num_verses": 20},
        ],
    },
    {
        "book_name": "1 Peter",
        "kikuyu_name": "1 Petero",
        "num_chapters": 5,
        "chapters": [
            {"chapter_no": 1, "num_verses": 25},
            {"chapter_no": 2, "num_verses": 25},
            {"chapter_no": 3, "num_verses": 22},
            {"chapter_no": 4, "num_verses": 19},
            {"chapter_no": 5, "num_verses": 14},
        ],
    },
    {
        "book_name": "2 Peter",
        "kikuyu_name": "2 Petero",
        "num_chapters": 3,
        "chapters": [
            {"chapter_no": 1, "num_verses": 21},
            {"chapter_no": 2, "num_verses": 22},
            {"chapter_no": 3, "num_verses": 18},
        ],
    },
    {
        "book_name": "1 John",
        "kikuyu_name": "1 Johana",
        "num_chapters": 5,
        "chapters": [
            {"chapter_no": 1, "num_verses": 10},
            {"chapter_no": 2, "num_verses": 29},
            {"chapter_no": 3, "num_verses": 24},
            {"chapter_no": 4, "num_verses": 21},
            {"chapter_no": 5, "num_verses": 21},
        ],
    },
    {
        "book_name": "2 John",
        "kikuyu_name": "2 Johana",
        "num_chapters": 1,
        "chapters": [
            {"chapter_no": 1, "num_verses": 13},
        ],
    },
    {
        "book_name": "3 John",
        "kikuyu_name": "3 Johana",
        "num_chapters": 1,
        "chapters": [
            {"chapter_no": 1, "num_verses": 14},
        ],
    },
    {
        "book_name": "Jude",
        "kikuyu_name": "Juda",
        "num_chapters": 1,
        "chapters": [
            {"chapter_no": 1, "num_verses": 25},
        ],
    },
    {
        "book_name": "Revelation",
        "kikuyu_name": "Kũguũrĩrio",
        "num_chapters": 22,
        "chapters": [
            {"chapter_no": 1, "num_verses": 20},
            {"chapter_no": 2, "num_verses": 29},
            {"chapter_no": 3, "num_verses": 22},
            {"chapter_no": 4, "num_verses": 11},
            {"chapter_no": 5, "num_verses": 14},
            {"chapter_no": 6, "num_verses": 17},
            {"chapter_no": 7, "num_verses": 17},
            {"chapter_no": 8, "num_verses": 13},
            {"chapter_no": 9, "num_verses": 21},
            {"chapter_no": 10, "num_verses": 11},
            {"chapter_no": 11, "num_verses": 19},
            {"chapter_no": 12, "num_verses": 17},
            {"chapter_no": 13, "num_verses": 18},
            {"chapter_no": 14, "num_verses": 20},
            {"chapter_no": 15, "num_verses": 8},
            {"chapter_no": 16, "num_verses": 21},
            {"chapter_no": 17, "num_verses": 18},
            {"chapter_no": 18, "num_verses": 24},
            {"chapter_no": 19, "num_verses": 21},
            {"chapter_no": 20, "num_verses": 15},
            {"chapter_no": 21, "num_verses": 27},
            {"chapter_no": 22, "num_verses": 21},
        ],
    },
]

# Build book name mapping
BOOK_NAME_MAPPING = {book["kikuyu_name"]: book["book_name"] for book in BIBLE_BOOKS}

# Build lookup dictionaries for quick access
CHAPTER_VERSE_COUNTS = {}
for book in BIBLE_BOOKS:
    book_name = book["book_name"]
    CHAPTER_VERSE_COUNTS[book_name] = {}
    for chapter in book["chapters"]:
        CHAPTER_VERSE_COUNTS[book_name][chapter["chapter_no"]] = chapter["num_verses"]


def get_book_by_name(book_name: str) -> Optional[Dict]:
    """
    Get book information by name.

    Args:
        book_name: Name of the book (English)

    Returns:
        Book information dictionary or None if not found
    """
    for book in BIBLE_BOOKS:
        if book["book_name"].lower() == book_name.lower():
            return book
    return None


def get_book_by_kikuyu_name(kikuyu_name: str) -> Optional[Dict]:
    """
    Get book information by Kikuyu name.

    Args:
        kikuyu_name: Kikuyu name of the book

    Returns:
        Book information dictionary or None if not found
    """
    for book in BIBLE_BOOKS:
        if book["kikuyu_name"].lower() == kikuyu_name.lower():
            return book
    return None


def get_verse_count(book_name: str, chapter_no: int) -> Optional[int]:
    """
    Get the number of verses in a chapter.

    Args:
        book_name: Name of the book (English)
        chapter_no: Chapter number

    Returns:
        Number of verses or None if not found
    """
    book_chapters = CHAPTER_VERSE_COUNTS.get(book_name)
    if book_chapters:
        return book_chapters.get(chapter_no)
    return None


def is_valid_reference(book_name: str, chapter_no: int, verse_no: int) -> bool:
    """
    Check if a Bible reference is valid.

    Args:
        book_name: Name of the book (English)
        chapter_no: Chapter number
        verse_no: Verse number

    Returns:
        True if the reference is valid, False otherwise
    """
    verse_count = get_verse_count(book_name, chapter_no)
    if verse_count is None:
        return False
    return 1 <= verse_no <= verse_count


def get_verse_id(book_name: str, chapter_no: int, verse_no: int) -> str:
    """
    Generate a unique ID for a verse.

    Args:
        book_name: Name of the book (English)
        chapter_no: Chapter number
        verse_no: Verse number

    Returns:
        Unique verse ID in the format "Book.Chapter.Verse"
    """
    return f"{book_name}.{chapter_no}.{verse_no}"


def get_all_books() -> List[str]:
    """
    Get a list of all book names (English).

    Returns:
        List of book names
    """
    return [book["book_name"] for book in BIBLE_BOOKS]


def get_all_kikuyu_books() -> List[str]:
    """
    Get a list of all Kikuyu book names.

    Returns:
        List of Kikuyu book names
    """
    return [book["kikuyu_name"] for book in BIBLE_BOOKS]


def get_all_chapter_numbers(book_name: str) -> List[int]:
    """
    Get all chapter numbers for a book.

    Args:
        book_name: Name of the book (English)

    Returns:
        List of chapter numbers
    """
    book = get_book_by_name(book_name)
    if book:
        return [chapter["chapter_no"] for chapter in book["chapters"]]
    return []


def get_all_verse_numbers(book_name: str, chapter_no: int) -> List[int]:
    """
    Get all verse numbers for a chapter.

    Args:
        book_name: Name of the book (English)
        chapter_no: Chapter number

    Returns:
        List of verse numbers
    """
    verse_count = get_verse_count(book_name, chapter_no)
    if verse_count:
        return list(range(1, verse_count + 1))
    return []


def english_to_kikuyu_book_name(english_name: str) -> Optional[str]:
    """
    Convert English book name to Kikuyu book name.

    Args:
        english_name: English book name

    Returns:
        Kikuyu book name or None if not found
    """
    for book in BIBLE_BOOKS:
        if book["book_name"].lower() == english_name.lower():
            return book["kikuyu_name"]
    return None


def kikuyu_to_english_book_name(kikuyu_name: str) -> Optional[str]:
    """
    Convert Kikuyu book name to English book name.

    Args:
        kikuyu_name: Kikuyu book name

    Returns:
        English book name or None if not found
    """
    return BOOK_NAME_MAPPING.get(kikuyu_name)


def get_missing_verses(
    parsed_verses: Dict[str, Dict[int, Dict[int, str]]], book_name: str
) -> List[Tuple[int, int]]:
    """
    Get missing verses for a book in the parsed verses.

    Args:
        parsed_verses: Dictionary of parsed verses
        book_name: Name of the book (English)

    Returns:
        List of (chapter_no, verse_no) tuples for missing verses
    """
    missing_verses = []
    book = get_book_by_name(book_name)

    if not book or book_name not in parsed_verses:
        return missing_verses

    for chapter in book["chapters"]:
        chapter_no = chapter["chapter_no"]
        verse_count = chapter["num_verses"]

        if chapter_no not in parsed_verses[book_name]:
            missing_verses.extend(
                [(chapter_no, verse_no) for verse_no in range(1, verse_count + 1)]
            )
            continue

        parsed_chapter = parsed_verses[book_name][chapter_no]
        for verse_no in range(1, verse_count + 1):
            if verse_no not in parsed_chapter:
                missing_verses.append((chapter_no, verse_no))

    return missing_verses


def get_extra_verses(
    parsed_verses: Dict[str, Dict[int, Dict[int, str]]], book_name: str
) -> List[Tuple[int, int]]:
    """
    Get extra verses in the parsed verses that shouldn't exist.

    Args:
        parsed_verses: Dictionary of parsed verses
        book_name: Name of the book (English)

    Returns:
        List of (chapter_no, verse_no) tuples for extra verses
    """
    extra_verses = []

    if book_name not in parsed_verses:
        return extra_verses

    for chapter_no, verses in parsed_verses[book_name].items():
        for verse_no in verses:
            if not is_valid_reference(book_name, chapter_no, verse_no):
                extra_verses.append((chapter_no, verse_no))

    return extra_verses
