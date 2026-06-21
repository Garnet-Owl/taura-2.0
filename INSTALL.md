# Installation Guide for Taura 2.0

This project uses `uv` for dependency and environment management. Follow these instructions to set up your development environment.

## Prerequisites

- Python 3.12 or higher
- Git

## Installing uv

`uv` is an extremely fast Python package and project manager.

### Windows

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### macOS / Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Project Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/garnet-owl/taura-2.0.git
   cd taura-2.0
   ```

2. Synchronize and set up the virtual environment:
   ```bash
   uv sync
   ```
   This automatically creates a `.venv` directory, installs the specified Python version if missing, and installs all project and development dependencies.

---

## Development Setup

1. Set up pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```

2. Run the test suite:
   ```bash
   uv run pytest
   ```

---

## Common uv Commands

- Add a new dependency:
  ```bash
  uv add package-name
  ```

- Add a development dependency:
  ```bash
  uv add --group dev package-name
  ```

- Update dependencies:
  ```bash
  uv lock --upgrade
  ```

- Run a script inside the virtual environment:
  ```bash
  uv run python your_script.py
  ```

---

## Troubleshooting

### FastText Installation Issues

Under `uv`, `fasttext-wheel` is specified directly, which provides precompiled binaries for most platforms and should install without requiring local compilers. If you still encounter compile errors during installation:

- **Windows**: Install Visual C++ Build Tools
- **Linux**: `sudo apt-get install build-essential`
- **macOS**: `xcode-select --install`
