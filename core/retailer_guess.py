"""
Normalize retailer name from OCR text (best guess, e.g. CHEDRAUI, WALMART).

Goals:
- Prefer strong identifiers (RFC) when present.
- Handle common OCR variants (e.g. CHEDRAUT).
- Avoid false positives from product lines by focusing on:
  - first N lines (header area)
  - whole-text RFC scan (RFC can appear lower)
- Return "" if no confident guess.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Dict, List, Tuple


def _norm(s: str) -> str:
    """Uppercase + remove accents/diacritics for stable matching."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.upper()


# Strong identifiers (RFCs etc.) – these should override everything
RETAILER_RFC_MAP: Dict[str, str] = {
    "TCH850701": "CHEDRAUI",
    "ITA060511": "ITALCAFE",
    "HAM111006K69": "H&M",
    # Add more RFCs here as you learn them:
    # "WME920113": "WALMART",
}

("ITALCAFE", [
    r"\bITALCAFE\b",
    r"\bITAL\s*CAFE\b",
    r"\bITA060511\w*\b",     # RFC prefix variants
    r"\bITALIANNIS\b",       # many receipts show brand/store name
]),



# Keyword patterns (include common OCR misspellings)
# Patterns are run against normalized uppercase text.
RETAILER_PATTERNS: List[Tuple[str, List[str]]] = [
    (
        "CHEDRAUI",
        [
            r"\bCHEDRAUI\b",
            r"\bCHEDRAUT\b",  # OCR variant you already saw
            r"\bCHEDRAU[I1]\b",
            r"\bTIENDAS\s+CHEDRAU\w*\b",
            r"\bCH[E3]DRAU[I1]\b",
        ],
    ),
    (
        "H&M",
        [
            r"\bH\s*&\s*M\b",
            r"\bHENNES\b",
            r"\bMAURITZ\b",
            r"\bHAM\d{6,}\b",  # RFC-ish prefix seen on H&M tickets
        ],
    ),
]

# Optional: known retailers list (not used directly for matching,
# but can be used later for UI drop-downs / validation).
KNOWN_RETAILERS: List[str] = [
    "CHEDRAUI",
    "WALMART",
    "WAL MART",
    "SORIANA",
    "OXXO",
    "ELEKTRA",
    "BODEGA",
    "AURRERA",
    "BODEGA AURRERA",
    "COMERCIAL MEXICANA",
    "LA COMER",
    "HEB",
    "CITY MARKET",
    "COSTCO",
    "SAM'S",
    "SAMS",
    "LIVERPOOL",
    "PALACIO DE HIERRO",
    "SANBORNS",
    "FARMACIA GUADALAJARA",
    "FARMACIA DEL AHORRO",
    "SIMILAR",
    "MEGA",
    "CIRCUITO K",
    "CALIMAX",
    "CASA LEY",
]


def _first_lines(text: str, n: int = 20) -> str:
    """Take first N non-empty lines (header area) to reduce product noise."""
    lines: List[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        lines.append(line)
        if len(lines) >= n:
            break
    return "\n".join(lines)


def normalize_retailer_name(text: str) -> str:
    """
    Return a best-guess retailer name, or "" if unknown.

    Strategy:
    1) RFC-based detection (scan full text) - strongest signal.
    2) Score-based keyword patterns on header lines (first N lines).
       This reduces false positives from product lists below.
    """
    if not text:
        return ""

    t_full = _norm(text)

    # 1) RFC-based detection (highest priority, scan full text)
    for rfc, name in RETAILER_RFC_MAP.items():
        if rfc and rfc in t_full:
            return name

    # 2) Pattern scoring on header-only text (reduces product noise)
    header = _first_lines(text, n=25)
    t_header = _norm(header)

    best_name = ""
    best_score = 0

    for name, patterns in RETAILER_PATTERNS:
        score = 0
        for pat in patterns:
            score += len(re.findall(pat, t_header))
        if score > best_score:
            best_score = score
            best_name = name

    # Require at least one hit
    return best_name if best_score > 0 else ""

