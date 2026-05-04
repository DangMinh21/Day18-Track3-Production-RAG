# Group Report — Lab 18: Production RAG

**Nhóm:** Track3 Production RAG  
**Ngày:** 4/5/2026

## Thành viên & Phân công

| Tên | Module | Hoàn thành | Tests pass |
|-----|--------|-----------|-----------|
| Doan Thu Anh | M1: Chunking & M5: Enrichment | ✅ | 13/13 |
| Đồng Văn Thịnh  | M2: Hybrid Search | ✅ | 5/5 |
| Nguyễn Thị Quỳnh Trang | M3: Reranking | ✅ | 5/5 |
| Đặng Văn Minh | M4: Evaluation | ✅ | 4/4 |

## Kết quả RAGAS

| Metric | Naive | Production | Δ |
|--------|-------|-----------|---|
| Faithfulness | 0.956 | 0.882 | -0.074 |
| Answer Relevancy | 0.293 | 0.070 | -0.223 |
| Context Precision | 0.828 | 0.825 | -0.003 |
| Context Recall | 0.714 | -0.112 |  |
| Context Recall | 0.826 | 0.714 | -0.112 |

## Key Findings

1. **Biggest improvement:** Context Precision duy trì ổn định (0.828 → 0.825), cho thấy retrieval và reranking hoạt động tốt trong việc lọc context liên quan.
2. **Biggest challenge:** Answer Relevancy giảm mạnh (0.293 → 0.070), cho thấy prompt template và generation step cần cải thiện để trả lời chính xác câu hỏi.
3. **Surprise finding:** Faithfulness giảm nhẹ nhưng vẫn cao (0.956 → 0.882), production pipeline phức tạp hơn nhưng không làm tăng hallucination đáng kể.

## Presentation Notes (5 phút)

1. RAGAS scores (naive vs production): Production pipeline có độ chính xác context tốt nhưng generation step yếu, dẫn đến answer relevancy thấp.
2. Biggest win — module nào, tại sao: M2 Hybrid Search, vì context precision ổn định nhờ BM25 + Dense + RRF fusion.
3. Case study — 1 failure, Error Tree walkthrough: Question "Người nộp thuế trong tờ khai GTGT là công ty nào và mã số thuế là gì?" - Output sai → Context đúng? Có → Query OK? Không → Root cause: Prompt không hướng dẫn model extract thông tin cụ thể → Fix: Cải thiện prompt template.
4. Next optimization nếu có thêm 1 giờ: Tối ưu prompt engineering và thêm query expansion để cải thiện answer relevancy.
