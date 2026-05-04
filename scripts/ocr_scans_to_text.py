"""Create searchable PDFs and sidecar text files from scanned PDFs.

This implements the scan -> searchable PDF -> real text workflow:
    data/*.pdf -> data/processed/*_searchable.pdf
                -> data/processed/*.txt

Requirements outside Python:
- Tesseract OCR with Vietnamese language data (`vie`)
- Ghostscript (`gs`)

Usage:
    python scripts/ocr_scans_to_text.py
"""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
PDF_FILES = (
    DATA_DIR / "BCTC.pdf",
    DATA_DIR / "Nghi_dinh_so_13-2023_ve_bao_ve_du_lieu_ca_nhan_508ee.pdf",
)


def ocr_pdf(pdf_path: Path) -> None:
    """Run OCRmyPDF and emit both searchable PDF and sidecar text."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    searchable_pdf = PROCESSED_DIR / f"{pdf_path.stem}_searchable.pdf"
    sidecar_text = PROCESSED_DIR / f"{pdf_path.stem}.txt"

    command = [
        "ocrmypdf",
        "--language",
        "vie+eng",
        "--deskew",
        "--rotate-pages",
        "--force-ocr",
        "--invalidate-digital-signatures",
        "--clean",
        "--optimize",
        "1",
        "--jobs",
        "4",
        "--sidecar",
        str(sidecar_text),
        str(pdf_path),
        str(searchable_pdf),
    ]
    print(f"OCR: {pdf_path.name}")
    subprocess.run(command, check=True, cwd=ROOT_DIR)
    print(f"  PDF:  {searchable_pdf.relative_to(ROOT_DIR)}")
    print(f"  Text: {sidecar_text.relative_to(ROOT_DIR)}")


def main() -> None:
    """OCR all configured scanned PDFs sequentially."""
    for pdf_path in PDF_FILES:
        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)
        ocr_pdf(pdf_path)


if __name__ == "__main__":
    main()
