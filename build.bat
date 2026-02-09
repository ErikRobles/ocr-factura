@echo off
REM Build OCRFactura Windows exe (one-folder). Run from project root with venv activated.
REM Output: dist\OCRFactura\OCRFactura.exe — copy the whole OCRFactura folder to the user's PC.

echo Building OCRFactura...
python -m PyInstaller OCRFactura.spec --noconfirm
if errorlevel 1 (
    echo Build failed.
    exit /b 1
)
echo.
echo Done. Run: dist\OCRFactura\OCRFactura.exe
echo Or copy the folder dist\OCRFactura to the user's computer.
exit /b 0
