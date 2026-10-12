# Nhóm thực hiện K4 Track 3A

Tên nhóm: Latentia

Repo chung: https://github.com/minhtuann1102/K4-L3-DAY24-Latentia-Eval-Guard

Trưởng nhóm/người nộp: Nguyễn Minh Tuấn - MSSV: 2A202602420

Ngày lab/deadline áp dụng: 2024-10-12 23:59 — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: main

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Nguyễn Minh Tuấn | 2A202602420 | Trưởng nhóm, phụ trách tích hợp m1-m5, sinh answers và Phase A (src/phase_a_ragas.py) | Commit trên nhánh feat/phase-a và báo cáo failure_clusters.md |
| 2 | Nguyễn Minh Thắng | 2A202602706 | Thành viên, phụ trách Phase B (src/phase_b_judge.py) | Commit trên nhánh feat/phase-b và báo cáo bias_report.md |
| 3 | Nguyễn Thị Vàng | 2A202602897 | Thành viên, phụ trách Phase C (src/phase_c_guard.py) | Commit trên nhánh feat/phase-c và đóng góp blueprint.md |

Người tích hợp/chạy batch/nộp link: Nguyễn Minh Tuấn, tích hợp PR và nộp link GitHub.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: Windows 11 / Python 3.11 / MSVC C++ Build Tools.
Virtualenv/dependencies/imports: Đã cài đặt qua requirements.txt và constraints-core.txt.
Models/Qdrant/50 answers đã chuẩn bị: Qdrant v1.9.7 docker running port 6333, embedding & cross-encoder ready, setup_answers.py.
Nếu cài full NeMo chưa thành công, ghi lỗi thực tế; không dùng unit test pass
hoặc pip resolve để khẳng định runtime đã chạy.

## INDIVIDUAL

Sao chép mẫu cho mỗi thành viên; tiêu đề họ tên không dấu-MSSV.

### NguyenMinhTuan-20240001

- Phần được giao và phần thực tế đã làm: Phụ trách tích hợp pipeline RAG Day 18, sinh answers_50q.json, hoàn thành Tasks 1-4 trong src/phase_a_ragas.py và viết failure_clusters.md.
- Bằng chứng: Commits trên Git và file artifacts/ragas_50q.json, failure_clusters.md.
- Cách kiểm tra: python -m pytest tests/test_phase_a.py và python scripts/run_experiments.py --phase a --live.
- Điều đã học: Hiểu sâu về 4 metric RAGAS, phân tích nguyên nhân lỗi retrieval vs generation và các bẫy bối cảnh/phiên bản.
- Giới hạn/cách xử lý: Xử lý ngoại lệ mô hình evaluator m4 trả về và cấu hình timeout khi sinh 50 câu.
- Nguồn/AI hỗ trợ nếu có: Tham khảo tài liệu RAGAS, đề bài và AI coding assistant để debug cú pháp.

### NguyenMinhThang-20240002

- Phần được giao và phần thực tế đã làm: Phụ trách Phase B gồm Tasks 5-8 trong src/phase_b_judge.py, đo lường position bias, verbosity bias và viết bias_report.md.
- Bằng chứng: Commits trên Git và file artifacts/judge_results.json, bias_report.md.
- Cách kiểm tra: python -m pytest tests/test_phase_b.py và python scripts/run_experiments.py --phase b --live.
- Điều đã học: Hiểu cách LLM-as-a-judge bị bias theo vị trí (position bias), kỹ thuật swap-and-average và hiệu chuẩn nhãn nhị phân với Cohen's kappa.
- Giới hạn/cách xử lý: Đảm bảo prompt JSON nghiêm ngặt và không leak human labels vào prompt đánh giá.
- Nguồn/AI hỗ trợ nếu có: Tham khảo tài liệu scikit-learn, OpenAI JSON mode và đề bài.

### NguyenThiVang-20240003

- Phần được giao và phần thực tế đã làm: Phụ trách Phase C gồm Tasks 9a-12 trong src/phase_c_guard.py, thiết lập Presidio PII, NeMo input/output rails, chạy adversarial suite và đo P95 latency.
- Bằng chứng: Commits trên Git và file artifacts/guard_results.json, đóng góp vào blueprint.md.
- Cách kiểm tra: python -m pytest tests/test_phase_c.py và python scripts/run_experiments.py --phase c --live --latency-samples 20.
- Điều đã học: Nắm vững cấu trúc bảo vệ nhiều lớp, nhận diện PII đặc thù VN (CCCD, SĐT), chặn jailbreak mà không gây false positive trên câu sạch.
- Giới hạn/cách xử lý: Tối ưu latency, loại bỏ 2 vòng warm-up khỏi thống kê percentile tuyến tính.
- Nguồn/AI hỗ trợ nếu có: Tham khảo tài liệu NeMo Guardrails, Presidio Analyzer và đề bài.

## Cập nhật sau khi nộp

Bản nộp chính thức theo commit SHA cuối cùng trước deadline. Không có cập nhật sửa đổi sau deadline.
