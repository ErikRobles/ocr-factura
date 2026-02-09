"""
Base directory for the app: when run as PyInstaller exe, use the folder
containing the exe (so output/ and sessions live next to it); otherwise
use the repo root.
"""
import sys
from pathlib import Path


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent
