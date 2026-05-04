"""Convert PDFs in data/ to Markdown files with Docling.

The RAG loader in src/m1_chunking.py reads Markdown files directly from data/.
This script therefore writes one .md file next to each source .pdf. Tables are
also exported to data/tables/ as CSV and HTML so large financial/legal tables
can be inspected without trusting Markdown formatting blindly.

Usage:
    python scripts/parse_pdfs_docling.py
"""

from __future__ import annotations

import logging
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
TABLES_DIR = DATA_DIR / "tables"


def _write_markdown(pdf_path: Path, markdown: str) -> Path:
    """Write parsed Markdown beside the source PDF for the current loader."""
    output_path = pdf_path.with_suffix(".md")
    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def _export_tables(document, pdf_path: Path) -> int:
    """Export each detected table as CSV and HTML for manual verification."""
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    for table_index, table in enumerate(document.tables, start=1):
        stem = f"{pdf_path.stem}_table_{table_index:03d}"
        dataframe = table.export_to_dataframe(doc=document)
        dataframe.to_csv(TABLES_DIR / f"{stem}.csv", index=False)
        (TABLES_DIR / f"{stem}.html").write_text(table.export_to_html(doc=document), encoding="utf-8")

    return len(document.tables)


def parse_pdf(pdf_path: Path, converter: DocumentConverter) -> None:
    """Parse one PDF and persist Markdown plus table audit files."""
    logging.info("Parsing %s", pdf_path.name)
    result = converter.convert(pdf_path)
    document = result.document

    markdown_path = _write_markdown(pdf_path, document.export_to_markdown())
    table_count = _export_tables(document, pdf_path)

    logging.info("Saved %s (%s tables)", markdown_path.relative_to(ROOT_DIR), table_count)


def main() -> None:
    """Parse every PDF in data/ sequentially to keep memory use predictable."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    pdf_paths = sorted(DATA_DIR.glob("*.pdf"))

    if not pdf_paths:
        logging.warning("No PDF files found in %s", DATA_DIR)
        return

    pipeline_options = PdfPipelineOptions()
    # These source PDFs may be scanned/image-heavy, so OCR is enabled. The first
    # run downloads OCR/layout/table models; later runs reuse the local cache.
    pipeline_options.do_ocr = True
    # Force RapidOCR because Docling's auto mode may choose ocrmac after it is
    # installed, but Apple Vision produced image-only Markdown for these files.
    pipeline_options.ocr_options = RapidOcrOptions()
    pipeline_options.do_table_structure = True

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
        }
    )
    for pdf_path in pdf_paths:
        parse_pdf(pdf_path, converter)


if __name__ == "__main__":
    main()
