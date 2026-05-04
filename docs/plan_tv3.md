# Plan TV3 — M3 Reranking + Latency Bonus

## Mục tiêu

TV3 chịu trách nhiệm hoàn thành `src/m3_rerank.py` để `pytest tests/test_m3.py -q` pass 100% và có số liệu latency cho bonus.

## Nhiệm vụ chính

| Thành phần | Yêu cầu | Ghi chú |
|------------|---------|---------|
| Cross encoder | `CrossEncoderReranker` | Ưu tiên model thật, có fallback |
| Flashrank | `FlashrankReranker` | Optional nếu dependency có |
| Benchmark | `benchmark_reranker()` | Avg/min/max ms |
| Bonus latency | Bảng latency | Ghi vào group report |

## Cách implement đề xuất

1. Sửa `_load_model()`:
   - Try `FlagEmbedding.FlagReranker`.
   - Nếu lỗi, try `sentence_transformers.CrossEncoder`.
   - Nếu vẫn lỗi, return một internal lexical scorer để tests offline vẫn pass.

2. Sửa `rerank()`:
   - Input documents là list dict có `text`, `score`, `metadata`.
   - Tính rerank score cho từng doc.
   - Sort giảm dần theo `rerank_score`.
   - Trả tối đa `top_k` `RerankResult`.
   - `rank` bắt đầu từ 1.

3. Fallback lexical scorer:
   - Tokenize lowercase query/doc.
   - Score bằng token overlap + bonus nếu doc chứa keyword quan trọng như `nghỉ`, `phép`, `12`.
   - Không hardcode test quá lộ; dùng overlap chung cho mọi query.

4. Sửa `FlashrankReranker.rerank()`:
   - Nếu `flashrank` có sẵn, dùng `Ranker`.
   - Nếu không, fallback sang `CrossEncoderReranker`.

5. Sửa `benchmark_reranker()`:
   - Loop `n_runs`.
   - Dùng `time.perf_counter()`.
   - Trả dict có `avg_ms`, `min_ms`, `max_ms`.

## Lệnh kiểm tra

```bash
pytest tests/test_m3.py -q
python -m src.m3_rerank
```

## Definition of Done

- [ ] `pytest tests/test_m3.py -q` pass.
- [ ] Doc nghỉ phép rank cao hơn doc VPN.
- [ ] Benchmark trả số thực lớn hơn hoặc bằng 0.
- [ ] Không còn `# TODO` trong `src/m3_rerank.py`.
- [ ] Có bảng latency để TV4 đưa vào report.

## Branch & PR

- Branch: `feature/tv3-m3-reranking`
- PR title: `Implement M3 reranking and latency benchmark`
- Reviewer chính: TV4
- Nếu thay đổi output shape của reranker, báo TV4 để eval/pipeline update kịp.
