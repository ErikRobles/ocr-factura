"""
Schema + lightweight validation for ChatGPT batch JSON.

Goal:
- Accept batches of receipt rows returned by ChatGPT (Vision).
- Validate shape + basic field types.
- Normalize common key variants.
- Return (ok, errors, normalized_rows).

NO external deps (no pydantic).
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple


# Canonical keys we want the app to work with internally (aligned to new prompt).
CANON_KEYS = {
    "image_file_name",
    "retailer_name",
    "ticket_number",
    "date",
    "time",
    "amount_total",
    "amount_subtotal",
    "transaction_number",
    "payment_method",
    "cashier",
    "caja",
    "tienda",
    "sucursal",
    "complejo",
    "facturacion_url",
    "facturacion_email",
    "warnings",
}

# Acceptable aliases from ChatGPT output (people will vary keys).
ALIASES = {
    # --- file name ---
    "Image_File_Name": "image_file_name",
    "image": "image_file_name",
    "file": "image_file_name",
    "filename": "image_file_name",

    # --- retailer ---
    "Retailer_Name": "retailer_name",
    "retailer": "retailer_name",
    "store": "retailer_name",
    "merchant": "retailer_name",
    "brand": "retailer_name",
    "Retailer": "retailer_name",

    # --- ticket/folio ---
    "Ticket_or_Folio": "ticket_number",
    "Ticket": "ticket_number",
    "Folio": "ticket_number",
    "folio": "ticket_number",
    "ticket": "ticket_number",
    "ticket_or_folio": "ticket_number",
    "ticket_number": "ticket_number",
    "numero_ticket": "ticket_number",
    "no_ticket": "ticket_number",
    "referencia": "ticket_number",

    # --- date/time ---
    "Date": "date",
    "fecha": "date",
    "Fecha": "date",
    "Time": "time",
    "hora": "time",
    "Hora": "time",

    # --- amounts ---
    "Amount_Total": "amount_total",
    "Total": "amount_total",
    "total": "amount_total",
    "importe_total": "amount_total",
    "monto_total": "amount_total",
    "Amount": "amount_total",

    "Amount_Subtotal": "amount_subtotal",
    "Subtotal": "amount_subtotal",
    "subtotal": "amount_subtotal",
    "importe_subtotal": "amount_subtotal",

    # --- transaction ---
    "Transaction_Number": "transaction_number",
    "transaction": "transaction_number",
    "transaccion": "transaction_number",
    "operacion": "transaction_number",
    "num_operacion": "transaction_number",

    # --- payment ---
    "Payment_Method": "payment_method",
    "payment": "payment_method",
    "metodo_pago": "payment_method",
    "forma_pago": "payment_method",

    # --- cashier / cajero ---
    "Cajero": "cashier",
    "cajero": "cashier",
    "Cashier_Number": "cashier",
    "operador": "cashier",
    "cajera": "cashier",
    "cashier": "cashier",

    # --- caja ---
    "Caja": "caja",
    "caja": "caja",
    "Register_Number": "caja",
    "terminal": "caja",
    "pos": "caja",

    # --- tienda / sucursal / complejo ---
    "Tienda": "tienda",
    "tienda": "tienda",

    "Sucursal": "sucursal",
    "sucursal": "sucursal",
    "Surcursal": "sucursal",  # common misspelling

    "Complejo": "complejo",
    "complejo": "complejo",
    "plaza": "complejo",
    "centro_comercial": "complejo",

    # --- facturación URL ---
    "Facturacion_URL_On_Ticket": "facturacion_url",
    "Facturacion_URL": "facturacion_url",
    "factura_url": "facturacion_url",
    "url_facturacion": "facturacion_url",
    "facturacion_url": "facturacion_url",
    "Facturacion": "facturacion_url",

    # --- facturación email (e.g. Kikos: "Enviar fotografía al correo facturacion@...") ---
    "Facturacion_Email": "facturacion_email",
    "facturacion_email": "facturacion_email",
    "email_facturacion": "facturacion_email",
    "Email_On_Ticket": "facturacion_email",
    "email_on_ticket": "facturacion_email",
    "correo_facturacion": "facturacion_email",

    # --- warnings ---
    "Warnings": "warnings",
    "warning": "warnings",
    "notes": "warnings",  # treat legacy notes as warnings
}


# Minimal required fields for a "valid" row.
# You can relax this to an empty set if you want to accept everything and review later.
REQUIRED_MIN = {"retailer_name", "ticket_number"}


def _is_str_or_empty(v: Any) -> bool:
    return v is None or isinstance(v, str)


def _coerce_str(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, (int, float)):
        # Keep as plain string; downstream can parse if needed
        return str(v)
    if isinstance(v, str):
        return v.strip()
    return str(v).strip()


def normalize_keys(row: Dict[str, Any]) -> Dict[str, Any]:
    """Map aliases -> canonical keys; keep unknown keys under '_extra'."""
    out: Dict[str, Any] = {}
    extra: Dict[str, Any] = {}

    for k, v in row.items():
        canon = ALIASES.get(k, k)
        if canon in CANON_KEYS:
            out[canon] = v
        else:
            extra[k] = v

    if extra:
        out["_extra"] = extra
    return out


def validate_row(row: Any, idx: int) -> Tuple[bool, List[str], Dict[str, Any]]:
    errors: List[str] = []

    if not isinstance(row, dict):
        return False, [f"Row {idx}: expected object/dict, got {type(row).__name__}"], {}

    n = normalize_keys(row)

    # Coerce known fields to strings (keeps merge/export simple)
    for k in list(n.keys()):
        if k in CANON_KEYS:
            n[k] = _coerce_str(n.get(k))

    # Required minimal fields
    for req in REQUIRED_MIN:
        if not n.get(req):
            errors.append(f"Row {idx}: missing '{req}'")

    # Basic type sanity
    for k in CANON_KEYS:
        if k in n and not _is_str_or_empty(n.get(k)):
            errors.append(f"Row {idx}: '{k}' must be a string")

    ok = len(errors) == 0
    return ok, errors, n


def validate_batch(payload: Any) -> Tuple[bool, List[str], List[Dict[str, Any]]]:
    """
    Accept:
      - list[dict]
      - dict with "rows": list[dict]
      - dict with "data": list[dict]
      - dict with {"batch_meta": {...}, "rows": [...]}

    Return:
      (ok, errors, normalized_rows)
    """
    errors: List[str] = []
    rows: Any = payload

    if isinstance(payload, dict):
        if "rows" in payload:
            rows = payload["rows"]
        elif "data" in payload:
            rows = payload["data"]

    if not isinstance(rows, list):
        return False, ["Batch payload must be a list, or an object with 'rows'/'data' list."], []

    normalized: List[Dict[str, Any]] = []
    for i, r in enumerate(rows, 1):
        ok, row_errs, n = validate_row(r, i)
        if not ok:
            errors.extend(row_errs)
        normalized.append(n)  # keep row even if it has errors (so user can review)

    return len(errors) == 0, errors, normalized
