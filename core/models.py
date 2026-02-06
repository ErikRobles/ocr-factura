"""
Data models for extracted receipt/invoice rows.
One row per image; fields align with Excel output columns.
"""
from dataclasses import dataclass


UNABLE_TO_READ = "Unable to read value"


@dataclass
class ExtractedRow:
    """Single row of extracted data from one receipt image."""

    # Core identifiers (high priority)
    retailer_name: str = ""
    ticket_or_folio: str = ""
    ticket_or_folio_candidates: str = ""  # pipe-separated
    transaction_number: str = ""
    date: str = ""  # YYYY-MM-DD if possible
    time: str = ""  # HH:MM if possible
    amount_total: str = ""
    amount_subtotal: str = ""
    currency: str = ""
    payment_method: str = ""

    # Retailer invoicing hints
    facturacion_url_on_ticket: str = ""
    facturacion_method: str = ""  # URL | EMAIL | UNKNOWN
    email_on_ticket: str = ""
    facturacion_notes: str = ""

    # Extra
    store_branch: str = ""
    cashier_number: str = ""
    register_number: str = ""
    sucursal: str = ""
    tienda: str = ""
    caja: str = ""
    cajero: str = ""

    # Quality and traceability
    ocr_quality: str = ""  # Good | Medium | Poor
    confidence_score: float = 0.0
    missing_fields: str = ""  # comma list
    warnings: str = ""
    image_file_name: str = ""
    image_file_path: str = ""
    image_open_link: str = ""  # same as path for hyperlink
    cropped_preview_folder: str = ""
    ticket_crop_link: str = ""
    amount_crop_link: str = ""
    date_crop_link: str = ""

    def is_low_confidence_or_missing_key_fields(self) -> bool:
        """True if row should appear in Needs_Review sheet."""
        key_fields = [
            self.retailer_name,
            self.ticket_or_folio,
            self.date,
            self.amount_total,
        ]
        any_missing = any(
            not v or v == UNABLE_TO_READ for v in key_fields
        )
        low_conf = self.confidence_score < 0.5
        return any_missing or low_conf or self.ocr_quality == "Poor"
