# Plan TV1 — M1 Advanced Chunking

## Mục tiêu

TV1 chịu trách nhiệm hoàn thành `src/m1_chunking.py` để `pytest tests/test_m1.py -q` pass 100% và cung cấp chunks tốt cho pipeline production.

## Nhiệm vụ chính

| Hàm | Yêu cầu | Ghi chú |
|-----|---------|---------|
| `chunk_semantic()` | Nhóm câu theo similarity | Có fallback không cần tải model |
| `chunk_hierarchical()` | Tạo parent/child chunks | Child có `parent_id` hợp lệ |
| `chunk_structure_aware()` | Parse Markdown headers | Preserve headers, metadata có `section` |
| `compare_strategies()` | So sánh 4 strategies | Trả dict đủ keys cho tests |

## Cách implement đề xuất

1. Sửa `chunk_semantic()`:
   - Split câu bằng regex theo dấu câu và paragraph.
   - Thử dùng `sentence_transformers` nếu đã cài.
   - Nếu thiếu dependency, fallback bằng token overlap/Jaccard similarity để tests vẫn pass.
   - Metadata mỗi chunk có `chunk_index` và `strategy="semantic"`.

2. Sửa `chunk_hierarchical()`:
   - Gom paragraphs đến gần `parent_size`.
   - Mỗi parent có metadata `chunk_type="parent"` và `parent_id`.
   - Tách child bằng sliding window hoặc paragraph-aware split theo `child_size`.
   - Mỗi child có `parent_id` trỏ đến parent hợp lệ.

3. Sửa `chunk_structure_aware()`:
   - Split theo headers `#{1,3}`.
   - Mỗi chunk gồm header + content.
   - Metadata có `section`, `strategy="structure"`, `chunk_index`.

4. Sửa `compare_strategies()`:
   - Chạy basic, semantic, hierarchical, structure trên toàn bộ documents.
   - Tính `num_chunks`, `avg_length`, `min_length`, `max_length`.
   - Với hierarchical, ghi thêm `num_parents`, `num_children`.

## Lệnh kiểm tra

```bash
pytest tests/test_m1.py -q
python -m src.m1_chunking
```

## Definition of Done

- [ ] `pytest tests/test_m1.py -q` pass.
- [ ] Không còn `# TODO` trong `src/m1_chunking.py`.
- [ ] `compare_strategies()` trả đủ `basic`, `semantic`, `hierarchical`, `structure`.
- [ ] TV2 có thể dùng output children từ hierarchical để index.

## Branch & PR

- Branch: `feature/tv1-m1-chunking`
- PR title: `Implement M1 advanced chunking`
- Reviewer chính: TV2
- Không sửa file module của TV2-TV4 trừ khi có thống nhất trên PR.
