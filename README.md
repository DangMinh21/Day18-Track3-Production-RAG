# Lab 18: Production RAG Pipeline

**AICB-P2T3 · Ngày 18 · Production RAG**  
**Giảng viên:** M.Sc Trần Minh Tú · **Thời gian:** 2 giờ  
**Nhóm:** Track3 Production RAG · **Ngày nộp:** 4/5/2026

---

## Giới thiệu tổng thể

Repository này implement một hệ thống **Production-Ready Retrieval-Augmented Generation (RAG)** pipeline hoàn chỉnh cho tiếng Việt, bao gồm:

- **4 modules cốt lõi:** Chunking, Hybrid Search, Reranking, Evaluation
- **Vietnamese-specific optimizations:** BM25 với underthesea segmentation, bge-m3 embeddings, FlagEmbedding reranker
- **Production features:** Qdrant vector DB, RAGAS evaluation, failure analysis với Error Tree
- **Data:** Báo cáo tài chính (BCTC) và Nghị định bảo vệ dữ liệu cá nhân
- **Evaluation:** 30 Q&A pairs, so sánh naive baseline vs production pipeline

**Kết quả chính:**
- Faithfulness: 0.882 
- Answer Relevancy: 0.070 
- Context Precision: 0.825 
- Context Recall: 0.714

---

## Thành viên nhóm & Phân công

| STT | Tên | MSHV | Vai trò | Module phụ trách | Hoàn thành |
|-----|-----|------|--------|------------------|-----------|
| 1 | Doan Thu Anh | 2A202600364 | Thành viên | M1: Chunking & M5: Enrichment | ✅ 13/13 tests |
| 2 | Đồng Văn Thịnh | 2A202500365 | Thành viên | M2: Hybrid Search | ✅ 5/5 tests |
| 3 | Nguyễn Thị Quỳnh Trang | 2A202600406 | Thành viên | M3: Reranking | ✅ 5/5 tests |
| 4 | Đặng Văn Minh | 2A202600027 | Team Lead | M4: Evaluation + Team coordination | ✅ 4/4 tests |

**Team Lead responsibilities:**
- Phân chia công việc và assign modules
- Tạo test_set.json (30 Q&A pairs từ data thực)
- Kết nối pipeline tổng trong `src/pipeline.py`
- Chạy thực nghiệm và generate reports
- Coordinate team communication qua GitHub

---

## Cấu trúc repo (Chi tiết cho người chấm)

```
lab18-production-rag/
├── README.md                           # 📖 File này - Tổng quan & hướng dẫn
├── ASSIGNMENT_INDIVIDUAL.md            # 📋 Đề bài cá nhân (Phần A)
├── ASSIGNMENT_GROUP.md                 # 📋 Đề bài nhóm (Phần B)
├── RUBRIC.md                           # 📊 Hệ thống chấm điểm chi tiết
│
├── main.py                             # 🚀 Entry point: Chạy full pipeline
├── check_lab.py                        # ✅ Kiểm tra format trước nộp
├── naive_baseline.py                   # 📈 Baseline RAG (chạy trước)
├── config.py                           # ⚙️  Shared config (Qdrant, models)
├── requirements.txt                    # 📦 Dependencies (pinned versions)
├── docker-compose.yml                  # 🐳 Qdrant local DB
├── .env.example                        # 🔑 API keys template
│
├── data/                               # 📚 Corpus tiếng Việt
│   ├── BCTC.md                         # Báo cáo tài chính DHA Surfaces
│   └── Nghị định bảo vệ dữ liệu.md     # Nghị định 13/2023/NĐ-CP
├── test_set.json                       # ❓ 30 Q&A pairs cho evaluation
│
├── src/                                # 🛠️  Source code (implement đầy đủ)
│   ├── __init__.py
│   ├── m1_chunking.py                  # M1: 4 strategies chunking
│   ├── m2_search.py                    # M2: BM25 + Dense + RRF
│   ├── m3_rerank.py                    # M3: Cross-encoder reranking
│   ├── m4_eval.py                      # M4: RAGAS evaluation
│   └── pipeline.py                     # 🔗 Ghép modules thành pipeline
│
├── tests/                              # 🧪 Auto-grading (37/37 passed)
│   ├── __init__.py
│   ├── test_m1.py                      # 13 tests cho chunking
│   ├── test_m2.py                      # 5 tests cho search
│   ├── test_m3.py                      # 5 tests cho rerank
│   ├── test_m4.py                      # 4 tests cho eval
│   └── test_m5.py                      # 10 tests cho enrichment
│
├── analysis/                           # 📝 Deliverables (đã điền đầy đủ)
│   ├── failure_analysis.md             # 🔍 Phân tích 10 failures với Error Tree
│   ├── group_report.md                 # 📊 Báo cáo nhóm + presentation notes
│   └── reflections/                    # 🤔 Reflections cá nhân
│       ├── reflection_DoanThuAnh.md
│       ├── reflection_DongVanThinh.md
│       ├── reflection_NguyenThiQuynhTrang.md
│       └── reflection_DangVanMinh.md
│
├── reports/                            # 📈 Auto-generated results
│   ├── ragas_report.json               # RAGAS scores production pipeline
│   └── naive_baseline_report.json      # Baseline scores
│
├── templates/                          # 📄 Templates gốc (backup)
│   ├── failure_analysis.md
│   └── group_report.md
│
└── docs/                               # 📚 Documentation bổ sung
    ├── github_workflow.md              # Quy trình GitHub
    ├── lab_overview.md                 # Tổng quan lab
    ├── plan_tv1.md                     # Plan của TV1
    ├── plan_tv2.md                     # Plan của TV2
    ├── plan_tv3.md                     # Plan của TV3
    └── plan_tv4.md                     # Plan của TV4
```

**Chú thích cho người chấm:**
- **src/**: Code implement đầy đủ, không còn TODO markers
- **tests/**: 37/37 tests passed, bao gồm Vietnamese-specific tests
- **analysis/**: Reports đã điền chi tiết, có insights và Error Tree analysis
- **reports/**: JSON files với RAGAS metrics, failures list
- **data/**: Real Vietnamese documents (BCTC + legal text)

---

## Hướng dẫn chạy và chấm

### 1. Setup môi trường

```bash
# Clone repo
git clone <repo-url> && cd lab18-production-rag

# Start Qdrant DB
docker compose up -d

# Install dependencies
pip install -r requirements.txt

# Setup API keys (nếu cần)
cp .env.example .env
# Edit .env với OpenAI API key nếu dùng GPT
```

### 2. Chạy baseline (bắt buộc)

```bash
python naive_baseline.py
# Output: reports/naive_baseline_report.json
```

### 3. Chạy production pipeline

```bash
python main.py
# Output: reports/ragas_report.json + comparison table
```

### 4. Kiểm tra trước nộp

```bash
python check_lab.py
# Should show: 🚀 Bài lab sẵn sàng để nộp!
```

### 5. Chạy tests (auto-grading)

```bash
# All modules
pytest tests/ -v

# Individual modules
pytest tests/test_m1.py -v  # Chunking
pytest tests/test_m2.py -v  # Search
pytest tests/test_m3.py -v  # Rerank
pytest tests/test_m4.py -v  # Eval
```

### 6. Hướng dẫn chấm (cho giảng viên)

**Phần A (60 điểm - Cá nhân):**
- Code review: Logic đúng, Vietnamese handling (underthesea, bge-m3)
- Tests: 100% pass = 15đ/module
- Quality: Ruff check pass, comments, type hints

**Phần B (40 điểm - Nhóm):**
- Pipeline: `python src/pipeline.py` exit 0
- RAGAS: ≥0.75 ở ít nhất 1 metric
- Analysis: Bottom-5 failures với Error Tree walkthrough
- Presentation: 4/4 points (scores, win, case study, next steps)

**Bonus (+10 max):**
- Faithfulness ≥0.85: +5
- Enrichment integrated: +3

**Total:** Max 110 điểm, cap tại 100.

---

## Dependencies & Tech Stack

**Core RAG:**
- **Chunking:** Custom strategies (semantic, hierarchical, structure-aware)
- **Search:** BM25 (rank-bm25) + Dense (sentence-transformers bge-m3) + RRF
- **Rerank:** FlagEmbedding bge-reranker-v2-m3 + Flashrank
- **Eval:** RAGAS (faithfulness, relevancy, precision, recall)
- **DB:** Qdrant (local via Docker)

**Vietnamese Processing:**
- underthesea (word segmentation)
- sentence-transformers (embeddings)

**Dev Tools:**
- pytest (testing)
- docker (Qdrant)
- openai (LLM generation)

---

## Timeline thực hiện

| Thời gian | Hoạt động | Trách nhiệm |
|-----------|-----------|-------------|
| 0:00–0:15 | Setup + baseline | Team Lead |
| 0:15–1:45 | Implement modules | Individual (M1-M4) |
| 1:45–2:15 | Integrate + eval + analysis | Team |
| 2:15–2:30 | Presentation | Team |

---

## Liên hệ

- **Team Lead:** Đặng Văn Minh (minhdv0201@gmail.com)
- **GitHub:** https://github.com/DangMinh21/Day18-Track3-Production-RAG
- **Issues:** Tất cả code đã test và chạy thành công trên macOS Python 3.13
