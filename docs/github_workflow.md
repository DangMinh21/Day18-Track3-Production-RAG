# GitHub Workflow Cho Nhóm 4 Thành Viên

## Mục tiêu

Làm song song M1-M4 mà ít conflict, review được chất lượng code và giữ nhánh `main` luôn chạy được.

## Branch strategy

| Nhánh | Người phụ trách | Nội dung |
|-------|-----------------|----------|
| `main` | Cả nhóm | Chỉ chứa code đã review và chạy được |
| `feature/tv1-m1-chunking` | TV1 | `src/m1_chunking.py`, test M1 |
| `feature/tv2-m2-hybrid-search` | TV2 | `src/m2_search.py`, test M2 |
| `feature/tv3-m3-reranking` | TV3 | `src/m3_rerank.py`, test M3 |
| `feature/tv4-m4-evaluation` | TV4 | `src/m4_eval.py`, `test_set.json`, reports |
| `feature/group-integration` | Cả nhóm | M5, pipeline, final docs |

## Setup lần đầu

```bash
git clone <repo-url>
cd Day18-Track3-Production-RAG
git status
```

Mỗi thành viên tạo branch riêng:

```bash
git checkout main
git pull origin main
git checkout -b feature/tv1-m1-chunking
```

Đổi tên branch tương ứng với từng TV.

## Quy trình làm việc hằng ngày

1. Cập nhật code mới nhất:

```bash
git checkout main
git pull origin main
git checkout feature/tvX-...
git merge main
```

2. Làm việc trong module được giao.

3. Chạy test module riêng:

```bash
pytest tests/test_mX.py -q
```

4. Commit nhỏ, message rõ:

```bash
git status
git add <files>
git commit -m "Implement M1 hierarchical chunking"
```

5. Push branch:

```bash
git push origin feature/tvX-...
```

6. Mở Pull Request vào `main`.

## Quy tắc Pull Request

Mỗi PR cần có:

- Mô tả đã sửa gì.
- Test command đã chạy và kết quả.
- Screenshot/log ngắn nếu có output quan trọng.
- Checklist không còn TODO trong module.
- Tag reviewer đúng theo vòng review:
  - TV1 review TV4
  - TV2 review TV1
  - TV3 review TV2
  - TV4 review TV3

## PR template gợi ý

```markdown
## Summary

- Implement ...
- Add fallback ...

## Tests

- [ ] pytest tests/test_mX.py -q
- [ ] pytest tests -q

## Notes

- Dependencies needed:
- Known limitations:
```

## Quy tắc tránh conflict

- TV1 chỉ sửa `src/m1_chunking.py` và reflection TV1.
- TV2 chỉ sửa `src/m2_search.py` và reflection TV2.
- TV3 chỉ sửa `src/m3_rerank.py` và reflection TV3.
- TV4 chỉ sửa `src/m4_eval.py`, `test_set.json`, report files và reflection TV4.
- `src/pipeline.py`, `src/m5_enrichment.py`, `requirements.txt`, `docker-compose.yml` chỉ sửa trên `feature/group-integration`.
- Nếu cần sửa file ngoài phạm vi, comment trên GitHub hoặc báo nhóm trước.

## Merge order đề xuất

1. Merge TV1 vì M1 tạo chunks cho pipeline.
2. Merge TV2 vì M2 cần chunks để index/search.
3. Merge TV3 vì M3 dùng output search để rerank.
4. Merge TV4 vì M4 dùng pipeline output để eval.
5. Tạo `feature/group-integration` từ `main` mới nhất.
6. Implement M5, pipeline, generation prompt, latency breakdown.
7. Chạy full tests và merge integration cuối cùng.

## Xử lý conflict

Khi Git báo conflict:

```bash
git status
```

Mở file conflict, giữ logic mới nhất từ cả hai bên. Sau khi sửa:

```bash
git add <file>
git commit
pytest tests -q
```

Không dùng `git reset --hard` hoặc force push lên branch người khác.

## Checklist trước khi merge PR

- [ ] Branch cập nhật với `main`.
- [ ] Không có file ngoài phạm vi bị sửa nhầm.
- [ ] Test module riêng pass.
- [ ] Reviewer đã approve.
- [ ] Không còn TODO trong module.
- [ ] Code không phụ thuộc bắt buộc vào API key nếu tests offline.

## Checklist release cuối

```bash
pytest tests -q
python main.py
python check_lab.py
git status
```

Các file cần có trước khi nộp:

- `reports/naive_baseline_report.json`
- `reports/ragas_report.json`
- `analysis/group_report.md`
- `analysis/failure_analysis.md`
- `analysis/reflections/reflection_TV1.md`
- `analysis/reflections/reflection_TV2.md`
- `analysis/reflections/reflection_TV3.md`
- `analysis/reflections/reflection_TV4.md`
