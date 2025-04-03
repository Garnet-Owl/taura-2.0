# Taura 2.0

Machine translation model for translating between Kikuyu and English.

The name "taura" is derived from the Kikuyu word "Taũra", which means "Translate".

## Features

- FastText-based word embeddings for Kikuyu and English
- Bidirectional translation between Kikuyu and English
- Clean, modular codebase with a focus on maintainability
- Comprehensive test suite

## Prerequisites

- Python 3.8 or higher
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/taura-2.0.git
   cd taura-2.0
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

## Project Structure

The project follows a clean, feature-based architecture:

```
taura-2.0/
├── app/                 # Main application code
│   ├── api/             # API and core functionality
│   │   ├── embedding/   # FastText embedding generation
│   │   ├── translation/ # Translation core functionality
│   │   ├── preprocessing/ # Data preprocessing
│   │   └── serve/       # API serving
│   └── tests/           # Test suite
├── models/              # Saved models directory
├── data/                # Data directory
└── scripts/             # Utility scripts
```

## Usage

### Training Embedding Models

```bash
poetry run python scripts/train_embeddings.py --source data/raw/kikuyu_english_pairs.csv
```

### Translating Text

```bash
poetry run python -m app.api.serve.cli translate "Nĩndakena gũkuona" --source kikuyu --target english
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black .
poetry run isort .
```

### Type Checking

```bash
poetry run mypy app
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
