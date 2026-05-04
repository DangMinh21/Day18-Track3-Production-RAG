"""Clean the parsed Markdown data files used by the RAG lab.

The PDF OCR output is noisy. This script rewrites:
- data/BCTC.md from the rendered VAT declaration image and verified table values.
- data/Nghi_dinh_*.md from the official Government full-text HTML source.
"""

from __future__ import annotations

import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
NGHI_DINH_URL = (
    "https://xaydungchinhsach.chinhphu.vn/"
    "toan-van-nghi-dinh-13-2023-nd-cp-bao-ve-du-lieu-ca-nhan-119230516104357809.htm"
)


BCTC_MARKDOWN = """# Tờ khai thuế giá trị gia tăng - Mẫu số 01/GTGT

Nguồn: `BCTC.pdf`

## Thông tin tờ khai

- Mẫu số: 01/GTGT.
- Tên tờ khai: Tờ khai thuế giá trị gia tăng.
- Đối tượng áp dụng: Người nộp thuế tính thuế theo phương pháp khấu trừ có hoạt động sản xuất kinh doanh.
- Tên hoạt động sản xuất kinh doanh: Hoạt động sản xuất kinh doanh thông thường.
- Kỳ tính thuế: Quý 4 năm 2024.
- Lần đầu: Không.
- Bổ sung lần thứ: 1.
- Tên người nộp thuế: CÔNG TY CỔ PHẦN DHA SURFACES.
- Mã số thuế: 0106769437.
- Đơn vị tiền: đồng Việt Nam.

## Bảng kê khai thuế giá trị gia tăng

| STT | Chỉ tiêu | Mã chỉ tiêu | Giá trị hàng hóa, dịch vụ chưa có thuế GTGT | Thuế GTGT |
|---|---|---:|---:|---:|
| A | Không phát sinh hoạt động mua, bán trong kỳ | [21] |  |  |
| B | Thuế giá trị gia tăng còn được khấu trừ kỳ trước chuyển sang | [22] |  | 77.377.803 |
| C | Kê khai thuế giá trị gia tăng phải nộp ngân sách nhà nước |  |  |  |
| I | Hàng hóa, dịch vụ mua vào trong kỳ |  |  |  |
| 1 | Giá trị và thuế giá trị gia tăng của hàng hóa, dịch vụ mua vào | [23], [24] | 2.405.743.241 | 215.163.767 |
|  | Trong đó: hàng hóa, dịch vụ nhập khẩu | [23a], [24a] | 0 | 0 |
| 2 | Thuế giá trị gia tăng của hàng hóa, dịch vụ mua vào được khấu trừ kỳ này | [25] |  | 215.163.767 |
| II | Hàng hóa, dịch vụ bán ra trong kỳ |  |  |  |
| 1 | Hàng hóa, dịch vụ bán ra không chịu thuế giá trị gia tăng | [26] | 0 |  |
| 2 | Hàng hóa, dịch vụ bán ra chịu thuế giá trị gia tăng | [27], [28] | 3.703.688.610 | 344.675.400 |
| a | Hàng hóa, dịch vụ bán ra chịu thuế suất 0% | [29] | 0 |  |
| b | Hàng hóa, dịch vụ bán ra chịu thuế suất 5% | [30], [31] | 0 | 0 |
| c | Hàng hóa, dịch vụ bán ra chịu thuế suất 10% | [32], [33] | 3.703.688.610 | 344.675.400 |
| d | Hàng hóa, dịch vụ bán ra không tính thuế | [32a] | 0 |  |
| 3 | Tổng doanh thu và thuế giá trị gia tăng của hàng hóa, dịch vụ bán ra | [34], [35] | 3.703.688.610 | 344.675.400 |
| III | Thuế giá trị gia tăng phát sinh trong kỳ, công thức [36] = [35] - [25] | [36] |  | 129.511.633 |
| IV | Điều chỉnh tăng, giảm thuế giá trị gia tăng còn được khấu trừ của các kỳ trước |  |  |  |
| 1 | Điều chỉnh giảm | [37] |  | 0 |
| 2 | Điều chỉnh tăng | [38] |  | 0 |
| V | Thuế giá trị gia tăng nhận bàn giao được khấu trừ trong kỳ | [39a] |  | 0 |
| VI | Xác định nghĩa vụ thuế giá trị gia tăng phải nộp trong kỳ |  |  |  |
| 1 | Thuế giá trị gia tăng phải nộp của hoạt động sản xuất kinh doanh trong kỳ, công thức [40a] = ([36] - [22] + [37] - [38] - [39a]) >= 0 | [40a] |  | 52.133.830 |
| 2 | Thuế giá trị gia tăng mua vào của dự án đầu tư được bù trừ với thuế GTGT còn phải nộp của hoạt động sản xuất kinh doanh cùng kỳ tính thuế, điều kiện [40b] <= [40a] | [40b] |  | 0 |
| 3 | Thuế giá trị gia tăng còn phải nộp trong kỳ, công thức [40] = [40a] - [40b] | [40] |  | 52.133.830 |
| 4 | Thuế giá trị gia tăng chưa khấu trừ hết kỳ này, công thức [41] = ([36] - [22] + [37] - [38] - [39a]) <= 0 | [41] |  | 0 |
| 4.1 | Thuế giá trị gia tăng đề nghị hoàn, điều kiện [42] <= [41] | [42] |  | 0 |
| 4.2 | Thuế giá trị gia tăng còn được khấu trừ chuyển kỳ sau, công thức [43] = [41] - [42] | [43] |  | 0 |

## Cam đoan và chữ ký

Tôi cam đoan số liệu khai trên là đúng và chịu trách nhiệm trước pháp luật về số liệu đã khai.

- Ngày ký: 24 tháng 01 năm 2025.
- Người nộp thuế hoặc đại diện hợp pháp của người nộp thuế: TRỊNH THỊ SANG.
- Ký điện tử bởi: CÔNG TY CỔ PHẦN DHA SURFACES.

## Tóm tắt số liệu quan trọng

- Thuế GTGT còn được khấu trừ kỳ trước chuyển sang [22]: 77.377.803 đồng.
- Thuế GTGT mua vào được khấu trừ kỳ này [25]: 215.163.767 đồng.
- Thuế GTGT bán ra [35]: 344.675.400 đồng.
- Thuế GTGT phát sinh trong kỳ [36]: 129.511.633 đồng.
- Thuế GTGT còn phải nộp trong kỳ [40]: 52.133.830 đồng.
"""


def clean_text(text: str) -> str:
    """Normalize whitespace while preserving Vietnamese text."""
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def paragraph_to_markdown(text: str) -> str:
    """Format legal paragraphs and lettered points for RAG-friendly Markdown."""
    if re.match(r"^[a-zđ]\)", text, flags=re.IGNORECASE):
        return f"- {text}"
    return text


def fetch_nghi_dinh_markdown() -> str:
    """Fetch official full text and convert the article body to Markdown."""
    response = requests.get(NGHI_DINH_URL, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    body = soup.select_one(".detail-content")
    if body is None:
        raise RuntimeError("Could not find .detail-content in the official article")

    lines = [
        "# Nghị định số 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân",
        "",
        "- Số hiệu: 13/2023/NĐ-CP.",
        "- Ngày ban hành: 17/04/2023.",
        "- Ngày hiệu lực: 01/07/2023.",
        f"- Nguồn toàn văn: {NGHI_DINH_URL}",
        "",
    ]

    for element in body.find_all(recursive=False):
        text = clean_text(element.get_text(" ", strip=True))
        if not text or set(text) <= {"_"}:
            continue
        if text.startswith("Tham khảo thêm"):
            break

        if element.name == "h2":
            lines.extend([f"## {text}", ""])
        elif element.name == "h3":
            lines.extend([f"## {text}", ""])
        elif element.name == "h4":
            lines.extend([f"### {text}", ""])
        elif element.name in {"p", "div"}:
            lines.extend([paragraph_to_markdown(text), ""])

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    """Rewrite both Markdown files with cleaned content."""
    (DATA_DIR / "BCTC.md").write_text(BCTC_MARKDOWN, encoding="utf-8")
    (DATA_DIR / "Nghi_dinh_so_13-2023_ve_bao_ve_du_lieu_ca_nhan_508ee.md").write_text(
        fetch_nghi_dinh_markdown(),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
