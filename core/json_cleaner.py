# core/json_cleaner.py
from __future__ import annotations

import re
from typing import Tuple


_CODE_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE | re.MULTILINE)

# Remove ASCII control chars except tab/newline/carriage return (we handle newline separately)
_BAD_CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

# Smart quotes → normal quotes
SMART_QUOTES = {
    "\u201c": '"',
    "\u201d": '"',
    "\u2018": "'",
    "\u2019": "'",
    "\ufeff": "",  # BOM
}


def _strip_to_json_object(s: str) -> str:
    """
    If the user pasted extra text, try to slice from first '{' to last '}'.
    """
    first = s.find("{")
    last = s.rfind("}")
    if first != -1 and last != -1 and last > first:
        return s[first : last + 1]
    return s


def repair_json_text(raw: str) -> Tuple[str, list[str]]:
    """
    Repairs common ChatGPT JSON paste issues.

    Key repair:
    - Replace literal newlines/carriage returns inside quoted strings with spaces.
      (JSON does NOT allow raw newline in a string.)
    """
    warnings: list[str] = []
    if raw is None:
        return "", ["Empty input"]

    s = str(raw)

    # Normalize smart quotes / BOM
    for bad, good in SMART_QUOTES.items():
        s = s.replace(bad, good)

    # Remove code fences if present
    s = _CODE_FENCE_RE.sub("", s).strip()

    # If they pasted extra stuff around JSON, try to isolate {...}
    s2 = _strip_to_json_object(s)
    if s2 != s:
        warnings.append("Trimmed non-JSON text surrounding the object.")
        s = s2

    # Remove invalid control chars (except \n/\r handled below)
    s = _BAD_CTRL_RE.sub("", s)

    # --- Repair literal newlines inside JSON strings ---
    out = []
    in_string = False
    escape = False

    for ch in s:
        if in_string:
            if escape:
                out.append(ch)
                escape = False
                continue

            if ch == "\\":
                out.append(ch)
                escape = True
                continue

            if ch == '"':
                out.append(ch)
                in_string = False
                continue

            if ch == "\n" or ch == "\r":
                # Replace illegal literal newline with a space.
                out.append(" ")
                continue

            out.append(ch)
        else:
            if ch == '"':
                out.append(ch)
                in_string = True
                escape = False
            else:
                out.append(ch)

    cleaned = "".join(out)

    # Collapse accidental multiple spaces created inside strings (safe)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)

    return cleaned.strip(), warnings
