# OCRFactura

Local web application for Mexican retail receipt → facturación. You extract receipt data using **ChatGPT** (upload images there, paste the app's prompt), then paste the JSON into this app to validate, merge batches, and export a single Excel file. No OCR; no APIs or scraping.

**Status:** Option B in use (ChatGPT batch → JSON → merge → Excel).

## What it does

- **Web UI** (Flask, default port 5173): paste ChatGPT JSON batches, validate, add to session, merge all batches, export one `.xlsx`.
- **Session storage**: one file per day under `output/sessions/session_YYYY-MM-DD.jsonl`.
- **Excel export**: one workbook with sheets **Extracted**, **Needs_Review**, **Run_Summary**; clickable links to image paths when available.
- **Visualize**: open a dark-themed dashboard of the exported Excel data (by retailer).
- **Prompt**: the UI shows a copy-paste prompt to use in ChatGPT so it returns strict JSON (`batch_meta` + `rows`) for batch processing.

## Setup

1. **Python 3.10+** and a virtual environment (recommended):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   (No Tesseract or OCR setup required for the current flow.)

## Run

From the project root:

```bash
python -m app.main
```

Optional port:

```bash
python -m app.main --port 5173
```

Then open the URL shown in the terminal (e.g. http://127.0.0.1:5173).

## User flow

1. Open the local web UI (`python -m app.main`).
2. Copy the **ChatGPT prompt** from the page, then in ChatGPT upload 3–5 receipt images and send the prompt.
3. ChatGPT returns a single JSON object (`batch_meta` + `rows`). Copy it (JSON only).
4. Paste the JSON into the app and click **Add Batch**. Repeat for more batches.
5. Click **Export Excel** to merge all batches, de-dupe, and write one `.xlsx` to `output/`.
6. Use **Visualize** to open a dashboard of the exported data (if any Excel file exists in `output/`).

## Tests

From the project root:

```bash
pip install pytest
python -m pytest tests/ -v
```

Tests cover amount normalization, date/amount/transaction extraction patterns, and `extract_from_text` behavior (used by legacy path; ChatGPT flow uses schema validation in `core/chatgpt_batch_schema.py`).

## Project structure

```
OCRFactura/
  app/
    main.py              # Entry point: runs web UI (Flask)
  core/
    webui.py             # Flask app: paste JSON, Add Batch, Export Excel, Visualize
    chatgpt_batch_schema.py  # Validate and normalize ChatGPT batch JSON
    merge_batches.py     # Merge sessions, de-dupe, pick best fields
    json_cleaner.py      # Repair pasted JSON (e.g. literal newlines in strings)
    excel_export.py     # .xlsx with Extracted / Needs_Review / Run_Summary
    models.py           # ExtractedRow and shared data structures
    retailer_guess.py   # Retailer normalization / registry
    extract.py          # Legacy regex extraction (optional)
  output/
    sessions/           # session_YYYY-MM-DD.jsonl
  tests/
    test_amount_normalization.py
    test_extract_patterns.py
  requirements.txt
  OCRFactura.spec   # PyInstaller spec for Windows exe
  run_ocrfactura.py # Launcher for built exe
  build.bat         # Build script for Windows exe
  create-shortcut.ps1  # Create Desktop shortcut (no console)
  RunOCRFactura.vbs    # Launcher used by shortcut (no console)
  GUIA-USUARIO.md      # Short end-user guide (include in dist folder)
  spec/
```

## Distribution (Windows exe)

To give the app to someone who does not have Python installed:

1. **Build the exe** (on your dev machine, from project root with venv activated):

   ```bash
   pip install -r requirements-build.txt
   build.bat
   ```

   Or: `python -m PyInstaller OCRFactura.spec --noconfirm`

2. **Copy the folder** `dist\OCRFactura` to the user's computer. The folder contains:
   - `OCRFactura.exe` — run directly to see the console (status; closing it stops the app)
   - `RunOCRFactura.vbs` — used by the shortcut to start the app **without** showing the console
   - `create-shortcut.ps1` — run once to create a Desktop shortcut (shortcut uses the VBS, so no console)
   - `GUIA-USUARIO.md` — short end-user guide (give this to the user)
   - Other DLLs and files (required; do not delete)

3. **Desktop shortcut (recommended):**  
   In the `OCRFactura` folder, right-click `create-shortcut.ps1` → **Run with PowerShell**.  
   The shortcut runs the app via `RunOCRFactura.vbs`, so **no console window** appears—only the browser opens.

4. **User experience:**
   - **Shortcut:** Double-click the Desktop shortcut → browser opens; no terminal. To stop the app they use Task Manager (end `OCRFactura.exe`) or close the browser and leave it running in the background.
   - **Exe directly:** Double-click `OCRFactura.exe` → console window + browser. Closing the console stops the app. Sessions and exported Excel files are in `output/` and `output/sessions/` inside that folder.

## Manual check

1. Run `python -m app.main` and open the URL.
2. Copy the prompt from the page, open ChatGPT, upload 2–3 receipt images, send the prompt.
3. Copy the JSON response (no markdown) into the app and click **Add Batch**.
4. Click **Export Excel**, then open the file from `output/` and optionally use **Visualize**.
