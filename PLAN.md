# KẾ HOẠCH PHỐI HỢP THỰC HIỆN DỰ ÁN — NHÓM LATENTIA
**K4 Track 3A — Production Eval + Guardrail Stack (Day 24)**

---

## 1. THÀNH VIÊN & PHÂN CÔNG TỔNG QUAN

| STT | Thành viên | Vai trò | Trọng tâm phụ trách | File code & báo cáo | Mục tiêu điểm |
|---|---|---|---|---|---|
| **1** | **Nguyễn Minh Tuấn** (Lead) | `2A202602420` | Trưởng nhóm / Phase A Lead | Tích hợp m1–m5, sinh answers 50q, RAGAS Eval | `src/phase_a_ragas.py`<br>`doc/reports/failure_clusters.md` | 30đ + 4đ bonus |
| **2** | **Nguyễn Minh Thắng** | `2A202602706` | Core Dev / Phase B Lead | Pairwise LLM Judge, Swap-and-average, Cohen's κ, Bias Report | `src/phase_b_judge.py`<br>`doc/reports/bias_report.md` | 35đ + 3đ bonus |
| **3** | **Nguyễn Thị Vàng** | `2A202602897` | Core Dev / Phase C Lead | Presidio PII (VN), NeMo Guardrails In/Out, P95 Latency | `src/phase_c_guard.py`<br>Đóng góp `blueprint.md` | 35đ + 3đ bonus |
| **ALL** | **Cả nhóm** | Tích hợp & Đóng gói | Đề xuất kiến trúc CI/CD, Quality gates, Monitoring | `doc/reports/blueprint.md`<br>`doc/TEAM.md` | Tổng 100đ + 10đ |

---

## 2. QUY TẮC LÀM VIỆC NHÓM & GIT WORKFLOW

Để **3 người làm việc song song 100% không bị xung đột (conflict)**:

1. **Phân chia branch:**
   * `main`: Nhánh ổn định để nộp bài.
   * `feat/phase-a`: Nhánh của **Tuấn** (chỉ sửa `phase_a_ragas.py`, `failure_clusters.md`).
   * `feat/phase-b`: Nhánh của **Thắng** (chỉ sửa `phase_b_judge.py`, `bias_report.md`).
   * `feat/phase-c`: Nhánh của **Vàng** (chỉ sửa `phase_c_guard.py`, `guardrails/`).

2. **Quy tắc commit bắt buộc (để được tính điểm cá nhân):**
   * Mỗi thành viên **bắt buộc phải có commit từ tài khoản GitHub của mình**.
   * Không commit file `.env` hoặc API keys.
   * Khi code xong các hàm, **bắt buộc xóa dòng `# TODO`** (nếu để sót `# TODO` sẽ bị trừ 5 điểm/module).

---

## 3. CHECKLIST CÔNG VIỆC THEO TỪNG THÀNH VIÊN

### 👑 Luồng 1: Nguyễn Minh Tuấn (Lead & Phase A)
* [ ] **Bước 1 (Chuẩn bị - CP0):**
  * Tích hợp 5 modules RAG (`m1_chunking.py`, `m2_search.py`, `m3_rerank.py`, `m4_eval.py`, `m5_enrichment.py`) vào thư mục `src/`.
  * Khởi động Qdrant: `docker compose -f infra/docker-compose.yml up -d`.
  * Chạy sinh answers: `python scripts/setup_answers.py --live` → sinh ra `artifacts/answers_50q.json`.
  * Commit và push `answers_50q.json` lên nhánh chung để Thắng lấy dữ liệu cho Phase B.
* [ ] **Bước 2 (Code Phase A trong `src/phase_a_ragas.py`):**
  * Task 1: `group_by_distribution()` (chia đủ 20 factual, 20 multi_hop, 10 adversarial).
  * Task 2: `run_ragas_50q()` (gọi `m4_eval.evaluate_ragas`, trả về 4 metric: Faithfulness, Answer Relevancy, Context Precision, Context Recall).
  * Task 3: `bottom_10()` (lấy 10 câu có avg_score thấp nhất, gán worst_metric, diagnosis, suggested_fix).
  * Task 4: `cluster_analysis()` (tạo ma trận worst_metric × distribution, tìm distribution yếu nhất theo avg_score trung bình thấp nhất).
* [ ] **Bước 3 (Kiểm thử & Báo cáo):**
  * Chạy unit test mock: `python -m pytest tests/test_phase_a.py -q`.
  * Chạy thực nghiệm live: `python scripts/run_experiments.py --phase a --live` → sinh `artifacts/ragas_50q.json`.
  * Điền báo cáo `doc/reports/failure_clusters.md` từ số liệu JSON.
  * *Mục tiêu Bonus:* Phân tích rõ các bẫy version conflict / negation trong adversarial distribution.

---

### ⚡ Luồng 2: Nguyễn Minh Thắng (Phase B: Judge & Bias)
* [x] **Bước 1 (Code Phase B trong `src/phase_b_judge.py`):**
  * Task 5: `pairwise_judge(question, answer_a, answer_b, reference)`:
    * Gửi prompt JSON cho LLM so sánh A vs B theo 3 tiêu chí: accuracy, completeness, conciseness.
    * Trả về JSON: `{"winner": "A"|"B"|"tie", "reasoning": str, "scores": {"A": float, "B": float}}`.
  * Task 6: `swap_and_average(question, answer_a, answer_b, reference)`:
    * Chạy 2 lượt: Pass 1 (A vs B) và Pass 2 (B vs A).
    * Quy đổi winner lượt 2 về không gian A/B gốc.
    * Xác định `final_winner` (đồng thuận thì giữ, bất nhất thì thành `"tie"`), đo `position_consistent`.
  * Task 7: `cohen_kappa(judge_labels, human_labels)`:
    * Tính hệ số thỏa thuận Cohen's κ giữa 10 nhãn nhị phân (0/1) của LLM judge với nhãn human trong `fixtures/human_labels_10q.json`.
  * Task 8: `bias_report(judge_results)`:
    * Đo position bias rate (`% cases position_consistent == False`).
    * Đo verbosity bias (`% trường hợp câu dài hơn thắng trong các case decisive`).
* [x] **Bước 2 (Kiểm thử & Báo cáo):**
  * Chạy unit test mock: `python -m pytest tests/test_phase_b.py -q`.
  * Sau khi có `answers_50q.json`, chạy live: `python scripts/run_experiments.py --phase b --live` → sinh `artifacts/judge_results.json`.
  * Điền báo cáo `doc/reports/bias_report.md`.
  * *Mục tiêu Bonus:* Đạt Cohen's $\kappa > 0.6$ trên 10 model answers gốc.

---


Kết quả live của Nguyễn Minh Thắng: κ=1.0, 2/5 inconsistent, 3/3 longer winner trong decisive cases; artifact/report đã validate. Các kiểm tra toàn nhóm A/C còn lỗi, xem doc/SUBMISSION_REVIEW.md.

### 🛡️ Luồng 3: Nguyễn Thị Vàng (Phase C: Guardrails & Latency)
* [ ] **Bước 1 (Code Phase C trong `src/phase_c_guard.py`):**
  * Task 9a: `pii_scan(text)`:
    * Dùng Presidio nhận diện & ẩn danh CCCD (12 số), CMND (9 số), SĐT VN (`0[3-9]xxxxxxxx`) và Email.
  * Task 9b: `check_input_rail(text)` (async):
    * Gọi NeMo input rail, kiểm tra `activated_rails`, xác định `allowed` và `blocked_reason`.
  * Task 10: `run_adversarial_suite(adversarial_set)`:
    * Chạy 28 inputs (20 attacks + 8 clean controls).
    * Thứ tự: Presidio trước → NeMo Input sau.
    * Tiêu chí: Chặn $\ge 15/20$ attacks (bonus $\ge 18/20$), cho phép $8/8$ clean controls (false positive = 0).
  * Task 11: `check_output_rail(question, answer)` (async):
    * NeMo output rail kiểm tra câu trả lời, giữ nguyên câu sạch và thay/redact câu vi phạm.
  * Task 12: `measure_p95_latency(test_inputs, n_runs=20)`:
    * Scope: Sequential input layers (`Presidio` + `NeMo input`).
    * Chạy 2 lượt warm-up thật (loại khỏi thống kê), đo $\ge 20$ samples timed bằng `perf_counter`.
    * Tính P50, P95, P99 nội suy tuyến tính.
* [ ] **Bước 2 (Kiểm thử & Báo cáo):**
  * Chạy unit test mock: `python -m pytest tests/test_phase_c.py -q`.
  * Chạy live: `python scripts/run_experiments.py --phase c --live --latency-samples 20` → sinh `artifacts/guard_results.json`.
  * Cung cấp bảng số đo Latency P50/P95/P99 để đưa vào `blueprint.md`.
  * *Mục tiêu Bonus:* Chặn $\ge 18/20$ attacks và $8/8$ clean controls được allowed.

---

## 4. GIAI ĐOẠN TỔNG HỢP & NỘP BÀI (CẢ 3 THÀNH VIÊN)

1. **Merge Code về `main`:**
   * Merge lần lượt các nhánh `feat/phase-a`, `feat/phase-b`, `feat/phase-c` vào `main`.
2. **Hoàn thiện `doc/reports/blueprint.md`:**
   * Tổng hợp kiến trúc hệ thống: `Input → Presidio → NeMo Input → RAG → NeMo Output → Response`.
   * Điền bảng đo latency từ Phase C.
   * Đề xuất các CI Quality Gates và cơ chế Monitoring dữ liệu / drift.
3. **Cập nhật `doc/TEAM.md`:**
   * Cập nhật MSSV thật của từng bạn (thay thế mã tạm `20240001`, `20240002`, `20240003`).
   * Kiểm tra lại phần `INDIVIDUAL` của mỗi người.
4. **Kiểm tra tự động toàn bộ:**
   ```powershell
   python scripts/check_lab.py --with-tests
   ```
   *Yêu cầu:* 100% các tiêu chí báo `PASS`.
5. **Nộp bài:**
   * Trưởng nhóm commit lần cuối và push lên repo: `https://github.com/minhtuann1102/K4-L3-DAY24-Latentia-Eval-Guard`.
   * Nộp link repo lên hệ thống lớp học trước 23:59.
