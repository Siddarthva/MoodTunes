"""
conftest.py — pytest configuration for the MoodTunes backend.
Ensures the backend package root (C:\nndl\backend) is on sys.path so that
import app.* works regardless of which directory pytest is invoked from.
"""
import sys
from pathlib import Path

# backend/ directory (parent of this conftest.py's tests/ directory)
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
