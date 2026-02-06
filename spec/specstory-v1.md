# OCRFactura — Spec Story v1 (ChatGPT Batch → JSON → Merge → Excel)

## Problem

Receipts/tickets from Mexican retailers vary heavily in layout and labeling. OCR + heuristics are brittle:

- Ticket/folio labels differ by retailer
- Amounts and dates appear in inconsistent formats
- Skewed images create false positives (RFC mistaken as ticket number, etc.)

We do not solve generalized receipt OCR locally.

## Solution (Option B)

A local tool that:

1. Lets the user post **batches of 3–5 receipt images into ChatGPT** manually (using the prompt provided in the app)
2. User pastes the **JSON-only response** into the local web UI
3. Tool repairs common paste issues (e.g. literal newlines in strings), validates each batch, merges all batches, de-dupes, and exports **one Excel file**
4. User can **visualize** exported Excel data in a dark-themed dashboard (new tab)

No APIs. No browser automation. No scraping. Manual interaction with ChatGPT only.

## Users

- People who do monthly invoicing from retail receipts
- Already paying for ChatGPT (Plus/Pro) and willing to paste JSON batches
- Not a commercial product

## Core User Flow

1. User opens the local web UI (e.g. `python -m app.main`; default port 5173).
2. User copies the **ChatGPT prompt** shown on the page, then posts 3–5 receipt images to ChatGPT.
3. ChatGPT returns a single JSON object (`batch_meta` + `rows`).
4. User pastes the JSON into the app and clicks **Add Batch**.
5. App repairs JSON if needed (e.g. newlines inside strings), then validates:
   - Payload is a list or object with `rows` or `data`
   - Each row is an object with at least `retailer_name` and `ticket_number` (REQUIRED_MIN)
   - Keys are normalized (aliases mapped to canonical names, e.g. `notes` → `warnings`, `ticket_or_folio` → `ticket_number`)
6. App appends the batch to a **session file** (one file per day: `output/sessions/session_YYYY-MM-DD.jsonl`).
7. User repeats steps 2–4 until all receipts are processed.
8. User clicks **Export Excel**. App merges all batches, de-dupes, converts to rows, and writes one `.xlsx` to `output/` (e.g. `MonthlyInvoicing_YYYY-MM_HHMMSS.xlsx`).
9. If any Excel files exist in `output/`, the **Visualize** button is enabled. User clicks it to open a dashboard (new tab) showing the Extracted sheet data grouped by retailer; if multiple Excel files exist, the app asks which one to open.

## Output Columns (Excel)

Sheets: **Extracted** (all rows), **Needs_Review** (rows missing key fields or low confidence), **Run_Summary** (counts, timestamp, warnings).

Column order (aligned with `core/excel_export.py`):

- Retailer_Name
- Ticket_or_Folio
- Ticket_or_Folio_Candidates
- Amount_Total
- Amount_Subtotal
- Currency
- Payment_Method
- Date
- Time
- Transaction_Number
- Sucursal
- Tienda
- Caja
- Cajero
- Facturacion_URL_On_Ticket
- Facturacion_Email
- Facturacion_Method
- Facturacion_Notes
- OCR_Quality
- Confidence_Score
- Missing_Fields
- Warnings
- Image_File_Name
- Image_File_Path
- Image_Open_Link (clickable when path exists)

Explicitly excluded from Excel:

- RFC
- Address
- IVA column
- Product list

## Data Model

- Each extracted object corresponds to one receipt image.
- Session: append-only JSONL; each line is an object with `type: "batch"`, `timestamp`, and `items` (list of normalized row dicts).
- Merge step: combine all batches into a single list of rows. De-dupe key order:
  1. `image_file_name` (if present) → `img::{filename}`
  2. Else `retailer_name` + `ticket_number` → `rt::{retailer}|{ticket}`
  3. Else composite: retailer + amount + date + time → `cmp::...`
- When duplicates occur: merge field-by-field (prefer longer non-empty value); warnings are emitted. Rows are sorted by retailer, date, image filename for export.

## Validation Rules

- Payload: either a **list** of row objects, or a **dict** with key `rows` or `data` (list). Supports `{"batch_meta": {...}, "rows": [...]}`.
- Each row: must be a dict. Canonical keys (after alias normalization) include: image_file_name, retailer_name, ticket_number, date, time, amount_total, amount_subtotal, transaction_number, payment_method, cashier, caja, tienda, sucursal, complejo, facturacion_url, facturacion_email, warnings.
- **REQUIRED_MIN** for a valid row: `retailer_name`, `ticket_number`. Missing either produces a validation error (batch still stored; user can fix and re-paste or review in Excel).
- Amounts, dates, and other fields are coerced to strings; confidence default 0.5 if missing.
- Needs_Review: rows with missing retailer_name, ticket_or_folio, or amount_total, or confidence_score &lt; 0.5, or ocr_quality "Poor".

## Acceptance Criteria

1. User can paste a batch JSON and see success or validation errors plus a preview (status + JSON in pre).
2. App persists batches in a per-day session file so user can close/reopen and continue.
3. Export produces one Excel file with Extracted, Needs_Review, and Run_Summary sheets and the defined columns.
4. Needs_Review includes rows missing key fields (retailer_name, ticket_or_folio, amount_total) or low confidence.
5. De-dupe works deterministically (image_file_name first, then retailer+ticket_number, then composite); merge keeps the more complete value per field.
6. Visualize: button disabled when no Excel files in `output/`; when one file, opens `/view?file=...` in new tab; when multiple, user picks file then opens dashboard.
7. UI: dark theme, mobile-friendly, centered layout; ChatGPT prompt is visible and copyable on the main page.

## Non-Goals

- Fully automated interaction with ChatGPT
- OCR, image preprocessing, skew correction
- Full SAT CFDI generation or invoicing submission
- Building a retailer-agnostic ticket-number extractor

## Implementation (Current)

**Active modules:**

- **app/main.py** — Entry point; runs Flask web UI (default port 5173).
- **core/webui.py** — Flask app: `/` (home: paste JSON, prompt, Add Batch, Refresh Status, Export Excel, Visualize); `/api/status`, `/api/add-batch`, `/api/export`, `/api/excel-files`, `/api/excel-data?file=`, `/view?file=` (visualize dashboard); session handling; `_to_rows`, `_list_excel_files`, `_read_excel_extracted`, `_view_dashboard_html`.
- **core/chatgpt_batch_schema.py** — Validation and key normalization; accepts list or object with `rows`/`data`; REQUIRED_MIN = {retailer_name, ticket_number}; CANON_KEYS and ALIASES (including facturacion_email, payment_method, notes→warnings).
- **core/merge_batches.py** — Merge batches, de-dupe (image_file_name → retailer+ticket_number → composite), field-merge (prefer longer non-empty), sort by retailer/date/filename.
- **core/excel_export.py** — Write .xlsx with Extracted, Needs_Review, Run_Summary; column order and _row_to_dict from ExtractedRow.
- **core/models.py** — ExtractedRow dataclass; is_low_confidence_or_missing_key_fields().
- **core/json_cleaner.py** — Repair pasted JSON (smart quotes, code fences, literal newlines inside strings, trim to first `{` to last `}`).

**Retired (deprecated/ removed):**

- OCR pipeline: ocr_tesseract, pipeline, extract, preprocess, retailer_guess. Not used by the ChatGPT-batch workflow.

## Test Plan

- Unit tests (if added): schema validation (good/bad JSON, required keys), merge behavior and de-dupe, export column mapping.
- Manual tests: 3 receipts → 1 batch → export; multiple batches → export; duplicates pasted → verify merge + warning; Visualize with 0, 1, and multiple Excel files; facturacion_email present in JSON → appears in Excel and dashboard.
