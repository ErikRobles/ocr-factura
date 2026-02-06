# OCRFactura

Local Windows desktop application that extracts Mexican retail ticket data from receipt images and generates a monthly facturación Excel spreadsheet.

**Status:** V1 in development (Milestone 1 complete)

## What it does

- Reads all `.jpg`, `.jpeg`, `.png` images from a **single folder** (no recursion).
- Runs **local OCR** (Tesseract), with optional preprocessing (grayscale, contrast).
- Extracts fields: retailer, ticket/folio, date, total amount, payment method, facturación URL/email, etc.
- Outputs a **.xlsx** workbook with:
  - **Extracted** — one row per image, sorted by retailer then date then filename.
  - **Needs_Review** — rows with missing key fields or low confidence.
  - **Run_Summary** — counts and run info.
- Clickable hyperlinks to the original image path in Excel.

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

3. **Tesseract OCR** must be installed on the system and on `PATH`:
   - Download: [GitHub - tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)
   - Or: `winget install UB-Mannheim.TesseractOCR`
   - For Spanish + English: install the `spa` and `eng` language data (often included).

## Run (CLI — Milestone 1)

From the project root (`OCRFactura`):

```bash
python -m app.main "C:\path\to\folder\with\receipt\images"
```

Optional: specify output file:

```bash
python -m app.main "C:\path\to\folder" --output "C:\path\to\output\MonthlyInvoicing.xlsx"
```

- Only images with extensions `.jpg`, `.jpeg`, `.png` in that folder are processed.
- Default output: `MonthlyInvoicing_YYYY-MM_HHMMSS.xlsx` in the same folder.

## Tests

From the project root:

```bash
pip install pytest
python -m pytest tests/ -v
```

Unit tests cover:

- Amount normalization (`$1,234.50` → `1234.50`).
- Amount parsing (total, subtotal, IVA).
- Date parsing (dd/mm/yyyy, yyyy-mm-dd).
- Transaction number (TR: xxx).
- Ticket/folio and payment method extraction.
- Facturación URL/email detection.
- Full `extract_from_text` with empty and sample text.

## Project structure

```
OCRFactura/
  app/
    main.py          # CLI entry
    ui.py            # (Milestone 3: desktop UI)
  core/
    pipeline.py      # folder → OCR → extract → rows
    preprocess.py    # image preprocessing
    ocr.py           # Tesseract OCR (modular for PaddleOCR later)
    extract.py       # regex + heuristics extraction
    retailer_guess.py
    excel_export.py  # .xlsx with 3 sheets and hyperlinks
    models.py        # ExtractedRow dataclass
  tests/
    test_amount_normalization.py
    test_extract_patterns.py
  requirements.txt
  spec/
```

## Manual testing before Milestone 2

1. Put 2–3 receipt images (JPG/PNG) in a folder.
2. Run: `python -m app.main "path\to\that\folder"`.
3. Open the generated .xlsx:
   - **Extracted**: one row per image; key columns filled where OCR could read them.
   - **Needs_Review**: rows with missing/low-confidence data.
   - **Run_Summary**: total processed, needs-review count.
   - Click **Image_Open_Link** (or Image_File_Path) to open the original image.
4. If Tesseract is not on PATH, fix installation or add its directory to `PATH`.

Next: **Milestone 2** — improved preprocessing (deskew, contrast, shadow reduction), confidence scoring.
