# Team Action Plan — Lab 18 Production RAG

## Nguyên tắc làm việc

- Mỗi thành viên sở hữu một module chính và chịu trách nhiệm test tương ứng.
- Không merge code nếu module test riêng chưa pass.
- Sau khi M1-M4 ổn định, cả nhóm ghép pipeline, thêm M5 bonus và chạy RAGAS.
- Không ghi score giả vào report; mọi số liệu RAGAS để `TBD` cho đến khi chạy thật.

## Timeline đề xuất

| Giai đoạn | Việc cần làm | Người phụ trách |
|-----------|--------------|-----------------|
| 0. Setup | Cài dependency, sửa `test_set.json`, chuẩn bị Qdrant/API key | Cả nhóm |
| 1. Module core | Implement M1-M4 để test riêng pass | TV1-TV4 |
| 2. Bonus | Implement M5 enrichment và latency benchmark | TV3 + cả nhóm |
| 3. Integration | Chạy `python main.py`, tạo reports | TV2 + TV4 |
| 4. Analysis | Điền group report, failure analysis, reflection | Cả nhóm |
| 5. Final check | Chạy full test và `python check_lab.py` | Cả nhóm |

## TV1 — M1 Advanced Chunking

**Mục tiêu:** `pytest tests/test_m1.py -q` pass 100% và chunking đủ tốt cho retrieval.

**Việc cần làm:**

- Implement `chunk_semantic()`:
  - split câu bằng regex;
  - dùng embedding nếu có `sentence_transformers`;
  - có fallback lexical similarity để test không phụ thuộc model tải mạng.
- Implement `chunk_hierarchical()`:
  - tạo parent theo paragraph với `parent_id`;
  - tách child nhỏ hơn parent;
  - child phải có `parent_id` hợp lệ.
- Implement `chunk_structure_aware()`:
  - parse Markdown headers;
  - preserve header + content;
  - metadata có `section` và `strategy`.
- Implement `compare_strategies()`:
  - trả stats cho `basic`, `semantic`, `hierarchical`, `structure`;
  - in bảng so sánh ngắn.

**Acceptance criteria:**

- `pytest tests/test_m1.py -q` pass.
- Children nhỏ hơn parents.
- Không còn TODO trong `src/m1_chunking.py`.

## TV2 — M2 Hybrid Search

**Mục tiêu:** `pytest tests/test_m2.py -q` pass 100% và pipeline có retrieval ổn định.

**Việc cần làm:**

- Implement `segment_vietnamese()`:
  - dùng `underthesea.word_tokenize(text, format="text")` nếu có;
  - fallback trả lowercase text nếu thiếu package.
- Implement `BM25Search`:
  - index tokenized corpus;
  - search top-k sorted theo score;
  - fallback BM25 thủ công nếu thiếu `rank_bm25`.
- Implement `DenseSearch`:
  - tạo Qdrant collection;
  - encode bằng `BAAI/bge-m3`;
  - upsert payload có `text` và metadata.
- Implement `reciprocal_rank_fusion()`:
  - merge theo text;
  - score bằng `1 / (k + rank)`;
  - trả method `hybrid`.

**Acceptance criteria:**

- `pytest tests/test_m2.py -q` pass.
- Query "nghỉ phép năm" rank đúng tài liệu nghỉ phép.
- Không còn TODO trong `src/m2_search.py`.

## TV3 — M3 Reranking + Latency Bonus

**Mục tiêu:** `pytest tests/test_m3.py -q` pass 100%, có benchmark latency cho bonus.

**Việc cần làm:**

- Implement `CrossEncoderReranker._load_model()`:
  - ưu tiên `FlagEmbedding.FlagReranker`;
  - fallback `sentence_transformers.CrossEncoder`;
  - fallback cuối cùng dùng lexical scorer để test chạy offline.
- Implement `rerank()`:
  - tạo query-document pairs;
  - tính score;
  - sort descending;
  - trả `RerankResult` đúng rank.
- Implement `FlashrankReranker` nếu package có sẵn.
- Implement `benchmark_reranker()`:
  - đo `avg_ms`, `min_ms`, `max_ms`;
  - dùng `time.perf_counter()`.
- Chuẩn bị bảng latency cho group report.

**Acceptance criteria:**

- `pytest tests/test_m3.py -q` pass.
- Doc nghỉ phép rank trên doc VPN.
- Có số liệu latency để ghi bonus.
- Không còn TODO trong `src/m3_rerank.py`.

## TV4 — M4 Evaluation + Failure Analysis

**Mục tiêu:** `pytest tests/test_m4.py -q` pass 100%, report đủ để chấm nhóm.

**Việc cần làm:**

- Sửa `test_set.json` thành JSON hợp lệ và có câu hỏi thật.
- Implement `evaluate_ragas()`:
  - dùng RAGAS nếu dependency/API sẵn sàng;
  - fallback heuristic numeric scores để tests và pipeline không chết.
- Implement `failure_analysis()`:
  - sort bottom-N theo avg score;
  - tìm worst metric;
  - map diagnosis + suggested fix theo rubric.
- Đảm bảo `save_report()` sinh JSON đúng keys.
- Điền `analysis/failure_analysis.md` sau khi có report thật.

**Acceptance criteria:**

- `pytest tests/test_m4.py -q` pass.
- `reports/ragas_report.json` có `aggregate`, `num_questions`, `failures`.
- Bottom-5 có diagnosis và suggested fix rõ.
- Không còn TODO trong `src/m4_eval.py`.

## Việc chung — Full điểm + Bonus

**M5 Enrichment:**

- Implement extractive fallback cho `summarize_chunk()`.
- Generate HyQA bằng heuristic khi không có OpenAI key.
- `contextual_prepend()` phải preserve original text.
- `extract_metadata()` trả dict có topic/entities/category/language.
- `enrich_chunks()` trả list `EnrichedChunk`.
- Chạy `pytest tests/test_m5.py -q`.

**Pipeline + generation:**

- Dùng M1 hierarchical children để index.
- Dùng M5 enriched text trước khi embed.
- Search bằng hybrid M2.
- Rerank top results bằng M3.
- Generate answer dựa trên contexts; nếu chưa dùng LLM thì dùng context tốt nhất.
- Chạy `python main.py` để sinh reports.

**Presentation:**

- Slide 1: naive vs production RAGAS.
- Slide 2: biggest win, thường là M2 hybrid + M3 rerank.
- Slide 3: một case failure đi qua Error Tree.
- Slide 4: next optimization: better test set, prompt, metadata filtering, caching, latency.

## Thứ tự lệnh cuối cùng

```bash
pytest tests/test_m1.py -q
pytest tests/test_m2.py -q
pytest tests/test_m3.py -q
pytest tests/test_m4.py -q
pytest tests/test_m5.py -q
pytest tests -q
python main.py
python check_lab.py
```
