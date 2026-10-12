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

OS/Python/compiler: Windows 11 Home 10.0.26200; Python 3.11.9 (virtualenv `.venv`; máy có sẵn 3.12 nhưng NeMo 0.10 chỉ hỗ trợ đến 3.11); Microsoft Visual Studio Build Tools 2022 (17.14, workload VCTools) để build `annoy==1.17.3`.
Virtualenv/dependencies/imports: `py -3.11 -m venv .venv` → `pip install -r requirements/requirements.txt -c requirements/constraints-core.txt`: annoy build wheel thành công. Lỗi thực tế: pyarrow 26 kéo theo yêu cầu NumPy 2 xung đột với pin `numpy==1.26.4` (`ImportError: pyarrow requires NumPy 2.0`) → cài `pyarrow<20`. Sau đó `pip check`: "No broken requirements found"; `import ragas, nemoguardrails, annoy, presidio_analyzer, spacy`: OK; `python -m spacy download en_core_web_lg`: OK; unit tests 86 passed, 3 deselected (integration).
Models/Qdrant/50 answers đã chuẩn bị: Qdrant `qdrant/qdrant:v1.9.7` qua `docker compose -f infra/docker-compose.yml up -d`; embedding BGE-M3 + reranker tải từ HF Hub; LLM là Gemini free tier qua endpoint OpenAI-compatible. `setup_answers.py --live` sinh 50/50 answers `generation_mode=llm` (không fallback), 4 model generation do xoay vòng khi hết quota 20 request/model/ngày. Giới hạn: 2 PDF scan ảnh (BCTC.pdf, Nghị định 13/2023) không có text layer nên không được index; NeMo full runtime đã chạy live Phase C (guard `gemini-3.5-flash-lite`, 28/28 input, 4/4 output). Các sửa môi trường/tương thích đã làm: `m2_search` fallback `client.search()` cho qdrant-client 1.9; NeMo dùng `ChatOpenAI` cho model không phải gpt-*; `max_tokens: 1024` cho self-check prompts (Gemini thinking ẩn ăn hết 3 token mặc định); giãn cách request 4.5s cho judge/guard (giới hạn 15 RPM).
Nếu cài full NeMo chưa thành công, ghi lỗi thực tế; không dùng unit test pass
hoặc pip resolve để khẳng định runtime đã chạy.

## INDIVIDUAL

Sao chép mẫu cho mỗi thành viên; tiêu đề họ tên không dấu-MSSV.

### TranQuocBaoLong-2A202602696

- Phần được giao và phần thực tế đã làm: Phase B, file `src\phase_b_judge.py`.
- Bằng chứng: Commit SHA 4a4e94a4ba0b656775858096d873adf8f6b88b0c
- Cách kiểm tra: `python -m pytest tests/ -q`: 86 passed, 3 deselected (integration). Chạy `python scripts/run_experiments.py --phase b --live`; artifact có 5 cặp A/B, 10 binary judgments theo đúng `model_answer`, 10/10 nhãn trùng human labels và Cohen’s κ = 1.0.
- Điều đã học: Pairwise A/B/tie và nhãn tốt/xấu 0/1 trả lời hai câu hỏi khác nhau. Hoán đổi thứ tự câu trả lời giúp đo mức bất nhất theo vị trí; Cohen’s κ đo mức đồng thuận giữa judge và nhãn người sau khi hiệu chỉnh đồng thuận ngẫu nhiên.
- Giới hạn/cách xử lý: Chỉ có 5 cặp nên 1/5 (20%) position-inconsistent chưa đủ để kết luận thiên lệch vị trí. Verbosity win rate là 3/4 decisive cases (75%); cần xem nội dung từng cặp và không diễn giải như bằng chứng nhân quả. Calibration κ = 1.0 dựa trên 10 nhãn trong bộ mẫu, không đảm bảo đồng thuận trên dữ liệu rộng hơn.
- Nguồn/AI hỗ trợ nếu có: Codex hỗ trợ triển khai Tasks 5–8 trong `src/phase_b_judge.py` theo hợp đồng trong README/ASSIGNMENT. Phạm vi gồm pairwise judge, swap-and-average, Cohen’s κ và bias report.

### TranNhatMinh-2A202602483

- Phần được giao và phần thực tế đã làm: Phase A, file `src\phase_a_ragas.py`, `src\config.py` và bổ sung các file M1-M5 từ pipeline lab.
- Bằng chứng: Commit SHA fb5a69fc2a47cb156319ce4022a3d5e8d625bf58.
- Cách kiểm tra: `python -m pytest tests/ -q`: 86 passed, 3 deselected (integration). Chạy `python scripts/run_experiments.py --phase a --live` trên 50 câu; trung bình faithfulness 0.855, answer relevancy 0.830, context precision 0.795, context recall 0.805. Kết quả và phân tích bottom 10 được lưu ở `artifacts/ragas_50q.json` và `doc/reports/failure_clusters.md`.
- Điều đã học: Bốn metric RAGAS đo các khía cạnh khác nhau: độ bám context, mức liên quan câu trả lời, độ chính xác context được lấy và độ phủ ground truth. Phân tích answer cùng contexts giúp phân biệt lỗi retrieval thiếu chunk với lỗi generation dù context đã đủ.
- Giới hạn/cách xử lý: Đánh giá chỉ gồm 50 câu, trong đó 10 adversarial; hai PDF scan không có text layer nên không được index. Generation xoay vòng 4 model và evaluator dùng nhiều model do quota, nên điểm giữa các câu có thể chịu ảnh hưởng khác model. Khi so sánh cải tiến, cần cố định model và xử lý/index bản PDF có text trước.
- Nguồn/AI hỗ trợ nếu có: Claude hỗ trợ cho phần này; kết quả được đối chiếu với answers, contexts, ground truth và artifacts của lần chạy live.

### NguyenLePhucThang-2A202602638

- Phần được giao và phần thực tế đã làm: Phase C, file `src\phase_c_guard.py`.
- Bằng chứng: Commit SHA 0fca76146c1cfe7aa2d64d19a55ee73a14e7f095.
- Cách kiểm tra: `python -m pytest tests/ -q`: 86 passed, 3 deselected (integration). Chạy `python scripts/run_experiments.py --phase c --live --latency-samples 20`; `artifacts/guard_results.json` ghi attacks 20/20, clean controls 8/8, output cases 4/4. Đo 20 mẫu sau 2 warm-up; input guard p95 = 1237.501 ms.
- Điều đã học: Guard cần kiểm tra cả input lẫn output, đồng thời dùng clean controls để phát hiện chặn nhầm. Đạt tỷ lệ chặn attacks cao chưa đủ nếu yêu cầu hợp lệ bị chặn; latency cũng là một tiêu chí riêng cần đo sau warm-up.
- Giới hạn/cách xử lý: Input guard p95 1237.501 ms vượt ngân sách 500 ms dù Presidio p95 chỉ 32.023 ms; thời gian chủ yếu nằm ở NeMo input rail (p95 1198.593 ms). Đây là 20 mẫu trong một lần chạy với model guard `gemini-3.5-flash-lite`; cần đo lại sau tối ưu hoặc đổi cấu hình/model và vẫn xác nhận đủ attacks, clean controls, output cases.
- Nguồn/AI hỗ trợ nếu có: Claude hỗ trợ cho phần này; kết quả được tự kiểm tra qua artifact JSON, gồm từng case, kết quả pass/fail và thống kê latency.

## Cập nhật sau khi nộp

Không có
