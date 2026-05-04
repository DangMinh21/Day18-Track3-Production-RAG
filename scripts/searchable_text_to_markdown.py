"""Convert OCR sidecar text from searchable PDFs into Markdown.

This is intentionally conservative: it preserves the OCR wording, only fixing
line wrapping and turning common legal document markers into Markdown headings.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT_DIR / "data" / "processed"


def _clean_line(line: str) -> str:
    """Normalize whitespace on a single OCR line."""
    return re.sub(r"[ \t]+", " ", line.replace("\x0c", "")).strip()


def _is_heading(line: str) -> bool:
    """Detect uppercase legal headings emitted by OCR."""
    if len(line) < 4:
        return False
    letters = [char for char in line if char.isalpha()]
    if not letters:
        return False
    uppercase_ratio = sum(char.isupper() for char in letters) / len(letters)
    return uppercase_ratio > 0.8


def _markdown_line(line: str) -> str:
    """Convert legal markers to Markdown headings/list items."""
    line = _clean_line(line)
    if not line:
        return ""

    line = re.sub(r"^-+\s*", "", line)

    if re.match(r"^Chương\s+[IVXLCDM]+\b", line, flags=re.IGNORECASE):
        return f"## {line}"
    if re.match(r"^Mục\s+\d+\b", line, flags=re.IGNORECASE):
        return f"## {line}"
    if re.match(r"^Điều\s+\d+\.", line, flags=re.IGNORECASE):
        return f"### {line}"
    if _is_heading(line):
        return f"## {line}"
    if re.match(r"^[a-zđ]\)", line, flags=re.IGNORECASE):
        return f"- {line}"
    return line


def convert_text_to_markdown(text_path: Path, markdown_path: Path) -> None:
    """Convert one OCR text file into Markdown."""
    raw_lines = text_path.read_text(encoding="utf-8", errors="replace").splitlines()
    markdown_lines = [
        "# Nghị định số 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân",
        "",
        f"Nguồn OCR: `{text_path.name}` từ searchable PDF.",
        "",
    ]

    previous_blank = False
    for raw_line in raw_lines:
        line = _markdown_line(raw_line)
        if not line:
            if not previous_blank:
                markdown_lines.append("")
            previous_blank = True
            continue
        markdown_lines.append(line)
        previous_blank = False

    markdown_path.write_text("\n".join(markdown_lines).strip() + "\n", encoding="utf-8")


def main() -> None:
    """Convert the Nghị định 13 OCR sidecar text to Markdown."""
    text_path = PROCESSED_DIR / "Nghi_dinh_so_13-2023_ve_bao_ve_du_lieu_ca_nhan_508ee.txt"
    markdown_path = PROCESSED_DIR / "Nghi_dinh_so_13-2023_ve_bao_ve_du_lieu_ca_nhan_508ee_searchable.md"
    convert_text_to_markdown(text_path, markdown_path)
    print(f"Saved {markdown_path.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
