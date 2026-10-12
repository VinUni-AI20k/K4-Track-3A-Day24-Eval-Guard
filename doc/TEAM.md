# Nhóm thực hiện K4 Track 3A

Tên nhóm: LGBTree

Repo chung: https://github.com/long27112003/K4-L3-DAY24-LGBTree-Eval-Guard

Trưởng nhóm/người nộp: Nguyễn Hoàng Long

Ngày lab/deadline áp dụng: 12/10/2026 23:59 — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: 8c796e5fd7ad091c433a17c065925ed5156fcd41

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Ngô Tiến Dũng | 2A202602374 | Phụ trách Phase A: RAGAS Eval (Tasks 1-4) & Báo cáo failure clusters | src/phase_a_ragas.py, artifacts/ragas_50q.json, failure_clusters.md |

Người tích hợp/chạy batch/nộp link: Ngô Tiến Dũng tích hợp và kiểm tra batch Phase A; Trưởng nhóm nộp link GitHub chung.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: Windows 11, Python 3.11.9.
Virtualenv/dependencies/imports: Đã kích hoạt môi trường ảo .venv, cài đặt đầy đủ requirements (ragas, langchain-openai, presidio, spacy).
Models/Qdrant/50 answers đã chuẩn bị: Qdrant vector database chạy local port 6333; 50 answers đã sinh đầy đủ trong artifacts/answers_50q.json (20 factual, 20 multi_hop, 10 adversarial).
Nếu cài full NeMo chưa thành công, ghi lỗi thực tế; không dùng unit test pass
hoặc pip resolve để khẳng định runtime đã chạy.

## INDIVIDUAL

Sao chép mẫu cho mỗi thành viên; tiêu đề họ tên không dấu-MSSV.

### NgoTienDung-2A202602374

- Phần được giao và phần thực tế đã làm: Hoàn thiện Phase A: hiện thực 4 hàm Task 1–4 trong src/phase_a_ragas.py (group_by_distribution, run_ragas_50q, bottom_10, cluster_analysis); cấu hình RunConfig giới hạn max_workers=2 trong src/m4_eval.py để tránh lỗi giới hạn đồng thời 402 OpenRouter; chạy thực nghiệm live trên 50 câu hỏi sinh artifacts/ragas_50q.json; điền và hoàn thiện báo cáo doc/reports/failure_clusters.md.
- Bằng chứng: Mã nguồn tại src/phase_a_ragas.py và src/m4_eval.py; kết quả đánh giá tại artifacts/ragas_50q.json; báo cáo doc/reports/failure_clusters.md.
- Cách kiểm tra: Chạy offline pytest qua lệnh `python -m pytest tests/test_phase_a.py -v` (6/6 passed); chạy batch thực nghiệm qua `python scripts/run_experiments.py --phase a --live`; kiểm tra tính hợp lệ artifact qua `python scripts/check_lab.py`.
- Điều đã học: Hiểu và nắm vững 4 metric cốt lõi của RAGAS (faithfulness, answer_relevancy, context_precision, context_recall); phân biệt chẩn đoán nhóm lỗi theo chất lượng (avg_score thấp nhất) thay vì số lượng câu thuần túy; hiểu về các bẫy câu hỏi adversarial (xung đột phiên bản và điều kiện phủ định); kỹ năng xử lý rate-limit và concurrency khi gọi LLM evaluators.
- Giới hạn/cách xử lý: Khi chạy live với RAGAS mặc định 16 workers, OpenRouter báo lỗi 402 in_flight_budget_exhausted; đã khắc phục bằng cách cấu hình RunConfig(max_workers=2, max_retries=10) trong m4_eval.py.
- Nguồn/AI hỗ trợ nếu có: Sử dụng Antigravity AI hỗ trợ rà soát kiểm tra hợp đồng dữ liệu, debug lỗi concurrency API và cấu trúc báo cáo; toàn bộ code và artifact đều được tự kiểm chứng độc lập bằng pytest và check_lab.py.

## Cập nhật sau khi nộp

Bản nộp chính thức đúng hạn; không có cập nhật phát sinh sau deadline.
