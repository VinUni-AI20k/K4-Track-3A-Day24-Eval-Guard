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
| 1 | {{Họ tên}} | {{MSSV}} | {{Phase/file/hàm}} | {{Commit/PR/report}} |
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

### {{HoVaTen}}-{{MSSV}}

- Phần được giao và phần thực tế đã làm: {{Nhiệm vụ, file/hàm, mục đích}}.
- Bằng chứng: {{Commit/PR và artifacts/reports liên quan}}.
- Cách kiểm tra: {{Unit mock hoặc live experiment, lệnh và kết quả}}.
- Điều đã học: {{Khái niệm và cách thể hiện trong bài}}.
- Giới hạn/cách xử lý: {{Vấn đề và kiểm chứng}}.
- Nguồn/AI hỗ trợ nếu có: {{Công cụ, phạm vi, cách tự kiểm chứng}}.

### TranAnhQuan-2A202602598

- **Phần được giao và phần thực tế đã làm:** Phụ trách Phase B, Tasks 5–8 trong `src/phase_b_judge.py`: triển khai pairwise judge theo reference, hoán đổi thứ tự và quy đổi winner/scores, tính Cohen’s κ và thống kê position/verbosity bias. Báo cáo kỹ thuật đang chờ kết quả thực nghiệm.
- **Bằng chứng:** Commit `cdb36d9` triển khai Tasks 5–8; commit `71b14f5` chuyển helper/import vào hàm và tách lời gọi API khỏi xử lý validation. Báo cáo dự kiến tại `doc/reports/bias_report.md`, chưa có số liệu thật.
- **Cách kiểm tra:** Đã rà soát tĩnh mã nguồn và xác nhận không còn `# TODO`. Chưa xác minh kết quả unit tests. Khi môi trường sẵn sàng, chạy `.\.venv-tests\Scripts\python.exe -m pytest tests/test_phase_b.py -q`; bổ sung kết quả thực tế sau.
- **Điều đã học:** Phân biệt winner A/B/tie với nhãn chất lượng 0/1; cần quy đổi lượt swap về thứ tự gốc trước khi đối chiếu. κ xét cả đồng thuận quan sát và đồng thuận do ngẫu nhiên; tỷ lệ winner dài hơn chưa chứng minh nguyên nhân thiên lệch.
- **Giới hạn/cách xử lý:** Chưa có `artifacts/judge_results.json`, nên chưa kết luận κ hoặc bias. Chờ Giang chạy batch thật; dùng kết quả JSON để hoàn thiện báo cáo, không tự điền số hoặc chạy lại nhằm tăng κ.
- **Nguồn/AI hỗ trợ nếu có:** Sử dụng Codex hỗ trợ lập kế hoạch, rà soát tiến độ và hợp đồng hàm theo tài liệu phân công, đề bài và tests được cấp. Kiểm chứng hiện tại bằng đối chiếu tĩnh; kiểm thử mock và đối chiếu kết quả thật còn chờ thực hiện.

## Cập nhật sau khi nộp

{{Ghi phiên bản nộp; nếu sửa sau deadline, ghi commit/thời điểm/lý do và thông báo
coach cho phép áp dụng bản cập nhật. Nếu không có cập nhật, ghi rõ không có.}}
