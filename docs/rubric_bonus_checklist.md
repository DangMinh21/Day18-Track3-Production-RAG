# Rubric + Bonus Checklist

## Cá nhân — 60 điểm mỗi người

| Tiêu chí | Điểm | Checklist |
|----------|------|-----------|
| Logic module đúng | 15 | Hàm chính implement đúng yêu cầu assignment |
| Tests pass | 15 | Test module riêng pass 100% |
| Vietnamese-specific | 10 | Có xử lý tiếng Việt phù hợp module |
| Code quality | 10 | Type hints, code sạch, không hardcode test lộ liễu |
| TODO markers | 10 | `grep -r "# TODO" src/m*.py` trả 0 |

## Nhóm — 40 điểm

| Tiêu chí | Điểm | Checklist |
|----------|------|-----------|
| Pipeline end-to-end | 10 | `python src/pipeline.py` exit code 0 |
| RAGAS score | 10 | Ít nhất 2 metrics >= 0.75 để chắc full |
| Failure analysis | 10 | Bottom-5 có diagnosis, fix, Error Tree |
| Presentation | 10 | Có đủ 4 ý: score, win, case study, next step |

## Bonus — 10 điểm

| Bonus | Điểm | Cách lấy |
|-------|------|----------|
| Faithfulness >= 0.85 | 5 | Dùng prompt trả lời chỉ dựa trên context |
| Enrichment pipeline | 3 | Tích hợp contextual prepend hoặc HyQA trong indexing |
| Latency breakdown | 2 | Ghi thời gian chunk/search/rerank/generate/eval |

## Checklist trước khi nộp

- [ ] `test_set.json` là JSON hợp lệ và có câu hỏi/ground truth thật.
- [ ] Có `requirements.txt` hoặc hướng dẫn dependency rõ ràng.
- [ ] Có `docker-compose.yml` nếu dùng Qdrant local.
- [ ] `pytest tests -q` pass 100%.
- [ ] `python main.py` chạy xong.
- [ ] `reports/naive_baseline_report.json` được sinh ra.
- [ ] `reports/ragas_report.json` được sinh ra.
- [ ] `analysis/group_report.md` đã điền score thật.
- [ ] `analysis/failure_analysis.md` đã điền Bottom-5 thật.
- [ ] Mỗi thành viên có reflection riêng.
- [ ] `python check_lab.py` không báo lỗi nghiêm trọng.

## Lệnh kiểm tra nhanh

```bash
pytest tests -q
grep -r "# TODO" src/m*.py
python main.py
python check_lab.py
```

## Score table cần điền sau khi chạy thật

| Metric | Naive | Production | Delta | Đạt full? |
|--------|-------|------------|-------|-----------|
| Faithfulness | TBD | TBD | TBD | TBD |
| Answer Relevancy | TBD | TBD | TBD | TBD |
| Context Precision | TBD | TBD | TBD | TBD |
| Context Recall | TBD | TBD | TBD | TBD |

## Rủi ro cần xử lý sớm

- Dependency nặng như `sentence_transformers`, `FlagEmbedding`, `ragas`, `qdrant_client` có thể chưa cài.
- Qdrant cần chạy trước khi dense search hoạt động.
- RAGAS thường cần OpenAI API key; cần fallback để pipeline không chết khi thiếu key.
- Test set hiện quá ít và chưa chuẩn; cần thêm câu hỏi thật để report có ý nghĩa.
