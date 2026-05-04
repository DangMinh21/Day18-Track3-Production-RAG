# Individual Reflection — Lab 18

**Tên:** Đoàn Thư Ánh 
**MSSV:** 2A202600364  
**Module phụ trách:** M1 (Chunking) & M5 (Enrichment)

---

## 1. Đóng góp kỹ thuật

- **Module đã implement:** 
  - `m1_chunking.py` (Advanced Chunking Strategies)
  - `m5_enrichment.py` (Enrichment Pipeline)
- **Các hàm/class chính đã viết:**
  - **M1 (Chunking):** 
    - `chunk_semantic`: Nhóm các câu dựa trên độ tương đồng ngữ nghĩa (Semantic similarity dùng `sentence-transformers` với fallback là Jaccard similarity).
    - `chunk_hierarchical`: Áp dụng chiến lược Parent-Child chunking để giữ context lớn (parent) đưa cho LLM nhưng index context nhỏ (child) để tối ưu retrieval.
    - `chunk_structure_aware`: Phân tách chunk dựa trên cấu trúc header của Markdown (H1, H2, H3), bảo toàn table và code block.
    - `compare_strategies`: Viết hàm A/B test để so sánh thống kê các chiến lược chunking.
  - **M5 (Enrichment):** 
    - `summarize_chunk`: Tóm tắt chunk bằng LLM (`gpt-4o-mini`) giúp giảm nhiễu khi nhúng vector.
    - `generate_hypothesis_questions`: Tạo câu hỏi giả định (HyQA) để thu hẹp khoảng cách từ vựng giữa câu hỏi user và nội dung.
    - `contextual_prepend`: Thêm ngữ cảnh của tài liệu vào đầu chunk (kỹ thuật của Anthropic giúp giảm lỗi retrieval).
    - `extract_metadata`: Tự động trích xuất Topic, Entities, Category và Language từ văn bản.
    - `enrich_chunks`: Pipeline tổng hợp gọi tự động các hàm enrichment trên.
- **Số tests pass:** 23/23

## 2. Kiến thức học được

- **Khái niệm mới nhất:** Contextual Prepend (cách thêm bối cảnh tài liệu vào các chunk tách rời) và HyQA (Hypothetical Document Embeddings/Questions) - dùng LLM sinh ra dữ liệu làm giàu trước khi embedding. 
- **Điều bất ngờ nhất:** Việc áp dụng Contextual Prepend theo nghiên cứu của Anthropic có thể giảm tới 49% lỗi retrieval. Ngoài ra, thay vì nhúng trực tiếp văn bản gốc, nhúng các câu hỏi giả định sinh ra từ chunk lại cho kết quả khớp truy vấn của người dùng tự nhiên và chính xác hơn.
- **Kết nối với bài giảng (slide nào):** Slide về Advanced RAG (Tiền xử lý dữ liệu, Chunking Strategies, Metadata Extraction & Enrichment pipeline).

## 3. Khó khăn & Cách giải quyết

- **Khó khăn lớn nhất:** 
  1. Xử lý chia câu tiếng Việt trong Semantic Chunking có thể chưa hoàn hảo vì dấu câu khá phức tạp.
  2. Xử lý kết quả trả về từ LLM khi trích xuất metadata bằng JSON. LLM thường trả về text bọc trong Markdown Code Block (```json ... ```) gây lỗi `JSONDecodeError`.
- **Cách giải quyết:** 
  1. Thiết kế cơ chế fallback linh hoạt trong M1: kết hợp thuật toán cosine similarity trên `sentence-transformers` và fallback Jaccard.
  2. Viết thêm logic tiền xử lý chuỗi ở M5: kiểm tra `content.startswith("```")` và cắt bỏ các ký tự dư thừa trước khi đưa vào hàm `json.loads()`.
- **Thời gian debug:** 5p

## 4. Nếu làm lại

- **Sẽ làm khác điều gì:** Tích hợp trực tiếp thư viện NLP chuyên dụng cho tiếng Việt (như `underthesea` hoặc `pyvi`) thay vì regex cơ bản để tách câu chuẩn xác hơn, qua đó nâng cao chất lượng Semantic Chunking.
- **Module nào muốn thử tiếp:** M2 (Embedding) hoặc M4 (Retrieval/Generation) để xem các dữ liệu sinh ra từ Enrichment Pipeline giúp ích thế nào trong thực tế khi truy vấn (search).

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|----------|---------------|
| Hiểu bài giảng | 5 |
| Code quality | 4 |
| Teamwork | 5 |
| Problem solving | 4 |
