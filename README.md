# Taura 2.0

Original repo became too messy hit LFS limits, etc; https://github.com/Garnet-Owl/taura

Machine translation model for translating between Kikuyu and English.

The name "taura" is derived from the Kikuyu word "Taũra", which means "Translate".

Project Duration: The project initially started in April 2025, ran for two months, and paused. Resumed in June 2026. A first working version (MVP) is targeted for the end of July 2026, with Phase 1 completion expected by September 2026.

## Features

- FastText-based word embeddings for Kikuyu and English
- Bidirectional translation between Kikuyu and English
- Clean, modular codebase with a focus on maintainability
- Comprehensive test suite

## Prerequisites

- Python 3.12 or higher
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Garnet-Owl/taura-2.0.git
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
4. Install & remove unused packages
   ```bash
   poetry sync
   ```

## Project Structure

The project follows a clean, feature-based architecture:

```
taura-2.0/
├── app/                 # Main application code
│   ├── api/             # API and core functionality
│   │   ├── feature 1, e.g embedd_vectors
│   │   ├── feature 2, etc
│   │   ├── preprocessing/ # Data preprocessing
│   │   └── serve/       # API serving (Fast API)
│   └── tests/           # Test suite
├── models/              # Saved models directory
├── data/                # Data directory
└── scripts/             # Utility scripts
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
