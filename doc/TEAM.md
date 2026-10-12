# Nhóm thực hiện K4 Track 3A

Tên nhóm: {{Tên nhóm}}

Repo chung: {{Link repo}}

Trưởng nhóm/người nộp: {{Họ tên và MSSV}}

Ngày lab/deadline áp dụng: {{Ngày giờ theo thông báo lớp}} — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: {{Commit SHA}}

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Võ Huy Hoàng | 2A202602548 | Phase A: triển khai Tasks 1–4 trong `src/phase_a_ragas.py` với AI hỗ trợ; điều chỉnh adapter `src/m4_eval.py`; chạy RAGAS thật trên 50 câu; đối chiếu và viết `doc/reports/failure_clusters.md`. | Commit/PR: bổ sung sau khi commit; `artifacts/ragas_50q.json`, `doc/reports/failure_clusters.md`. |
| 2 | {{Họ tên}} | {{MSSV}} | {{Phase/file/hàm}} | {{Commit/PR/report}} |
| 3 | {{Họ tên}} | {{MSSV}} | {{Phase/file/hàm}} | {{Commit/PR/report}} |

Người tích hợp/chạy batch/nộp link: {{Họ tên, công việc và bằng chứng}}.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: {{Phiên bản thực tế}}.
Virtualenv/dependencies/imports: {{Lệnh và kết quả}}.
Models/Qdrant/50 answers đã chuẩn bị: {{Bằng chứng và giới hạn/fallback}}.
Nếu cài full NeMo chưa thành công, ghi lỗi thực tế; không dùng unit test pass
hoặc pip resolve để khẳng định runtime đã chạy.

## INDIVIDUAL

Sao chép mẫu cho mỗi thành viên; tiêu đề họ tên không dấu-MSSV.

### VoHuyHoang-2A202602548

- Phần được giao và phần thực tế đã làm: Phase A Tasks 1–4 trong `src/phase_a_ragas.py` (nhóm 20/20/10 câu, gọi bốn metric RAGAS, lấy bottom 10, phân tích matrix và nhóm yếu); tích hợp `src/m4_eval.py` để chấm với `gpt-5-nano`; chạy Phase A trên 50 answers; đọc `answer`, `contexts`, `ground_truth` và hoàn thiện `doc/reports/failure_clusters.md`.
- Bằng chứng: commit/PR sẽ bổ sung sau khi commit; `artifacts/ragas_50q.json` có 50 kết quả thật, 10 bottom rows và metadata evaluator; `doc/reports/failure_clusters.md` có số liệu, đối chiếu từng câu yếu và phân tích bẫy ID 41/48.
- Cách kiểm tra: đã chạy `.\.venv\Scripts\python.exe scripts/run_experiments.py --phase a --live` và tạo `artifacts/ragas_50q.json`; `.\.venv\Scripts\python.exe -m pytest tests/test_phase_a.py -q` đạt 6/6; kiểm tra offline schema, metadata nguồn và Markdown Phase A đều đạt. Không dùng unit test thay cho bằng chứng API thật.
- Điều đã học: RAGAS là tín hiệu chẩn đoán, không phải đáp án chuẩn; phân biệt lỗi truy xuất thiếu chứng cứ với bước tạo câu trả lời từ chối quá mức; chọn nhóm yếu theo điểm trung bình, không theo số phần tử của matrix; giữ riêng model generation và evaluator trong metadata.
- Giới hạn/cách xử lý: bản M4 ban đầu không tương thích `temperature` của `gpt-5-nano`; đã bỏ tham số này trước request. Lượt chấm tiếp theo gặp timeout và ba answer ngắn khó tách câu; đã chỉnh adapter rồi chạy thành công. Điểm tự động vẫn có thể lệch chứng cứ (ví dụ ID 8, 25); báo cáo giữ giới hạn đó và nêu mâu thuẫn cần làm rõ ở ID 26 thay vì sửa reference.
- Nguồn/AI hỗ trợ: Codex hỗ trợ triển khai và rà soát mã Phase A/M4, xử lý lỗi adapter, đối chiếu JSON với contexts, soạn báo cáo và chạy kiểm tra offline. Tôi chạy batch live; artifact và báo cáo cần được tôi rà soát trước khi nộp cho nhóm.

### {{HoVaTen}}-{{MSSV}}

- Phần được giao và phần thực tế đã làm: {{Nhiệm vụ, file/hàm, mục đích}}.
- Bằng chứng: {{Commit/PR và artifacts/reports liên quan}}.
- Cách kiểm tra: {{Unit mock hoặc live experiment, lệnh và kết quả}}.
- Điều đã học: {{Khái niệm và cách thể hiện trong bài}}.
- Giới hạn/cách xử lý: {{Vấn đề và kiểm chứng}}.
- Nguồn/AI hỗ trợ nếu có: {{Công cụ, phạm vi, cách tự kiểm chứng}}.

## Cập nhật sau khi nộp

{{Ghi phiên bản nộp; nếu sửa sau deadline, ghi commit/thời điểm/lý do và thông báo
coach cho phép áp dụng bản cập nhật. Nếu không có cập nhật, ghi rõ không có.}}
