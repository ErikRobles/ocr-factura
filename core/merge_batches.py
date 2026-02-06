"""
Merge multiple ChatGPT batches into a single list of normalized rows.

- Accepts normalized rows (dicts) returned from validate_batch().
- De-dupes using a stable key:
    1) image_file_name
    2) retailer_name + ticket_number
    3) retailer + (amount_total/subtotal) + date + time
- When duplicates occur, merges field-by-field (keeps most complete values).
- Returns (merged_rows, warnings).
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _norm(v: Any) -> str:
    return ("" if v is None else str(v)).strip()


def _filled_count(row: Dict[str, Any]) -> int:
    # Count non-empty canonical fields (ignore _extra)
    return sum(1 for k, v in row.items() if k != "_extra" and _norm(v) != "")


def _best_amount(row: Dict[str, Any]) -> str:
    return _norm(row.get("amount_total")) or _norm(row.get("amount_subtotal"))


def _dedupe_key(row: Dict[str, Any]) -> str:
    """
    Prefer image_file_name if present (best unique key).
    Otherwise fall back to:
      - retailer + ticket_number
      - retailer + amount + date + time
    """
    img = _norm(row.get("image_file_name"))
    if img:
        return f"img::{img.lower()}"

    retailer = _norm(row.get("retailer_name")).lower()
    ticket = _norm(row.get("ticket_number")).lower()
    if retailer and ticket:
        return f"rt::{retailer}|{ticket}"

    amount = _best_amount(row)
    date = _norm(row.get("date"))
    time = _norm(row.get("time"))

    return f"cmp::{retailer}|{amount}|{date}|{time}"


def _merge_two_rows(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge b into a, choosing the "better" value per field:
    - Prefer longer non-empty strings (usually contains more detail)
    - If one is empty, take the other
    - Merge _extra dictionaries
    """
    out = dict(a)

    # Merge normal fields
    for k, vb in b.items():
        if k == "_extra":
            continue

        va = out.get(k, "")
        sa = _norm(va)
        sb = _norm(vb)

        if not sa and sb:
            out[k] = vb
            continue

        if sa and sb:
            # Prefer the more informative value
            if len(sb) > len(sa):
                out[k] = vb

    # Merge _extra
    extra_a = a.get("_extra") if isinstance(a.get("_extra"), dict) else {}
    extra_b = b.get("_extra") if isinstance(b.get("_extra"), dict) else {}
    merged_extra = dict(extra_a)
    for k, v in extra_b.items():
        # don't overwrite existing unless empty
        if k not in merged_extra or _norm(merged_extra.get(k)) == "":
            merged_extra[k] = v
    if merged_extra:
        out["_extra"] = merged_extra

    return out


def merge_batches(
    batches: List[Any],
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Merge batches -> merged_rows, warnings

    batches may be:
      - List[List[Dict[str, Any]]]
      - List[Dict[str, Any]]   (single batch accidentally passed)
    """
    warnings: List[str] = []
    merged_map: Dict[str, Dict[str, Any]] = {}

    # Normalize input shape to List[List[Dict]]
    normalized_batches: List[List[Dict[str, Any]]] = []
    if not batches:
        return [], []

    # If first element is a dict, treat as a single batch already flattened
    if isinstance(batches[0], dict):
        normalized_batches = [batches]  # type: ignore[assignment]
    else:
        normalized_batches = batches  # type: ignore[assignment]

    for bi, rows in enumerate(normalized_batches, 1):
        if not rows:
            continue

        for ri, row in enumerate(rows, 1):
            if not isinstance(row, dict):
                warnings.append(f"Batch {bi} row {ri}: skipped (not an object).")
                continue

            key = _dedupe_key(row)

            if key not in merged_map:
                merged_map[key] = row
                continue

            existing = merged_map[key]
            merged = _merge_two_rows(existing, row)

            # If merged result differs, note it
            if _filled_count(merged) > _filled_count(existing):
                warnings.append(f"Batch {bi} row {ri}: duplicate '{key}' merged (added fields).")
            else:
                warnings.append(f"Batch {bi} row {ri}: duplicate '{key}' merged (no improvements).")

            merged_map[key] = merged

    merged_rows = list(merged_map.values())

    # Optional: stable sort for human readability
    def _sort_key(r: Dict[str, Any]):
        retailer = _norm(r.get("retailer_name")).upper()
        date = _norm(r.get("date"))
        img = _norm(r.get("image_file_name"))
        return (retailer, date, img)

    merged_rows.sort(key=_sort_key)
    return merged_rows, warnings
