# Individual Reflection — Lab 18

**Tên:** TV3  
**Module phụ trách:** M3: Reranking

---

## 1. Đóng góp kỹ thuật

- Module đã implement: `src/m3_rerank.py`
- Các hàm/class chính đã viết:
  - `CrossEncoderReranker._load_model()`
  - `CrossEncoderReranker.rerank()`
  - `FlashrankReranker.rerank()`
  - `benchmark_reranker()`
- Số tests pass: TBD

## 2. Kiến thức học được

- Khái niệm mới nhất: cross-encoder reranking, top-20 to top-3 filtering, latency tradeoff.
- Điều bất ngờ nhất: TBD
- Kết nối với bài giảng: reranking tăng context precision bằng cách giảm documents nhiễu trước generation.

## 3. Khó khăn & Cách giải quyết

- Khó khăn lớn nhất: model reranker có thể tải chậm hoặc thiếu dependency.
- Cách giải quyết: ưu tiên model thật khi có package, fallback scorer để đảm bảo pipeline và tests chạy được.
- Thời gian debug: TBD

## 4. Nếu làm lại

- Sẽ làm khác điều gì: TBD
- Module nào muốn thử tiếp: M5 Enrichment

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|----------|---------------|
| Hiểu bài giảng | TBD |
| Code quality | TBD |
| Teamwork | TBD |
| Problem solving | TBD |
