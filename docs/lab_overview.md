# Lab 18 Production RAG — Overview

## Mục tiêu

Hoàn thành bài lab với điểm tối đa phần cá nhân, phần nhóm và bonus. Hệ thống cần chạy được end-to-end:

```text
M1 Chunking -> M5 Enrichment -> M2 Hybrid Search -> M3 Rerank -> Generate -> M4 Eval
```

Kết quả cuối cùng cần có source code đã implement, test pass, report RAGAS, failure analysis, group report và reflection cá nhân.

## Bản đồ điểm

| Hạng mục | Điểm | Điều kiện chính |
|----------|------|-----------------|
| Cá nhân | 60 | Module đúng logic, test pass, xử lý tiếng Việt, code sạch, hết TODO |
| Nhóm | 40 | Pipeline chạy, RAGAS đạt ngưỡng, failure analysis tốt, presentation rõ |
| Bonus | 10 | Faithfulness >= 0.85, enrichment tích hợp, latency breakdown |

## Trạng thái repo hiện tại

| Vấn đề | Trạng thái | Hành động |
|--------|------------|-----------|
| TODO trong `src/` | 20 marker | Mỗi TV xử lý module được giao |
| Tests | 27 passed, 10 failed | Ưu tiên fix M1-M4 trước |
| `test_set.json` | JSON lỗi trailing comma | Sửa trước khi chạy M4/main |
| `requirements.txt` | Chưa có trong repo | Tạo hoặc ghi rõ dependency cần cài |
| `docker-compose.yml` | Chưa có trong repo | Bổ sung nếu dùng Qdrant local |
| Reports | Chưa có JSON report | Tạo bằng `python main.py` sau khi pipeline chạy |

## Kiến trúc module

| Module | File | Vai trò | Owner |
|--------|------|---------|-------|
| M1 | `src/m1_chunking.py` | Advanced chunking: semantic, hierarchical, structure-aware | TV1 |
| M2 | `src/m2_search.py` | Hybrid search: BM25 + dense + RRF | TV2 |
| M3 | `src/m3_rerank.py` | Cross-encoder rerank + latency benchmark | TV3 |
| M4 | `src/m4_eval.py` | RAGAS eval + failure analysis | TV4 |
| M5 | `src/m5_enrichment.py` | Contextual prepend, HyQA, metadata, summary | Chung |
| Pipeline | `src/pipeline.py` | Ghép full RAG system | Chung |

## Deliverables

| Deliverable | File | Trạng thái |
|-------------|------|------------|
| Production code | `src/*.py` | TBD |
| Naive report | `reports/naive_baseline_report.json` | TBD sau `python main.py` |
| RAGAS report | `reports/ragas_report.json` | TBD sau `python main.py` |
| Group report | `analysis/group_report.md` | Template đã chuẩn bị |
| Failure analysis | `analysis/failure_analysis.md` | Template đã chuẩn bị |
| Individual reflections | `analysis/reflections/reflection_TV*.md` | Template đã chuẩn bị |

## Definition of Done

- `pytest tests -q` pass 100%.
- `python main.py` chạy xong và sinh đủ report.
- `python check_lab.py` không báo lỗi deliverable quan trọng.
- Ít nhất 2 RAGAS metrics >= 0.75.
- Faithfulness >= 0.85 để lấy bonus nếu có OpenAI/RAGAS setup ổn định.
- `analysis/failure_analysis.md` có Bottom-5, diagnosis, suggested fix và case study.
- Presentation có số liệu naive vs production, biggest win, case study và next optimization.
