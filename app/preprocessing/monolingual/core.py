"""
Build large monolingual corpora from the Bible PDFs.

The Bible PDFs contain ~31,000 verses per language. We extract ALL verse text
from both PDFs and write them to the monolingual training files used by FastText.
This gives us rich word-level co-occurrence data without requiring web scraping.

Appends to existing monolingual files — safe to run multiple times.
"""

import fitz  # PyMuPDF
from pathlib import Path

from app.shared import config
from app.api.preprocessing import normalize_text
from app.shared.logger import setup_logger

logger = setup_logger(__name__)

DATA_DIR = Path("data")
PDF_DIR = DATA_DIR

_PDF_MAP = {
    "kikuyu": DATA_DIR / "Kikuyu_Bible_all.pdf",
    "english": DATA_DIR / "English_Bible_all.pdf",
}

_MONOLINGUAL_MAP = {
    "kikuyu": Path(config.TRAIN_KI_TXT),
    "english": Path(config.TRAIN_EN_TXT),
}


def extract_sentences_from_pdf(pdf_path: Path) -> list[str]:
    """Extract all non-trivial lines of text from a Bible PDF."""
    sentences: list[str] = []
    with fitz.open(str(pdf_path)) as doc:
        for page in doc:
            for line in page.get_text().splitlines():
                line = line.strip()
                # Keep only lines that look like actual verse text:
                # at least 20 chars, not pure numbers / headers / page refs
                if (
                    len(line) >= 20
                    and not line.replace(".", "").replace(" ", "").isdigit()
                ):
                    sentences.append(line)
    return sentences


def main() -> None:
    for lang, pdf_path in _PDF_MAP.items():
        if not pdf_path.exists():
            logger.warning("PDF not found: %s — skipping %s", pdf_path, lang)
            continue

        out_path = _MONOLINGUAL_MAP[lang]
        out_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Extracting %s text from %s ...", lang, pdf_path.name)
        sentences = extract_sentences_from_pdf(pdf_path)
        logger.info("Extracted %d raw lines from %s PDF", len(sentences), lang)

        written = 0
        with open(out_path, "a", encoding="utf-8") as f:
            for sentence in sentences:
                normalized = normalize_text(sentence)
                if normalized:
                    f.write(f"{normalized}\n")
                    written += 1

        logger.info("Appended %d normalized sentences to %s", written, out_path)


if __name__ == "__main__":
    main()
