# Individual Reflection — Lab 18

**Tên:** Đồng Văn Thịnh  
**MSHV: ** 2A202500365
**Module phụ trách:** M2

---

## 1. Đóng góp kỹ thuật

- **Module đã implement:** Module 2: Hybrid Search.
- **Các hàm/class chính đã viết:**
    - `segment_vietnamese(text)`: Sử dụng `underthesea` để tách từ tiếng Việt, chuẩn hóa input cho BM25.
    - `BM25Search`: Class quản lý việc tạo index và tìm kiếm theo thuật toán BM25Okapi.
    - `DenseSearch`: Class quản lý việc lưu trữ vector vào Qdrant và tìm kiếm ngữ nghĩa sử dụng model `bge-m3`.
    - `reciprocal_rank_fusion(results_list)`: Hàm kết hợp kết quả từ BM25 và Dense bằng thuật toán RRF.
    - `HybridSearch`: Pipeline tổng hợp kết hợp cả hai phương pháp trên.
- **Số tests pass:** 5/5 (đã kiểm tra và pass tất cả các test case quan trọng về segmentation, search và fusion).

## 2. Kiến thức học được

- **Khái niệm mới nhất:** Reciprocal Rank Fusion (RRF). Đây là một phương pháp rất thông minh để kết hợp các danh sách kết quả có thang điểm khác nhau (BM25 điểm không giới hạn, Dense điểm từ 0-1) mà không cần phải thực hiện normalization phức tạp.
- **Điều bất ngờ nhất:** Tầm quan trọng của việc tách từ (segmentation) đối với tiếng Việt. Nếu không dùng `underthesea`, BM25 sẽ coi "nghỉ" và "phép" là hai từ riêng biệt, làm giảm độ chính xác khi tìm kiếm cụm từ cố định như "nghỉ phép".
- **Kết nối với bài giảng (slide nào):** Kết nối trực tiếp với phần "Hybrid Search & RRF" và "Vietnamese RAG Optimization" trong bài giảng về Retrieval.

## 3. Khó khăn & Cách giải quyết

- **Khó khăn lớn nhất:** Cấu hình và kết nối với Qdrant trong môi trường Docker, đồng thời đảm bảo vector dimension (1024 cho bge-m3) khớp với cấu hình collection.
- **Cách giải quyết:** Đọc kỹ tài liệu của Qdrant Python SDK và kiểm tra log của Docker container để đảm bảo service đã sẵn sàng trước khi thực hiện indexing.
- **Thời gian debug:** Khoảng 2 giờ để tinh chỉnh logic fusion và xử lý các trường hợp kết quả trả về bị rỗng.

## 4. Nếu làm lại

- **Sẽ làm khác điều gì:** Sẽ tìm hiểu cách sử dụng bộ lọc (Filter) của Qdrant dựa trên metadata ngay trong lúc tìm kiếm vector để tăng tốc độ thay vì chỉ tìm kiếm và merge kết quả sau đó.
- **Module nào muốn thử tiếp:** Module 3 (Reranking) vì tôi muốn xem sau khi Hybrid Search trả về kết quả tốt, bước Rerank sẽ cải thiện độ chính xác (Precision) thêm bao nhiêu phần trăm.

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|----------|---------------|
| Hiểu bài giảng | 4 |
| Code quality | 5 |
| Teamwork | 4 |
| Problem solving | 4 |
