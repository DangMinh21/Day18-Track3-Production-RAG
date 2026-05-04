# Individual Reflection — Lab 18

**Tên:** Nguyễn Thị Quỳnh Trang  
**MSHV:** 2A202600406  
**Module phụ trách:** M3: Reranking

---

## 1. Đóng góp kỹ thuật

- Module đã implement: M3 Reranking với CrossEncoderReranker và FlashrankReranker, bao gồm latency benchmarking.
- Các hàm/class chính đã viết: `CrossEncoderReranker.rerank()`, `FlashrankReranker.rerank()`, `benchmark_reranker()`.
- Số tests pass: 5/5

## 2. Kiến thức học được

- Khái niệm mới nhất: Cross-encoder reranking và cách benchmark latency trong production RAG systems.
- Điều bất ngờ nhất: Reranking có thể cải thiện precision nhưng không đảm bảo recall, và latency trade-off quan trọng.
- Kết nối với bài giảng (slide nào): Slide về reranking techniques và performance optimization.

## 3. Khó khăn & Cách giải quyết

- Khó khăn lớn nhất: Integrate FlagEmbedding và Flashrank models với proper error handling.
- Cách giải quyết: Đọc documentation và implement fallback khi model không available.
- Thời gian debug: 45 phút để fix model loading và rerank logic.

## 4. Nếu làm lại

- Sẽ làm khác điều gì: Thêm comparison với multiple reranking models để chọn best one.
- Module nào muốn thử tiếp: M1 Chunking để hiểu preprocessing impact trên downstream tasks.

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|----------|---------------|
| Hiểu bài giảng | 5 |
| Code quality | 4 |
| Teamwork | 5 |
| Problem solving | 4 |