"""
OCRFactura entry point (Option B).
Starts a tiny local web UI for:
- paste ChatGPT JSON batches
- validate + store session
- merge all batches
- export one Excel file

Usage:
  python -m app.main
  python -m app.main --port 5173
"""

import argparse
import sys
from pathlib import Path

# Run from repo root (or exe dir when frozen) so that app and core are importable
if getattr(sys, "frozen", False):
    # PyInstaller: use folder containing exe for output/sessions; don't touch sys.path
    _REPO_ROOT = Path(sys.executable).resolve().parent
else:
    _REPO_ROOT = Path(__file__).resolve().parent.parent
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))

from core.webui import run_webui  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="OCRFactura (Option B): paste ChatGPT JSON batches and export Excel."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5173,
        help="Port for local web UI (default: 5173)",
    )
    args = parser.parse_args()

    run_webui(port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
