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

   The web UI needs **Flask** and **openpyxl**. If `requirements.txt` does not list Flask, install it:

   ```bash
   pip install flask openpyxl
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
  spec/
```

## Manual check

1. Run `python -m app.main` and open the URL.
2. Copy the prompt from the page, open ChatGPT, upload 2–3 receipt images, send the prompt.
3. Copy the JSON response (no markdown) into the app and click **Add Batch**.
4. Click **Export Excel**, then open the file from `output/` and optionally use **Visualize**.
