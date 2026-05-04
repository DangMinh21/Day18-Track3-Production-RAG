# Individual Reflection — Lab 18

**Tên:** TV4  
**Module phụ trách:** M4: RAGAS Evaluation

---

## 1. Đóng góp kỹ thuật

- Module đã implement: `src/m4_eval.py`
- Các hàm/class chính đã viết:
  - `load_test_set()`
  - `evaluate_ragas()`
  - `failure_analysis()`
  - `save_report()`
- Số tests pass: TBD

## 2. Kiến thức học được

- Khái niệm mới nhất: RAGAS metrics, faithfulness, answer relevancy, context precision, context recall.
- Điều bất ngờ nhất: TBD
- Kết nối với bài giảng: evaluation giúp biết pipeline fail ở retrieval, generation hay dữ liệu test.

## 3. Khó khăn & Cách giải quyết

- Khó khăn lớn nhất: RAGAS có thể cần API key và dependency đầy đủ.
- Cách giải quyết: dùng RAGAS khi môi trường sẵn sàng, fallback numeric scoring để pipeline không bị block.
- Thời gian debug: TBD

## 4. Nếu làm lại

- Sẽ làm khác điều gì: TBD
- Module nào muốn thử tiếp: M1 Chunking

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|----------|---------------|
| Hiểu bài giảng | TBD |
| Code quality | TBD |
| Teamwork | TBD |
| Problem solving | TBD |
