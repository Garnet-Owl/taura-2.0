import argparse
import json
import logging
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Set paths
DATA_DIR = Path("../../data")
RAW_DIR = DATA_DIR / "raw"

# Create necessary directories
RAW_DIR.mkdir(exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(DATA_DIR / "data_collection.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def save_parallel_data(english_texts, kikuyu_texts, output_file, metadata=None):
    """
    Save parallel texts to a CSV file.

    Args:
        english_texts (list): List of English texts
        kikuyu_texts (list): List of Kikuyu texts
        output_file (str): Path to output file
        metadata (dict, optional): Additional metadata to save
    """
    if len(english_texts) != len(kikuyu_texts):
        logger.error(f"Mismatch in number of texts: English ({len(english_texts)}) vs Kikuyu ({len(kikuyu_texts)})")
        return

    # Create DataFrame
    df = pd.DataFrame({"English": english_texts, "Kikuyu": kikuyu_texts})

    # Save to CSV
    df.to_csv(output_file, index=False)
    logger.info(f"Saved {len(df)} parallel texts to {output_file}")

    # Save metadata if provided
    if metadata:
        metadata_file = output_file.with_suffix(".meta.json")
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata to {metadata_file}")


def scrape_parallel_texts(url, english_selector, kikuyu_selector, max_items=None):
    """
    Scrape parallel texts from a website.

    Args:
        url (str): URL to scrape
        english_selector (str): CSS selector for English texts
        kikuyu_selector (str): CSS selector for Kikuyu texts
        max_items (int, optional): Maximum number of items to scrape

    Returns:
        tuple: (english_texts, kikuyu_texts, metadata)
    """
    logger.info(f"Scraping {url}")

    try:
        # Get page content
        response = requests.get(url)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract texts
        english_elements = soup.select(english_selector)
        kikuyu_elements = soup.select(kikuyu_selector)

        # Limit number of items if needed
        if max_items:
            english_elements = english_elements[:max_items]
            kikuyu_elements = kikuyu_elements[:max_items]

        # Extract text content
        english_texts = [elem.get_text().strip() for elem in english_elements]
        kikuyu_texts = [elem.get_text().strip() for elem in kikuyu_elements]

        # Create metadata
        metadata = {
            "source": url,
            "date_collected": time.strftime("%Y-%m-%d %H:%M:%S"),
            "english_selector": english_selector,
            "kikuyu_selector": kikuyu_selector,
            "num_items": len(english_texts),
        }

        logger.info(f"Scraped {len(english_texts)} parallel texts")

        return english_texts, kikuyu_texts, metadata

    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return [], [], {}


def create_csv_template(output_file):
    """
    Create a template CSV file for manual data collection.

    Args:
        output_file (str): Path to output file
    """
    # Create template with instructions
    df = pd.DataFrame(
        {
            "English": [
                "Hello, how are you?",
                "My name is John.",
                "I love Kenya.",
                "What time is it?",
                "Thank you very much.",
                # Add more example sentences here
            ],
            "Kikuyu": [
                "Niatia, ūhoro waku?",
                "",  # Leave empty for translator to fill
                "",
                "",
                "",
                # Empty cells for translations
            ],
        }
    )

    # Save to CSV
    df.to_csv(output_file, index=False)
    logger.info(f"Created template CSV file at {output_file}")


def combine_datasets(input_files, output_file):
    """
    Combine multiple datasets into one.

    Args:
        input_files (list): List of input file paths
        output_file (str): Path to output file
    """
    dfs = []

    for file in input_files:
        try:
            # Determine file type and read accordingly
            if file.endswith(".csv"):
                df = pd.read_csv(file)
            elif file.endswith(".xlsx") or file.endswith(".xls"):
                df = pd.read_excel(file)
            else:
                logger.warning(f"Unsupported file format: {file}")
                continue

            # Check if the required columns exist
            if "English" not in df.columns or "Kikuyu" not in df.columns:
                logger.warning(f"Required columns not found in {file}")
                continue

            # Add source column
            df["source"] = file

            dfs.append(df)
            logger.info(f"Added {len(df)} rows from {file}")

        except Exception as e:
            logger.error(f"Error reading {file}: {e}")

    if not dfs:
        logger.error("No valid datasets to combine")
        return

    # Combine all DataFrames
    combined_df = pd.concat(dfs, ignore_index=True)

    # Remove duplicates
    original_count = len(combined_df)
    combined_df.drop_duplicates(subset=["English", "Kikuyu"], inplace=True)
    logger.info(f"Removed {original_count - len(combined_df)} duplicates")

    # Save to CSV
    combined_df.to_csv(output_file, index=False)
    logger.info(f"Combined dataset with {len(combined_df)} rows saved to {output_file}")


def main():
    """
    Main function to parse arguments and perform data collection.
    """
    parser = argparse.ArgumentParser(description="Collect Kikuyu-English parallel data")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Scraper command
    scraper_parser = subparsers.add_parser("scrape", help="Scrape parallel texts from a website")
    scraper_parser.add_argument("--url", type=str, required=True, help="URL to scrape")
    scraper_parser.add_argument("--english-selector", type=str, required=True, help="CSS selector for English texts")
    scraper_parser.add_argument("--kikuyu-selector", type=str, required=True, help="CSS selector for Kikuyu texts")
    scraper_parser.add_argument("--output", type=str, default=None, help="Output file path")
    scraper_parser.add_argument("--max-items", type=int, default=None, help="Maximum number of items to scrape")

    # Template command
    template_parser = subparsers.add_parser("template", help="Create a template CSV file for manual data collection")
    template_parser.add_argument("--output", type=str, default=None, help="Output file path")

    # Combine command
    combine_parser = subparsers.add_parser("combine", help="Combine multiple datasets into one")
    combine_parser.add_argument("--inputs", type=str, nargs="+", required=True, help="Input file paths")
    combine_parser.add_argument("--output", type=str, default=None, help="Output file path")

    args = parser.parse_args()

    # Default output file
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    if args.command == "scrape":
        # Set default output file if not provided
        if args.output is None:
            args.output = RAW_DIR / f"scraped_{timestamp}.csv"

        # Scrape parallel texts
        english_texts, kikuyu_texts, metadata = scrape_parallel_texts(
            args.url, args.english_selector, args.kikuyu_selector, args.max_items
        )

        # Save to CSV
        if english_texts and kikuyu_texts:
            save_parallel_data(english_texts, kikuyu_texts, args.output, metadata)
        else:
            logger.error("No data collected")

    elif args.command == "template":
        # Set default output file if not provided
        if args.output is None:
            args.output = RAW_DIR / f"template_{timestamp}.csv"

        # Create template
        create_csv_template(args.output)

    elif args.command == "combine":
        # Set default output file if not provided
        if args.output is None:
            args.output = RAW_DIR / f"combined_{timestamp}.csv"

        # Combine datasets
        combine_datasets(args.inputs, args.output)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
