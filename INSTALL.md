# Installation Guide for Taura 2.0

This project uses Poetry for dependency management. Follow these instructions to set up your development environment.

## Prerequisites

- Python 3.8 or higher
- Git

## Installing Poetry

### Windows

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

Add Poetry to your PATH:
- Add `%APPDATA%\Python\Scripts` to your PATH environment variable
- Or use the full path: `%APPDATA%\Python\Scripts\poetry`

### macOS / Linux

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Add Poetry to your PATH (if not done automatically):
```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Project Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/garnet-owl/taura-2.0.git
   cd taura-2.0
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Initialize the project structure:
   ```bash
   poetry run python scripts/init_project.py
   ```

4. Activate the virtual environment:
   ```bash
   poetry shell
   ```

## Verifying Installation

To verify that everything is set up correctly:

```bash
poetry run python -c "import fasttext; print('FastText imported successfully')"
```

## Common Poetry Commands

- Add a new dependency:
  ```bash
  poetry add package-name
  ```

- Add a development dependency:
  ```bash
  poetry add --group dev package-name
  ```

- Update dependencies:
  ```bash
  poetry update
  ```

- Run a script:
  ```bash
  poetry run python your_script.py
  ```

- Run tests:
  ```bash
  poetry run pytest
  ```

- Export requirements.txt (if needed):
  ```bash
  poetry export -f requirements.txt --output requirements.txt
  ```

## Troubleshooting

### FastText Installation Issues

If you encounter issues installing FastText, you might need to install build tools:

- **Windows**: Install Visual C++ Build Tools
- **Linux**: `sudo apt-get install build-essential`
- **macOS**: `xcode-select --install`

### Poetry Version Conflicts

If you encounter version conflicts:

```bash
poetry lock --no-update
poetry install
```
