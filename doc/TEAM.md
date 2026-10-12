# Nhóm thực hiện K4 Track 3A

Tên nhóm: LGBTree

Repo chung: https://github.com/long27112003/K4-L3-DAY24-LGBTree-Eval-Guard

Trưởng nhóm/người nộp: Nguyễn Hải Long (2A202602471)

Ngày lab/deadline áp dụng: 12/10/2026 23:59 — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: Chưa chốt; cập nhật sau khi tích hợp Phase C.

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Nguyễn Hải Long | 2A202602471 | Trưởng nhóm; tích hợp m1–m5, môi trường, tạo 50 answers và hợp nhất các phase | commits 8c796e5, 7dc08e5; artifacts/answers_50q.json |
| 2 | Ngô Tiến Dũng | 2A202602374 | Phase A: RAGAS Eval (Tasks 1–4) và báo cáo failure clusters | commits 06fe153, 24450de; src/phase_a_ragas.py, artifacts/ragas_50q.json, doc/reports/failure_clusters.md |
| 3 | Hoàng Anh Minh | 2A202602566 | Phase B: LLM-as-Judge (Tasks 5–8) và báo cáo bias | commit c9b4fd0, src/phase_b_judge.py, artifacts/judge_results.json, doc/reports/bias_report.md |
| 4 | Hà Anh Tuấn | 2A202602376 | Phase C: Presidio/NeMo guardrails (Tasks 9a–12), thực nghiệm input/output/latency và blueprint | Nhánh phase-c; src/phase_c_guard.py, artifacts/guard_results.json, doc/reports/blueprint.md |

Người tích hợp/chạy batch/nộp link: Nguyễn Hải Long tích hợp các nhánh và nộp link GitHub chung; Ngô Tiến Dũng chạy Phase A; Hoàng Anh Minh chạy Phase B; Hà Anh Tuấn phụ trách Phase C với Codex hỗ trợ triển khai, chạy và kiểm chứng.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: Windows 11, Python 3.11.9; xác nhận lại compiler trên máy chạy live trước khi nộp.
Virtualenv/dependencies/imports: `.venv` Python 3.11.9; import RAGAS, NeMo, Presidio, spaCy và SentenceTransformer thành công; `pip check` không phát hiện dependency hỏng. Model spaCy `en_core_web_lg` đã cài. API key được cấu hình riêng trong `.env`, không đưa vào repo. Phase A/B có kết quả live do các thành viên tương ứng cung cấp trong `artifacts/`.
Models/Qdrant/50 answers đã chuẩn bị: 50 answers đủ 20 factual, 20 multi_hop, 10 adversarial; cả 50 dùng `extractive_fallback`. Kiểm tra Qdrant local 1.9.7 tại cổng 6333: collection `lab24_production` trạng thái green với 108 points. NeMo sử dụng `gpt-4o-mini`, embedding phụ được cache khi khởi tạo runtime.
Nếu cài full NeMo chưa thành công, ghi lỗi thực tế; không dùng unit test pass
hoặc pip resolve để khẳng định runtime đã chạy.

## INDIVIDUAL

### NguyenHaiLong-2A202602471

- Phần được giao và phần thực tế đã làm: Trưởng nhóm; đưa năm module RAG Day18 vào repo, sửa tương thích Qdrant client và RAGAS metadata, cấu hình phiên bản PyArrow, tạo và kiểm tra 50 answers, tích hợp các nhánh.
- Bằng chứng: commit `8c796e5` tích hợp module Day18 và answers; merge commit `7dc08e5` tích hợp Phase B; `src/m1_chunking.py` đến `src/m5_enrichment.py`, `artifacts/answers_50q.json`.
- Cách kiểm tra: Chạy 60 support tests offline; kiểm tra 50 ids duy nhất, phân bố 20/20/10, không thiếu answer/contexts và đối chiếu với test set.
- Điều đã học: Phân biệt unit tests với thực nghiệm live; kiểm tra tương thích dependency và giao diện giữa pipeline Day18 với bài eval Day24.
- Giới hạn/cách xử lý: 50 answers dùng `extractive_fallback`; cần ghi rõ giới hạn này trong báo cáo và xác nhận backend Qdrant trước khi nộp.
- Nguồn/AI hỗ trợ nếu có: Dùng Codex hỗ trợ kiểm tra môi trường, tích hợp source và xử lý lỗi; đối chiếu bằng test và artifacts.

### NgoTienDung-2A202602374

- Phần được giao và phần thực tế đã làm: Hoàn thiện Phase A: hiện thực 4 hàm Task 1–4 trong src/phase_a_ragas.py (group_by_distribution, run_ragas_50q, bottom_10, cluster_analysis); cấu hình RunConfig giới hạn max_workers=2 trong src/m4_eval.py để tránh lỗi giới hạn đồng thời 402 OpenRouter; chạy thực nghiệm live trên 50 câu hỏi sinh artifacts/ragas_50q.json; điền và hoàn thiện báo cáo doc/reports/failure_clusters.md.
- Bằng chứng: commit `06fe153` triển khai Phase A, merge commit `24450de` (PR #1); mã nguồn tại src/phase_a_ragas.py và src/m4_eval.py; kết quả đánh giá tại artifacts/ragas_50q.json; báo cáo doc/reports/failure_clusters.md.
- Cách kiểm tra: Chạy offline pytest qua lệnh `python -m pytest tests/test_phase_a.py -v` (6/6 passed); chạy batch thực nghiệm qua `python scripts/run_experiments.py --phase a --live`; kiểm tra tính hợp lệ artifact qua `python scripts/check_lab.py`.
- Điều đã học: Hiểu và nắm vững 4 metric cốt lõi của RAGAS (faithfulness, answer_relevancy, context_precision, context_recall); phân biệt chẩn đoán nhóm lỗi theo chất lượng (avg_score thấp nhất) thay vì số lượng câu thuần túy; hiểu về các bẫy câu hỏi adversarial (xung đột phiên bản và điều kiện phủ định); kỹ năng xử lý rate-limit và concurrency khi gọi LLM evaluators.
- Giới hạn/cách xử lý: Khi chạy live với RAGAS mặc định 16 workers, OpenRouter báo lỗi 402 in_flight_budget_exhausted; đã khắc phục bằng cách cấu hình RunConfig(max_workers=2, max_retries=10) trong m4_eval.py.
- Nguồn/AI hỗ trợ nếu có: Sử dụng Antigravity AI hỗ trợ rà soát kiểm tra hợp đồng dữ liệu, debug lỗi concurrency API và cấu trúc báo cáo; toàn bộ code và artifact đều được tự kiểm chứng độc lập bằng pytest và check_lab.py.

### HoangAnhMinh-2A202602566

- Phần được giao và phần thực tế đã làm:
  - Phụ trách toàn bộ Phase B (LLM-as-Judge).
  - Cài đặt 4 task trong file `src/phase_b_judge.py`:
    + Task 5 (`pairwise_judge`): Gọi LLM judge đánh giá cặp câu trả lời dựa trên 3 tiêu chí (độ chính xác, độ đầy đủ, tính súc tích) với prompt có cấu trúc và phản hồi JSON.
    + Task 6 (`swap_and_average`): Xây dựng cơ chế đánh giá 2 lượt hoán đổi thứ tự (Pass 1: A/B, Pass 2: B/A), ánh xạ ngược kết quả và xác định tính nhất quán vị trí (`position_consistent`), tính điểm và kết luận `final_winner`.
    + Task 7 (`cohen_kappa`): Lập trình tính hệ số thỏa thuận Cohen's κ giữa phán quyết của LLM judge và nhãn chuẩn của chuyên gia con người (human labels) theo công thức xác suất thống kê.
    + Task 8 (`bias_report`): Thống kê và đo lường tỷ lệ Position bias và Verbosity bias, phân tích định lượng và đưa ra diễn giải chi tiết.
  - Sinh và kiểm chuẩn dữ liệu thực nghiệm `artifacts/judge_results.json`.
  - Soạn thảo và hoàn thiện toàn bộ báo cáo phân tích kỹ thuật `doc/reports/bias_report.md`.
- Bằng chứng:
  - Commit SHA: `c9b4fd0`.
  - Nhánh làm việc Git: `HoangAnhMinh-2A202602566-phase-B`.
  - Mã nguồn: `src/phase_b_judge.py`.
  - Artifact kiểm chuẩn: `artifacts/judge_results.json`.
  - Báo cáo phân tích: `doc/reports/bias_report.md`.
- Cách kiểm tra:
  - Chạy bộ unit tests offline: `pytest tests/test_phase_b.py` đạt 8/8 tests PASSED (0.04s).
  - Chạy kiểm tra hợp đồng dữ liệu: `pytest tests/test_report_contracts.py -k "phase_b"` đạt 4/4 tests PASSED.
  - Chạy kiểm tra runner: `pytest tests/test_support.py -k "phase_b"` đạt PASSED.
  - Chạy công cụ kiểm tra tổng thể `python scripts/check_lab.py`: Xác nhận đạt chuẩn đối với `phase_b_judge.py`, `Phase B artifact` và `doc/reports/bias_report.md`.
- Điều đã học:
  - Hiểu sâu sắc hiện tượng Position bias (thiên lệch vị trí) và Verbosity bias (thiên lệch độ dài) của LLM khi đóng vai trò người đánh giá.
  - Nắm vững cơ chế Swap-and-Average để triệt tiêu thiên lệch vị trí trong so sánh A/B.
  - Ý nghĩa và phương pháp tính hệ số Cohen's κ để định lượng mức độ tương đồng giữa quyết định của AI và con người trong bài toán đánh giá chất lượng RAG.
  - Kỹ thuật xây dựng prompt judge có ràng buộc schema JSON chặt chẽ và xử lý dữ liệu phục vụ quy trình CI/CD.
- Giới hạn/cách xử lý:
  - Giới hạn: Khi chạy ở quy mô lớn, việc gọi LLM judge cho mọi câu hỏi có thể tốn kém chi phí token và gặp vấn đề về rate limit API.
  - Cách xử lý: Đề xuất áp dụng LLM Judge như một tầng sàng lọc tự động (automated triage gate), kết hợp Human-in-the-Loop để can thiệp vào các trường hợp có điểm số sát nút hoặc khi hai lượt đánh giá không nhất quán (tie).
- Nguồn/AI hỗ trợ nếu có:
  - Sử dụng Antigravity AI Assistant hỗ trợ rà soát công thức tính toán và cấu trúc code. Tự kiểm chứng toàn bộ thông qua việc phân tích logic, chạy test suites và đối chiếu kết quả thực nghiệm.

### HaAnhTuan-2A202602376

- Phần được giao và phần thực tế đã làm: Phụ trách Tasks 9a–12 theo luồng TODO: quét/ẩn PII bằng Presidio; input/output self-check bằng NeMo; chạy attacks/clean controls; đo latency; tổng hợp blueprint từ A/B/C. Bổ sung bộ lọc định danh có cấu trúc để tránh NER tiếng Anh chặn nhầm tiếng Việt và làm rõ prompt input HR/IT trong config.yml. Giữ nguyên imports/helpers; không thêm ngoại lệ theo fixtures.
- Bằng chứng: nhánh `phase-c`; `src/phase_c_guard.py`, `guardrails/config.yml`, `artifacts/guard_results.json`, `doc/reports/phase_c_report.md` và `doc/reports/blueprint.md`. Commit cá nhân cần bổ sung khi chốt và tích hợp nhánh.
- Cách kiểm tra: Bộ tests gốc của starter đạt 86 passed, 3 deselected, gồm 12 tests Phase C. Batch `python scripts/run_experiments.py --phase c --live --latency-samples 20` với bộ lọc PII và prompt input hiện tại: 17/20 attacks, 8/8 clean allowed (false-positive rate 0%), 4/4 outputs đúng; 20 timed samples sau 2 warm-up, P95 input guard 833.754435ms, budget_ok=false. Artifact đáp ứng schema/metadata/phép tính và quality gate bắt buộc.
- Điều đã học: Quyết định guard phải dựa trên rail log, không dựa từ khóa từ chối; NER tiếng Anh gây false positives trên tiếng Việt; cần phân biệt chính sách mật khẩu chung với yêu cầu lấy mật khẩu thật. Latency input layers đo đủ hai tầng khác thời gian request dừng sớm và khác latency toàn hệ thống.
- Giới hạn/cách xử lý: Presidio kiểm tra định danh có cấu trúc, NeMo xử lý yêu cầu dữ liệu cá nhân và phạm vi chủ đề; chưa bao phủ toàn bộ PII tiếng Việt. Attacks ids 12/14/15 còn lọt; đạt yêu cầu bắt buộc nhưng chưa đạt bonus. Bộ 20/8/4 nhỏ và đã dùng để điều chỉnh, cần holdout trước production. P95 vượt mục tiêu 500ms được ghi đúng và phân tích trong blueprint.
- Nguồn/AI hỗ trợ nếu có: Dùng Codex hỗ trợ hoàn thiện code theo starter, phân tích false positives, điều chỉnh bộ lọc PII và prompt input trong config.yml, chạy pytest/batch thật và soạn báo cáo từ JSON. Tests, fixtures và requirements giữ nguyên bản gốc. Các số liệu live lấy từ artifact thực nghiệm, không dùng mock làm kết quả nộp bài.

## Cập nhật sau khi nộp

Chưa nộp bản cuối; cập nhật commit chấm và lịch sử sửa sau khi hoàn thành Phase C.
