#!/usr/bin/env python3
"""
Initialize the project structure for taura-2.0.
Creates necessary directories and placeholder files.
"""

import os
import sys
from pathlib import Path


def create_directory(path):
    """Create a directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)
    print(f"Created directory: {path}")
    
    # Add a .gitkeep file to ensure empty directories are tracked by git
    gitkeep = path / ".gitkeep"
    if not gitkeep.exists():
        with open(gitkeep, "w") as f:
            f.write("# This file ensures git tracks this empty directory\n")


def create_init_file(path):
    """Create an empty __init__.py file if it doesn't exist."""
    init_file = path / "__init__.py"
    if not init_file.exists():
        with open(init_file, "w") as f:
            f.write("# This file makes this directory a Python package\n")
        print(f"Created file: {init_file}")


def main():
    """Main function to initialize the project structure."""
    # Get the project root directory
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    
    # Define directories to create
    directories = [
        # Main application structure
        project_root / "app",
        project_root / "app/api",
        project_root / "app/api/embedding",
        project_root / "app/api/translation",
        project_root / "app/api/preprocessing",
        project_root / "app/api/data",
        project_root / "app/api/serve",
        
        # Test structure
        project_root / "app/tests",
        project_root / "app/tests/unit",
        project_root / "app/tests/unit/embedding",
        project_root / "app/tests/unit/translation",
        project_root / "app/tests/unit/preprocessing",
        project_root / "app/tests/unit/data",
        project_root / "app/tests/integration",
        
        # Data directories
        project_root / "data",
        project_root / "data/raw",
        project_root / "data/processed",
        project_root / "data/embeddings",
        
        # Model directories
        project_root / "models",
        project_root / "models/fasttext",
        project_root / "models/alignment",
        
        # Config directories
        project_root / "configs",
        
        # Scripts directory
        project_root / "scripts",
    ]
    
    # Create directories and __init__.py files
    for directory in directories:
        create_directory(directory)
        
        # Only create __init__.py in Python package directories
        if "app" in str(directory):
            create_init_file(directory)
    
    print("\nProject structure initialized successfully!")
    print(f"Project root: {project_root}")
    print("\nNext steps:")
    print("1. Install dependencies:  poetry install")
    print("2. Activate environment:  poetry shell")
    print("3. Start development!")


if __name__ == "__main__":
    main()
