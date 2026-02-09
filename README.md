# OCRFactura

Local web application for Mexican retail receipt → facturación. You extract receipt data using **ChatGPT** (upload images there, paste the app's prompt), then paste the JSON into this app to validate, merge batches, and export a single Excel file. No OCR; no APIs or scraping.

This application is in beta and is "AS IS" - No guarantee it will work on your system. If you want to contribute to make this application better, please fork or issue a PR.

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

## Standalone deployment (Windows exe, no Python required)

You can run OCRFactura as a **standalone app** on any Windows PC without installing Python or an IDE. Build once on your dev machine, then copy the built folder to the target PC.

### Step 1: Build the standalone (developer, one time)

On your development machine, from the project root with the virtual environment activated:

**Command Prompt (Windows):**

```cmd
cd /d "d:\Misc Dev\OCRFactura"
.venv\Scripts\activate
pip install -r requirements-build.txt
build.bat
```

**Git Bash:** use `cmd //c build.bat` instead of `build.bat`, or run:

```bash
python -m PyInstaller OCRFactura.spec --noconfirm
```

When the build finishes, the standalone app is in **`dist\OCRFactura`** (inside the project folder). That folder contains everything needed to run the app.

### Step 2: Deploy to the target machine

1. Copy the **entire** `dist\OCRFactura` folder to the computer where the app will run (e.g. USB drive, shared folder, or zip and transfer).
2. Place it where you want (e.g. `C:\Program Files\OCRFactura` or the user's Desktop). Do not rename or remove any files inside the folder.
3. **(Optional)** Create a Desktop shortcut so the user can open the app without a console window:
   - Open the `OCRFactura` folder.
   - Right-click **create-shortcut.ps1** → **Run with PowerShell**.
   - A shortcut named **OCRFactura** will appear on the Desktop.

### Step 3: Run the standalone app

- **From the shortcut (recommended):** Double-click the **OCRFactura** shortcut on the Desktop. The browser opens to the app; no console window. To stop the app, use Task Manager and end **OCRFactura.exe**, or leave it running in the background.
- **From the folder:** Open the `OCRFactura` folder and double-click **OCRFactura.exe**. A console window and the browser will open. Closing the console window stops the app.

Exported Excel files and session data are stored in **`output\`** and **`output\sessions\`** inside that same folder. Give users the **GUIA-USUARIO.md** file in the folder as a short guide.

### What’s in the standalone folder

| Item                  | Purpose                                        |
| --------------------- | ---------------------------------------------- |
| `OCRFactura.exe`      | Main app; double-click to run (shows console). |
| `RunOCRFactura.vbs`   | Used by the shortcut to run without a console. |
| `create-shortcut.ps1` | Run once to create the Desktop shortcut.       |
| `GUIA-USUARIO.md`     | End-user guide (Spanish).                      |
| Other files/DLLs      | Required; do not delete.                       |

## Manual check

1. Run `python -m app.main` and open the URL.
2. Copy the prompt from the page, open ChatGPT, upload 2–3 receipt images, send the prompt.
3. Copy the JSON response (no markdown) into the app and click **Add Batch**.
4. Click **Export Excel**, then open the file from `output/` and optionally use **Visualize**.
