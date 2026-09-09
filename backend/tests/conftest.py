"""Pytest configuration and environment setup."""

import sys
from pathlib import Path

# Ensure src/ is on sys.path for test runners
src_path = Path(__file__).resolve().parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
