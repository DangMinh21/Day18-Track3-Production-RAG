# Plan TV4 — M4 Evaluation + Reports

## Mục tiêu

TV4 chịu trách nhiệm hoàn thành `src/m4_eval.py`, sửa test set, sinh report RAGAS và hoàn thiện failure analysis để đạt điểm nhóm.

## Nhiệm vụ chính

| Thành phần | Yêu cầu | Ghi chú |
|------------|---------|---------|
| Test set | JSON hợp lệ | Có question và ground truth thật |
| RAGAS eval | `evaluate_ragas()` | Dùng RAGAS nếu có, fallback nếu thiếu |
| Failure analysis | `failure_analysis()` | Bottom-N + diagnosis + suggested fix |
| Reports | JSON + markdown | Cập nhật `analysis/*.md` |

## Cách implement đề xuất

1. Sửa `test_set.json`:
   - Xóa trailing comma hiện tại.
   - Thêm ít nhất 5-10 câu hỏi thật từ corpus.
   - Mỗi item có `question` và `ground_truth`.

2. Sửa `evaluate_ragas()`:
   - Try import `ragas`, `datasets`.
   - Nếu dependency/API sẵn sàng, chạy 4 metrics:
     - faithfulness
     - answer_relevancy
     - context_precision
     - context_recall
   - Nếu lỗi, dùng heuristic scoring để trả numeric dict và `per_question`.
   - Không để pipeline chết vì thiếu API key.

3. Sửa `failure_analysis()`:
   - Tính avg score trên 4 metrics.
   - Sort tăng dần và lấy `bottom_n`.
   - Tìm worst metric.
   - Map diagnosis/fix:
     - faithfulness thấp -> tighten prompt
     - context_recall thấp -> improve chunking/search
     - context_precision thấp -> add reranking/filter
     - answer_relevancy thấp -> improve prompt

4. Hoàn thiện markdown:
   - Sau khi chạy `python main.py`, đọc `reports/*.json`.
   - Điền `analysis/group_report.md`.
   - Điền Bottom-5 thật trong `analysis/failure_analysis.md`.
   - Thu reflection từ TV1-TV3.

## Lệnh kiểm tra

```bash
python -m json.tool test_set.json
pytest tests/test_m4.py -q
python main.py
python check_lab.py
```

## Definition of Done

- [ ] `python -m json.tool test_set.json` pass.
- [ ] `pytest tests/test_m4.py -q` pass.
- [ ] `reports/ragas_report.json` có `aggregate`, `num_questions`, `failures`.
- [ ] `analysis/failure_analysis.md` có Bottom-5 thật.
- [ ] Không còn `# TODO` trong `src/m4_eval.py`.

## Branch & PR

- Branch: `feature/tv4-m4-evaluation`
- PR title: `Implement M4 evaluation and failure analysis`
- Reviewer chính: TV1
- TV4 là người chốt report cuối trước khi nộp.
