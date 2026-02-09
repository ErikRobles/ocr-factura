"""
Launcher for PyInstaller build. Entry point so the built exe is named OCRFactura.
"""
from app.main import main

if __name__ == "__main__":
    raise SystemExit(main())
