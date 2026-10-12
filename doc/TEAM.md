# Nhóm thực hiện K4 Track 3A

Tên nhóm: NhomBotVN

Repo chung: https://github.com/haikunn11/K4-Track-3A-Day24-NhomBotVN-Eval-Guard

Trưởng nhóm/người nộp: Phạm Đình Hải - 2A202602482

Ngày lab/deadline áp dụng: 12/10/2026 23:59 — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: main

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Phạm Đình Hải | 2A202602482 | Trưởng nhóm, Setup Pipeline Day 18, Phase A (RAGAS) | Nhánh `hai-phase-a` (Commit src/phase_a_ragas.py, failure_clusters.md, artifacts/ragas_50q.json) |
| 2 | Nguyễn Minh Ngọc | 20240002 | Thành viên, Phase B (LLM Judge & Bias Calibration) | Commit src/phase_b_judge.py, bias_report.md, artifacts/judge_results.json |
| 3 | Nguyễn Văn Đại | 20240003 | Thành viên, Phase C (Guardrails Stack & Latency) | Nhánh `dai-phase-c` (Commit src/phase_c_guard.py, blueprint.md, artifacts/guard_results.json) |

Người tích hợp/chạy batch/nộp link: Phạm Đình Hải, chạy check_lab.py và nộp link qua vlearn.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: Windows 11, Python 3.11, MSVC C++ Build Tools.
Virtualenv/dependencies/imports: Đã cài đặt theo requirements/requirements.txt và requirements/constraints-core.txt.
Models/Qdrant/50 answers đã chuẩn bị: Qdrant Docker port 6333, model embedding BAAI/bge-m3, model LLM gpt-4o-mini.
Nếu cài full NeMo chưa thành công, ghi lỗi thực tế; không dùng unit test pass hoặc pip resolve để khẳng định runtime đã chạy.

## INDIVIDUAL

Sao chép mẫu cho mỗi thành viên; tiêu đề họ tên không dấu-MSSV.

### PhamDinhHai-2A202602482

- Phần được giao và phần thực tế đã làm: Trưởng nhóm, phụ trách sao chép module RAG Day 18 (m1-m5), chạy setup sinh 50 answers và thực hiện Phase A RAGAS evaluation (Tasks 1-4 trong src/phase_a_ragas.py).
- Bằng chứng: Nhánh làm việc cá nhân `hai-phase-a`. Commit mã nguồn src/phase_a_ragas.py, file artifacts/answers_50q.json, artifacts/ragas_50q.json, và báo cáo doc/reports/failure_clusters.md.
- Cách kiểm tra: Chạy unit test offline pytest tests/test_phase_a.py và thực nghiệm live python scripts/run_experiments.py --phase a --live.
- Điều đã học: Hiểu sâu về 4 metric RAGAS (faithfulness, answer_relevancy, context_precision, context_recall), phân cụm lỗi và phát hiện các bẫy câu hỏi adversarial.
- Giới hạn/cách xử lý: Xử lý các trường hợp context thiếu sót và tối ưu hóa việc phân bố câu hỏi chính xác.
- Nguồn/AI hỗ trợ nếu có: Sử dụng Antigravity AI coding assistant hỗ trợ đọc hiểu đề bài và rà soát cấu trúc code; tự kiểm chứng bằng pytest và check_lab.py.

### NguyenMinhNgoc-20240002

- Phần được giao và phần thực tế đã làm: Phụ trách Phase B (LLM-as-a-Judge, Pairwise evaluation, Swap-and-average, Cohen's Kappa và phân tích thiên lệch trong src/phase_b_judge.py).
- Bằng chứng: Commit mã nguồn src/phase_b_judge.py, file artifacts/judge_results.json và báo cáo doc/reports/bias_report.md.
- Cách kiểm tra: Chạy unit test offline pytest tests/test_phase_b.py và thực nghiệm live python scripts/run_experiments.py --phase b --live.
- Điều đã học: Hiểu cách thức LLM chấm điểm, kỹ thuật Swap-and-Average để triệt tiêu Position Bias, đo lường Verbosity Bias và đánh giá độ tin cậy qua hệ số Cohen's Kappa với nhãn người.
- Giới hạn/cách xử lý: Hiệu chỉnh prompt để đảm bảo JSON output ổn định và phản ánh chính xác tiêu chí đánh giá.
- Nguồn/AI hỗ trợ nếu có: Sử dụng Antigravity AI coding assistant hỗ trợ giải thích công thức; tự kiểm chứng bằng unit test và kiểm tra thủ công.

### NguyenVanDai-20240003

- Phần được giao và phần thực tế đã làm: Phụ trách Phase C (Production Guardrails, Presidio PII scanning, NeMo input/output rails, adversarial suite và đo P95 latency trong src/phase_c_guard.py).
- Bằng chứng: Nhánh làm việc cá nhân `dai-phase-c`. Commit mã nguồn src/phase_c_guard.py, file artifacts/guard_results.json và báo cáo doc/reports/blueprint.md.
- Cách kiểm tra: Chạy unit test offline pytest tests/test_phase_c.py và thực nghiệm live python scripts/run_experiments.py --phase c --live --latency-samples 20.
- Điều đã học: Triển khai lá chắn bảo vệ hai đầu với Microsoft Presidio và NeMo Guardrails, cân bằng giữa tỷ lệ chặn tấn công và kiểm soát false-positive, đo lường độ trễ P95 tuần tự.
- Giới hạn/cách xử lý: Tối ưu regex cho PII tiếng Việt (CCCD, SĐT) và xử lý event loop async trong NeMo Guardrails.
- Nguồn/AI hỗ trợ nếu có: Sử dụng Antigravity AI coding assistant hỗ trợ tra cứu NeMo docs; tự kiểm chứng qua test suite 28 câu.

## Cập nhật sau khi nộp

Bản nộp khởi tạo đúng hạn theo phân công nhiệm vụ của nhóm.
