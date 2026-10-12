# Nhóm thực hiện K4 Track 3A

Tên nhóm: Latentia

Repo chung: https://github.com/minhtuann1102/K4-L3-DAY24-Latentia-Eval-Guard

Trưởng nhóm/người nộp: Nguyễn Minh Tuấn - MSSV: 2A202602420

Ngày lab/deadline áp dụng: 2026-10-12 23:59 — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: Trưởng nhóm cần chọn SHA cuối cùng sau khi A/C và checker hoàn tất; hiện theo dõi nhánh main.

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Nguyễn Minh Tuấn | 2A202602420 | Trưởng nhóm, phụ trách tích hợp m1-m5, sinh answers và Phase A (src/phase_a_ragas.py) | Commit trên nhánh feat/phase-a và báo cáo failure_clusters.md |
| 2 | Nguyễn Minh Thắng | 2A202602706 | Thành viên, phụ trách Phase B (src/phase_b_judge.py) | PR #1 Tasks 5–8; artifact live judge_results.json và bias_report.md của lượt 12/10/2026 |
| 3 | Nguyễn Thị Vàng | 2A202602897 | Thành viên, phụ trách Phase C (src/phase_c_guard.py) | Commit trên nhánh feat/phase-c và đóng góp blueprint.md |

Người tích hợp/chạy batch/nộp link: Nguyễn Minh Tuấn, tích hợp PR và nộp link GitHub.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: Windows 11 / Python 3.11 / MSVC C++ Build Tools.
Virtualenv/dependencies/imports: Đã cài đặt qua requirements.txt và constraints-core.txt.
Models/Qdrant/50 answers đã chuẩn bị: Qdrant v1.9.7 docker running port 6333, embedding & cross-encoder ready, setup_answers.py.
Nếu cài full NeMo chưa thành công, ghi lỗi thực tế; không dùng unit test pass
hoặc pip resolve để khẳng định runtime đã chạy.

### Môi trường kiểm chứng của Nguyễn Minh Thắng — 12/10/2026

Python 3.11.17 trong Conda `vinai_env` tại `D:\DayVinAI\envs\vinai_env`;
Annoy 1.17.3 dùng binary conda-forge, không build bằng MSVC trên máy này.
`pip check`: No broken requirements found. Bộ runtime đã được kiểm chứng khi
chuẩn bị môi trường; batch Phase B lần này dùng key trong `.env` và CA Windows,
không tắt xác minh TLS. Key không nằm trong source, report hoặc commit.
Metadata live được lưu lúc 12/10/2026 20:18:45 UTC+07:00. Model judge yêu cầu là gpt-4o-mini.
Mô tả Build Tools ở môi trường chung phía trên không phải bằng chứng máy Thắng
đã cài compiler. Kiến trúc pipeline hiện tại và giới hạn A/C xem blueprint/review.

Trạng thái đóng gói: B hoàn thành; A có số đo nhưng source hashes không khớp;
C còn TODO và thiếu guard_results.json. Deadline đã được người dùng xác nhận
12/10/2026 23:59 UTC+07:00. Chưa có bằng chứng nhóm đã nộp qua vlearn.

## INDIVIDUAL

Sao chép mẫu cho mỗi thành viên; tiêu đề họ tên không dấu-MSSV.

### NguyenMinhTuan-2A202602420

- Phần được giao và phần thực tế đã làm: Phụ trách tích hợp pipeline RAG Day 18, sinh answers_50q.json, hoàn thành Tasks 1-4 trong src/phase_a_ragas.py và viết failure_clusters.md.
- Bằng chứng: Commits trên Git và file artifacts/ragas_50q.json, failure_clusters.md.
- Cách kiểm tra: python -m pytest tests/test_phase_a.py và python scripts/run_experiments.py --phase a --live.
- Điều đã học: Hiểu sâu về 4 metric RAGAS, phân tích nguyên nhân lỗi retrieval vs generation và các bẫy bối cảnh/phiên bản.
- Giới hạn/cách xử lý: Xử lý ngoại lệ mô hình evaluator m4 trả về và cấu hình timeout khi sinh 50 câu.
- Nguồn/AI hỗ trợ nếu có: Tham khảo tài liệu RAGAS, đề bài và AI coding assistant để debug cú pháp.

### NguyenMinhThang-2A202602706

**Nguyễn Minh Thắng — MSSV 2A202602706.**

- Phần được giao và thực tế đã làm: Hoàn thành Phase B Tasks 5–8; kiểm thử JSON judge, swap winner/scores, Cohen κ và bias proxies; chạy batch live, viết bias_report.md và tổng hợp blueprint/submission review.
- Bằng chứng: 4 commit theo task (488244f, 0d5f510, 09dbb98, e25635b), test fe68869, docs 06025b1 trên PR #1 đã merge; artifacts/judge_results.json với timestamp 2026-10-12T13:18:45.107165+00:00. Báo cáo ghi tên Nguyễn Minh Thắng và đúng source hashes.
- Cách kiểm tra: 42 tests Phase B và 102 tests Phase B/helper/contracts pass offline; một batch live gồm 10 pairwise calls và 10 binary judgments. Artifact live qua schema, source ids, metadata/hashes và phép tính. Checker toàn nhóm còn lỗi A/C, không khai toàn repo đã pass.
- Kết quả: κ=1.0, agreement 10/10; position inconsistency 2/5 (40%); longer-answer win proxy 3/3 decisive (100%). Proxy không chứng minh nguyên nhân bias, reasoning còn cần review dù label khớp.
- Điều đã học: Quy đổi hai lượt về cùng A/B gốc; calibration đánh giá đúng model_answer của fixture; phân biệt agreement, reasoning quality và vị trí/độ dài là confound; không dùng pairwise winner thay nhãn tốt/xấu.
- Giới hạn/cách xử lý: Mẫu 5 cặp/10 nhãn nhỏ; đọc ID 12/41 và các reasoning suy thêm điều kiện. Phase A còn stale source hashes; Phase C của Vàng chưa implement/chưa có artifact; theo dõi tại SUBMISSION_REVIEW.md trước nộp.
- Nguồn/AI hỗ trợ: README, đề bài/rubric/scaffold của repo; Codex hỗ trợ implementation, kiểm thử biên song song, chạy API và phân tích JSON thật. Mock chỉ phục vụ test, không được khai là live evidence.

### NguyenThiVang-2A202602897

- Phần được giao và phần thực tế đã làm: Phụ trách Phase C gồm Tasks 9a-12 trong src/phase_c_guard.py, thiết lập Presidio PII, NeMo input/output rails, chạy adversarial suite và đo P95 latency.
- Bằng chứng: Commits trên Git và file artifacts/guard_results.json, đóng góp vào blueprint.md.
- Cách kiểm tra: python -m pytest tests/test_phase_c.py và python scripts/run_experiments.py --phase c --live --latency-samples 20.
- Điều đã học: Nắm vững cấu trúc bảo vệ nhiều lớp, nhận diện PII đặc thù VN (CCCD, SĐT), chặn jailbreak mà không gây false positive trên câu sạch.
- Giới hạn/cách xử lý: Tối ưu latency, loại bỏ 2 vòng warm-up khỏi thống kê percentile tuyến tính.
- Nguồn/AI hỗ trợ nếu có: Tham khảo tài liệu NeMo Guardrails, Presidio Analyzer và đề bài.

## Cập nhật sau khi nộp

Chưa ghi nhận lần nộp chính thức. Trưởng nhóm chọn commit SHA đã qua checks trước deadline; nếu sửa sau khi nộp, ghi SHA/thời điểm/lý do và điều kiện coach cho phép.
