"""Configure pytest environment."""

import sys
from pathlib import Path

# Add project root directory to Python path
# This allows imports from 'app' in test files
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
