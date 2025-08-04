"""
Pytest configuration file to set up the Python path for all tests.
"""

import sys
from pathlib import Path

# Add the project root to the Python path for all tests
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
