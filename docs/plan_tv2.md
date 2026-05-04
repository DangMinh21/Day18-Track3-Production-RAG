# Plan TV2 — M2 Hybrid Search

## Mục tiêu

TV2 chịu trách nhiệm hoàn thành `src/m2_search.py` để `pytest tests/test_m2.py -q` pass 100% và pipeline có retrieval bằng BM25 + dense + RRF.

## Nhiệm vụ chính

| Thành phần | Yêu cầu | Ghi chú |
|------------|---------|---------|
| Vietnamese segmentation | `segment_vietnamese()` | Dùng `underthesea` nếu có |
| BM25 | `BM25Search.index/search` | Có fallback nếu thiếu `rank_bm25` |
| Dense search | `DenseSearch.index/search` | Qdrant + `BAAI/bge-m3` |
| RRF | `reciprocal_rank_fusion()` | Method output là `hybrid` |

## Cách implement đề xuất

1. Sửa `segment_vietnamese()`:
   - Try import `underthesea.word_tokenize`.
   - Nếu import lỗi, return text lowercase bình thường.
   - Không để thiếu dependency làm crash tests.

2. Sửa `BM25Search.index()`:
   - Lưu `self.documents = chunks`.
   - Segment từng chunk, split tokens.
   - Dùng `rank_bm25.BM25Okapi` nếu có.
   - Nếu thiếu package, lưu corpus tokens để search bằng token overlap/TF score.

3. Sửa `BM25Search.search()`:
   - Tokenize query.
   - Tính score, sort giảm dần.
   - Trả `SearchResult(..., method="bm25")`.
   - Bỏ qua docs score 0 nếu vẫn còn đủ kết quả; nếu không, trả top-k để pipeline không rỗng.

4. Sửa `DenseSearch.index/search()`:
   - Recreate collection Qdrant.
   - Encode texts bằng SentenceTransformer.
   - Upsert payload có `text` và metadata.
   - Search query vector và trả `method="dense"`.

5. Sửa `reciprocal_rank_fusion()`:
   - Merge theo `result.text`.
   - Cộng `1 / (k + rank + 1)` cho mỗi ranking list.
   - Sort score giảm dần và trả top-k `SearchResult` method `hybrid`.

## Lệnh kiểm tra

```bash
pytest tests/test_m2.py -q
python -m src.m2_search
```

## Definition of Done

- [ ] `pytest tests/test_m2.py -q` pass.
- [ ] Query `nghỉ phép năm` trả tài liệu nghỉ phép đứng đầu BM25.
- [ ] RRF merge không mất metadata.
- [ ] Không còn `# TODO` trong `src/m2_search.py`.
- [ ] Pipeline có thể gọi `HybridSearch.index()` và `HybridSearch.search()`.

## Branch & PR

- Branch: `feature/tv2-m2-hybrid-search`
- PR title: `Implement M2 hybrid search`
- Reviewer chính: TV3
- Khi cần thay đổi pipeline/index format, tag TV1 và TV4 trong PR.
