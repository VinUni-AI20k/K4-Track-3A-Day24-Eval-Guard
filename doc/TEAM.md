# Nhóm thực hiện K4 Track 3A

Tên nhóm: ThienBinh

Repo chung: https://github.com/longtqb04/K4-L3-DAY24-ThienBinh-Eval-Guard

Trưởng nhóm/người nộp: Trần Quốc Bảo Long - 2A202602696

Ngày lab/deadline áp dụng: 12/10/2026 23:59 — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: {{Commit SHA}}

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Trần Quóc Bảo Long | 2A202602696 | Phase B | {{Commit/PR/report}} |
| 2 | Trần Nhật Minh | 2A202602483 | Phase A | {{Commit/PR/report}} |
| 3 | Nguyễn Lê Phúc Thắng | 2A202602638 | Phase C | {{Commit/PR/report}} |

Người tích hợp/chạy batch/nộp link: Trần Quốc Bảo Long, đảm nhiệm Phase B. Bằng chứng: 

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: Windows 11, Python 3.11.
Virtualenv/dependencies/imports: {{Lệnh và kết quả}}.
Models/Qdrant/50 answers đã chuẩn bị: {{Bằng chứng và giới hạn/fallback}}.
Nếu cài full NeMo chưa thành công, ghi lỗi thực tế; không dùng unit test pass
hoặc pip resolve để khẳng định runtime đã chạy.

## INDIVIDUAL

Sao chép mẫu cho mỗi thành viên; tiêu đề họ tên không dấu-MSSV.

### TranQuocBaoLong-2A202602696

- Phần được giao và phần thực tế đã làm: Phase B, file `src\phase_b_judge.py`.
- Bằng chứng: Commit SHA 4a4e94a4ba0b656775858096d873adf8f6b88b0c
- Cách kiểm tra: Chạy runner B để tạo 5 cặp/2 lượt cùng 10 binary judgments đúng nguồn.
- Điều đã học: Pairwise A/B/tie và nhãn tốt/xấu 0/1 trả lời hai câu hỏi khác nhau. Hoán đổi thứ tự câu trả lời giúp đo mức bất nhất theo vị trí; Cohen’s κ đo mức đồng thuận giữa judge và nhãn người sau khi hiệu chỉnh đồng thuận ngẫu nhiên.
- Giới hạn/cách xử lý: Phần code Phase B đã hoàn thiện nhưng chưa được kiểm chứng bằng unit mock hoặc API live. Cần chạy tests offline khi môi trường cho phép, sau đó chạy `python scripts/run_experiments.py --phase b --live`, kiểm tra JSON và cập nhật báo cáo bias.
- Nguồn/AI hỗ trợ nếu có: Codex hỗ trợ triển khai Tasks 5–8 trong `src/phase_b_judge.py` theo hợp đồng trong README/ASSIGNMENT. Phạm vi gồm pairwise judge, swap-and-average, Cohen’s κ và bias report.

### TranNhatMinh-2A202602483

- Phần được giao và phần thực tế đã làm: Phase A, file `src\phase_a_ragas.py`, `src\config.py` và bổ sung các file M1-M5 từ pipeline lab.
- Bằng chứng: Commit SHA fb5a69fc2a47cb156319ce4022a3d5e8d625bf58.
- Cách kiểm tra: {{Unit mock hoặc live experiment, lệnh và kết quả}}.
- Điều đã học: {{Khái niệm và cách thể hiện trong bài}}.
- Giới hạn/cách xử lý: {{Vấn đề và kiểm chứng}}.
- Nguồn/AI hỗ trợ nếu có: {{Công cụ, phạm vi, cách tự kiểm chứng}}.

### NguyenLePhucThang-2A202602638

- Phần được giao và phần thực tế đã làm: Phase C, file `src\phase_c_guard.py`.
- Bằng chứng: Commit SHA 0fca76146c1cfe7aa2d64d19a55ee73a14e7f095.
- Cách kiểm tra: {{Unit mock hoặc live experiment, lệnh và kết quả}}.
- Điều đã học: {{Khái niệm và cách thể hiện trong bài}}.
- Giới hạn/cách xử lý: {{Vấn đề và kiểm chứng}}.
- Nguồn/AI hỗ trợ nếu có: {{Công cụ, phạm vi, cách tự kiểm chứng}}.

## Cập nhật sau khi nộp

Không có
