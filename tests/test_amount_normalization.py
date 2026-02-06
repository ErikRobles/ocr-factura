"""Unit tests for amount parsing and normalization."""
import sys
from pathlib import Path

# Add repo root for imports
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from core.extract import normalize_amount, parse_amounts


def test_normalize_amount_dollars_and_commas():
    assert normalize_amount("$1,234.50") == "1234.50"
    assert normalize_amount("  $  2,000.00  ") == "2000.00"


def test_normalize_amount_integer():
    assert normalize_amount("500") == "500"
    assert normalize_amount("500.00") == "500.00"


def test_normalize_amount_empty():
    assert normalize_amount("") == ""
    assert normalize_amount("  ") == ""


def test_parse_amounts_total_subtotal_iva():
    text = """
    SUBTOTAL    $100.00
    IVA         $16.00
    TOTAL       $116.00
    """
    total, subtotal, iva = parse_amounts(text)
    assert total == "116.00"
    assert subtotal == "100.00"
    assert iva == "16.00"


def test_parse_amounts_spanish_labels():
    text = "Importe total: $1,234.50 Monto total $1234.50"
    total, subtotal, iva = parse_amounts(text)
    assert total in ("1234.50", "1234.50")  # may get first or second
    # At least one total found
    assert "1234" in total or total == "1234.50"
