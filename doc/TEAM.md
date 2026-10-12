# Nhóm thực hiện K4 Track 3A

Tên nhóm: LGBTree

Repo chung: https://github.com/long27112003/K4-L3-DAY24-LGBTree-Eval-Guard.git

Trưởng nhóm/người nộp: Hoàng Anh Minh - MSSV: 2A202602566

Ngày lab/deadline áp dụng: 12/10/2026 23:59 — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: 8c796e5

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Hoàng Anh Minh | 2A202602566 | Phase B: LLM-as-Judge (pairwise, swap-and-average, Cohen κ, bias analysis) | src/phase_b_judge.py, artifacts/judge_results.json, doc/reports/bias_report.md |

Người tích hợp/chạy batch/nộp link: Hoàng Anh Minh - MSSV: 2A202602566.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: Windows 11 / Python 3.11.2 / MSVC build tools.
Virtualenv/dependencies/imports: Đã cài đặt các gói cần thiết theo requirements-test.lock.txt và requirements.txt.
Models/Qdrant/50 answers đã chuẩn bị: Đã chuẩn bị artifacts/answers_50q.json từ pipeline Day 18 RAG.
Nếu cài full NeMo chưa thành công, ghi lỗi thực tế; không dùng unit test pass
hoặc pip resolve để khẳng định runtime đã chạy.

## INDIVIDUAL

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
  - Nhánh làm việc Git: `HoangAnhMinh-2A202602566`.
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

## Cập nhật sau khi nộp

Không có cập nhật bổ sung sau deadline.
