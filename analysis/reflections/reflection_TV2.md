# Individual Reflection — Lab 18

**Tên:** TV2  
**Module phụ trách:** M2: Hybrid Search

---

## 1. Đóng góp kỹ thuật

- Module đã implement: `src/m2_search.py`
- Các hàm/class chính đã viết:
  - `segment_vietnamese()`
  - `BM25Search.index()`
  - `BM25Search.search()`
  - `DenseSearch.index()`
  - `DenseSearch.search()`
  - `reciprocal_rank_fusion()`
- Số tests pass: TBD

## 2. Kiến thức học được

- Khái niệm mới nhất: hybrid retrieval, BM25 cho exact keyword, dense search cho semantic match, RRF để fuse ranking.
- Điều bất ngờ nhất: TBD
- Kết nối với bài giảng: retrieval quality quyết định context precision/recall trước khi LLM generate.

## 3. Khó khăn & Cách giải quyết

- Khó khăn lớn nhất: xử lý tiếng Việt và dependency Qdrant/embedding model.
- Cách giải quyết: dùng `underthesea` khi có package, fallback tokenization để test offline không chết.
- Thời gian debug: TBD

## 4. Nếu làm lại

- Sẽ làm khác điều gì: TBD
- Module nào muốn thử tiếp: M3 Reranking

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|----------|---------------|
| Hiểu bài giảng | TBD |
| Code quality | TBD |
| Teamwork | TBD |
| Problem solving | TBD |
