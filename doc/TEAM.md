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
| 1 | Đặng Quốc Cường | 2A202602466 | Phase C: triển khai Tasks 9a, 9b, 10, 11, 12 trong src/phase_c_guard.py; phần báo cáo latency và rà soát guard chờ kết quả chạy thật | Commit 7597ac6; mục INDIVIDUAL DangQuocCuong-2A202602466 |
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

### DangQuocCuong-2A202602466

- Phần được giao và phần thực tế đã làm: Tôi phụ trách Phase C, gồm Tasks 9a, 9b, 10, 11, 12 trong `src/phase_c_guard.py`, mục latency của `doc/reports/blueprint.md` và rà soát kết quả guard. Tôi đã triển khai `pii_scan` để lọc và ẩn danh CCCD/CMND, điện thoại Việt Nam, email; `check_input_rail` và `check_output_rail` để lấy quyết định từ trạng thái `stop` của rail, giữ nguyên câu trả lời an toàn hoặc thay thế nội dung bị chặn; `run_adversarial_suite` để kiểm tra input theo thứ tự Presidio → NeMo và ghi nhận `blocked_by`; `measure_p95_latency` để đo hai tầng input tuần tự sau hai lượt warm-up. Phần báo cáo latency và rà soát kết quả chạy thật còn chờ dữ liệu của nhóm.
- Bằng chứng: Commit `7597ac6596dad164c24ec5faaf713a5b06532ca9` (`Phase C: Tasks 9a-12`), tác giả `cuongdqhe187188-glitch`, ngày 12/10/2026, chứa thay đổi trong `src/phase_c_guard.py`. Nhánh cá nhân là `dangquoccuong_2A202602466`; báo cáo đóng góp được ghi tại mục INDIVIDUAL này. Chưa có `artifacts/guard_results.json` trong bản repo hiện tại để đối chiếu số đo latency hoặc kết quả guard thực tế.
- Cách kiểm tra: Chạy `.\.venv\Scripts\python.exe -m pytest tests/test_phase_c.py -q` trên Python 3.12.10, kết quả `12 passed`. Bộ test dùng engine giả, kiểm tra phát hiện/ẩn danh PII, quyết định input/output rail, batch 28 input gồm 20 attacks và 8 clean controls, cùng số lượt warm-up và mẫu latency. Lệnh `Select-String -Path src\phase_c_guard.py -Pattern '# TODO'` không trả kết quả. Các kết quả này xác nhận logic với mock; số đo và tỷ lệ đạt khi chạy thật cần lấy từ artifacts của nhóm.
- Điều đã học: Tôi hiểu cách kết hợp bộ phát hiện PII với input/output rails trong pipeline RAG và cách dùng engine được truyền vào để kiểm thử độc lập với API. Quyết định chặn phải dựa vào rail thay vì dò câu từ chối; nhãn `expected` chỉ dùng để so sánh kết quả. Khi đo latency cần tái sử dụng engine, loại warm-up khỏi mẫu, dùng `time.perf_counter()` và tính percentile từ các mẫu thô; P95 tổng được tính từ tổng thời gian từng mẫu qua `summarize_latency`.
- Giới hạn/cách xử lý: Bản repo hiện tại chưa có artifacts chạy thật nên chưa kết luận mức chặn attacks, false positives, độ đúng của bốn output cases hoặc việc đạt ngân sách 500 ms. Phép đo Task 12 chỉ bao gồm Presidio và NeMo input chạy đầy đủ hai tầng; RAG, output rail và toàn bộ request còn chưa đo. Sau khi Giang cung cấp `guard_results.json`, tôi sẽ đối chiếu các dòng không đạt, `blocked_by`, P50/P95/P99 và `latency_budget_ok`, rồi điền mục latency trong blueprint. Lần kiểm tra cá nhân dùng Python 3.12.10; môi trường Python 3.11 theo yêu cầu lab và hành vi Presidio/NeMo thật cần được nhóm xác nhận khi chạy thực nghiệm.
- Nguồn/AI hỗ trợ nếu có: Tài liệu phân công `Goi-C_DangQuocCuong_PhaseC.md`, yêu cầu lab và bộ test trong repo là nguồn đối chiếu phạm vi công việc. ChatGPT/Codex hỗ trợ tổng hợp, diễn đạt báo cáo này và chạy lại kiểm tra; nội dung được đối chiếu với mã nguồn, tác giả/SHA commit và đầu ra pytest. Số liệu thực nghiệm phải lấy từ artifacts chạy thật của nhóm.

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
