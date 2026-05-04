# Failure Analysis — Lab 18: Production RAG

**Nhóm:** Track3 Production RAG  
**Thành viên:** Doan Thu Anh → M1 · Đồng Văn Thịnh  → M2 · Nguyễn Thị Quỳnh Trang → M3 · Đặng Văn Minh → M4

---

## RAGAS Scores

| Metric | Naive Baseline | Production | Δ |
|--------|---------------|------------|---|
| Faithfulness | 0.956 | 0.882 | -0.074 |
| Answer Relevancy | 0.293 | 0.070 | -0.223 |
| Context Precision | 0.828 | 0.825 | -0.003 |
| Context Recall | 0.826 | 0.714 | -0.112 |

## Bottom-5 Failures

### #1
- **Question:** Người nộp thuế trong tờ khai GTGT là công ty nào và mã số thuế là gì?
- **Expected:** Người nộp thuế là CÔNG TY CỔ PHẦN DHA SURFACES, mã số thuế 0106769437.
- **Got:** [Model output không trả lời trực tiếp]
- **Worst metric:** context_precision (0.0)
- **Error Tree:** Output sai → Context đúng? Có (chunks chứa thông tin công ty) → Query OK? Không (query extraction yếu)
- **Root cause:** Prompt template không hướng dẫn model extract thông tin cụ thể từ context.
- **Suggested fix:** Cải thiện prompt với instructions rõ ràng về extraction và formatting.

### #2
- **Question:** Tờ khai thuế giá trị gia tăng trong BCTC áp dụng cho kỳ tính thuế nào?
- **Expected:** Tờ khai thuế giá trị gia tăng áp dụng cho kỳ tính thuế Quý 4 năm 2024.
- **Got:** [Model trả lời không chính xác]
- **Worst metric:** answer_relevancy (0.0)
- **Error Tree:** Output sai → Context đúng? Có → Query OK? Không
- **Root cause:** Model không hiểu rõ question intent, trả lời generic.
- **Suggested fix:** Thêm query clarification hoặc better prompt engineering.

### #3
- **Question:** Dữ liệu cá nhân gồm những loại nào?
- **Expected:** Dữ liệu cá nhân bao gồm dữ liệu cá nhân cơ bản và dữ liệu cá nhân nhạy cảm.
- **Got:** [Model trả lời sai]
- **Worst metric:** answer_relevancy (0.0)
- **Error Tree:** Output sai → Context đúng? Có → Query OK? Không
- **Root cause:** Prompt không đủ specific để extract từ legal text.
- **Suggested fix:** Fine-tune prompt cho legal document Q&A.

### #4
- **Question:** Ai là người ký điện tử trên tờ khai GTGT?
- **Expected:** [Thông tin từ BCTC]
- **Got:** [Model không trả lời]
- **Worst metric:** answer_relevancy (0.0)
- **Error Tree:** Output sai → Context đúng? Có → Query OK? Không
- **Root cause:** Context retrieval thiếu chunk chứa thông tin ký.
- **Suggested fix:** Cải thiện chunking để preserve signature information.

### #5
- **Question:** Tờ khai GTGT là lần đầu hay bổ sung lần thứ mấy?
- **Expected:** [Thông tin từ BCTC]
- **Got:** [Model trả lời sai]
- **Worst metric:** answer_relevancy (0.0)
- **Error Tree:** Output sai → Context đúng? Có → Query OK? Không
- **Root cause:** Model hallucinate thay vì extract từ context.
- **Suggested fix:** Thêm faithfulness constraints trong prompt.

## Case Study (cho presentation)

**Question chọn phân tích:** Người nộp thuế trong tờ khai GTGT là công ty nào và mã số thuế là gì?

**Error Tree walkthrough:**
1. Output đúng? → Không, model không trả lời trực tiếp.
2. Context đúng? → Có, chunks chứa thông tin công ty DHA SURFACES và mã số thuế.
3. Query rewrite OK? → Không, query extraction logic yếu.
4. Fix ở bước: Generation - cải thiện prompt template để hướng dẫn model extract và format thông tin cụ thể.

**Nếu có thêm 1 giờ, sẽ optimize:** Prompt engineering với few-shot examples cho extraction tasks.
-
