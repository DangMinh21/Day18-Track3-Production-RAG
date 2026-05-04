# Individual Reflection — Lab 18

**Tên:** Đặng Văn Minh  
**MSHV:** 2A202600027  
**Module phụ trách:** M4: Evaluation  
**Vai trò bổ sung:** Team Lead - Phân chia công việc, tạo data, kết nối pipeline tổng, chạy thực nghiệm

---

## 1. Đóng góp kỹ thuật

- Module đã implement: M4 Evaluation hoàn chỉnh với RAGAS integration và failure analysis.
- Các hàm/class chính đã viết: `evaluate_with_ragas()`, `analyze_failures()`, `ErrorTree` class.
- Số tests pass: 4/4
- **Team Lead contributions:** Phân chia công việc cho 4 thành viên (M1-M4), tạo test_set.json với 30 questions từ data BCTC và Nghị định, kết nối pipeline tổng trong `src/pipeline.py`, chạy thực nghiệm và generate reports.

## 2. Kiến thức học được

- Khái niệm mới nhất: RAGAS metrics (faithfulness, answer relevancy, context precision/recall) và cách sử dụng để đánh giá RAG systems; project management trong AI development.
- Điều bất ngờ nhất: Production pipeline phức tạp hơn nhưng scores có thể tệ hơn naive baseline ở một số metrics, nhấn mạnh tầm quan trọng của prompt engineering; vai trò team lead đòi hỏi balancing technical work với coordination.
- Kết nối với bài giảng (slide nào): Slide về evaluation metrics và error analysis trong RAG pipelines; slide về team collaboration in AI projects.

## 3. Khó khăn & Cách giải quyết

- Khó khăn lớn nhất: Implement failure analysis với Error Tree để diagnose root cause của failures; coordinate team để đảm bảo tất cả modules integrate đúng.
- Cách giải quyết: Nghiên cứu RAGAS documentation và xây dựng logic phân tích từng failure theo tree: Output → Context → Query; sử dụng GitHub để track progress và merge PRs.
- Thời gian debug: 30 phút để fix parsing RAGAS results và generate meaningful diagnoses; 1 giờ để debug pipeline integration issues.

## 4. Nếu làm lại

- Sẽ làm khác điều gì: Thêm automated prompt optimization để cải thiện answer relevancy; better upfront planning cho data creation.
- Module nào muốn thử tiếp: M2 Hybrid Search để hiểu sâu hơn về retrieval techniques; hoặc M1 Chunking để optimize data preprocessing.

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|----------|---------------|
| Hiểu bài giảng | 5 |
| Code quality | 4 |
| Teamwork | 5 |
| Problem solving | 4 |
| Leadership | 5 |