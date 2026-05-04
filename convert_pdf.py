import os
import time
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

def convert_bctc_to_md_advanced(input_path, output_path):
    print(f"🚀 Bắt đầu phân tích sâu file: {input_path}...")
    start_time = time.time()

    # 1. CẤU HÌNH PIPELINE PHÂN TÍCH SÂU DÀNH RIÊNG CHO BCTC
    pipeline_options = PdfPipelineOptions()
    
    # Bật OCR để đọc các bảng biểu/text bị chuyển thành ảnh (rất hay gặp trong BCTC VN)
    pipeline_options.do_ocr = True  
    
    # Ép sử dụng mô hình nhận diện cấu trúc bảng (Table Structure Recognition)
    pipeline_options.do_table_structure = True  
    
    # Bật tính năng khớp ô (Cell Matching) để xử lý các ô bị gộp (Merge cells) chuẩn xác hơn
    pipeline_options.table_structure_options.do_cell_matching = True 

    # Cài đặt option này cho định dạng PDF
    pdf_format_option = PdfFormatOption(
        pipeline_options=pipeline_options
    )

    # 2. KHỞI TẠO CONVERTER VỚI CẤU HÌNH NÂNG CAO
    converter = DocumentConverter(
        allowed_formats=[InputFormat.PDF],
        format_options={InputFormat.PDF: pdf_format_option}
    )

    try:
        print("⏳ Đang đọc bố cục và tái tạo bảng biểu (Quá trình này có thể mất vài phút vì đang chạy model AI)...")
        # Phân tích toàn bộ document
        result = converter.convert(input_path)

        print("📝 Đang kết xuất sang định dạng Markdown chuẩn...")
        # Lấy nội dung Markdown
        markdown_content = result.document.export_to_markdown()

        # 3. LƯU KẾT QUẢ
        # Tạo thư mục chứa file đầu ra nếu chưa có
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        end_time = time.time()
        print(f"✅ Tuyệt vời! File Markdown chuẩn chỉnh đã được lưu tại: {output_path}")
        print(f"⏱️ Tổng thời gian xử lý: {round(end_time - start_time, 2)} giây")

    except Exception as e:
        print(f"❌ Có lỗi trong quá trình xử lý: {e}")

if __name__ == "__main__":
    # Cấu hình đường dẫn
    INPUT_PDF = "data/BCTC.pdf"
    OUTPUT_MD = "data/BCTC.md" # Đổi tên file output một chút để dễ phân biệt
    
    # Kiểm tra file tồn tại
    if os.path.exists(INPUT_PDF):
        convert_bctc_to_md_advanced(INPUT_PDF, OUTPUT_MD)
    else:
        print(f"⚠️ Không tìm thấy file {INPUT_PDF}. Hãy kiểm tra lại thư mục data!")