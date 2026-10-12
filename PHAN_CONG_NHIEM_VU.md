# 📋 KẾ HOẠCH PHÂN CHIA NHIỆM VỤ NHÓM — K4 TRACK 3A (DAY 24)

**Dự án:** Production Eval + Guardrail Stack  
**Tên nhóm:** NhomBotVN  
**Repository:** [https://github.com/haikunn11/K4-Track-3A-Day24-NhomBotVN-Eval-Guard](https://github.com/haikunn11/K4-Track-3A-Day24-NhomBotVN-Eval-Guard)

---

## 👥 Bảng phân công tổng hợp

| STT | Thành viên | Vai trò | Module / Task phụ trách | File code | Artifacts tạo ra | Báo cáo Markdown |
|---|---|---|---|---|---|---|
| 1 | **Phạm Đình Hải** | Trưởng nhóm | Setup Pipeline Day 18 & **Phase A** (RAGAS Evaluation) | `src/phase_a_ragas.py`<br>*(+ chép `m1–m5`)* | `artifacts/answers_50q.json`<br>`artifacts/ragas_50q.json` | `doc/reports/failure_clusters.md`<br>+ `doc/TEAM.md` |
| 2 | **Nguyễn Minh Ngọc** | Thành viên | **Phase B** (LLM-as-a-Judge & Bias Calibration) | `src/phase_b_judge.py` | `artifacts/judge_results.json` | `doc/reports/bias_report.md` |
| 3 | **Nguyễn Văn Đại** | Thành viên | **Phase C** (Guardrails Stack & P95 Latency) | `src/phase_c_guard.py` | `artifacts/guard_results.json` | `doc/reports/blueprint.md` |

---

## 📌 CHI TIẾT CÔNG VIỆC TỪNG THÀNH VIÊN

---

### 1. PHẠM ĐÌNH HẢI (Trưởng nhóm — Setup RAG & Phase A: RAGAS Evaluation)
- **Nhánh làm việc cá nhân:** `hai-phase-a`

#### A. Nhiệm vụ:
1. **Thiết lập nền tảng & sinh câu trả lời RAG:**
   - Chép 5 module từ Day 18 (`m1_chunking.py`, `m2_search.py`, `m3_rerank.py`, `m4_eval.py`, `m5_enrichment.py`) sang thư mục `src/`.
   - Khởi động Qdrant: `docker compose -f infra/docker-compose.yml up -d`.
   - Chạy sinh 50 answers: `python scripts/setup_answers.py --live` tạo `artifacts/answers_50q.json`.
2. **Hiện thực 4 hàm TODO trong `src/phase_a_ragas.py`:**
   - `group_by_distribution(test_set)`: Phân loại 50 câu thành 3 nhóm (20 `factual`, 20 `multi_hop`, 10 `adversarial`).
   - `run_ragas_50q(answers)`: Tích hợp `m4_eval.evaluate_ragas`, trả về đối tượng `RagasEvaluation` với 4 metrics (faithfulness, answer_relevancy, context_precision, context_recall) và `evaluator_models`.
   - `bottom_10(results)`: Lọc 10 câu có điểm trung bình thấp nhất, gán `diagnosis` và `suggested_fix` tương ứng từ `DIAGNOSTIC_TREE`.
   - `cluster_analysis(results)`: Thống kê ma trận lỗi (`worst_metric` × `distribution`), tìm nhóm phân bố yếu nhất theo trung bình điểm.
3. **Kiểm thử & Báo cáo:**
   - Chạy test offline: `python -m pytest tests/test_phase_a.py -q`
   - Chạy thực nghiệm live: `python scripts/run_experiments.py --phase a --live`
   - Điền báo cáo `doc/reports/failure_clusters.md`.
   - Chạy tổng kiểm tra nộp bài: `python scripts/check_lab.py --with-tests`.

---

### 2. NGUYỄN MINH NGỌC (Thành viên — Phase B: LLM-as-a-Judge & Bias Calibration)

#### A. Nhiệm vụ:
1. **Hiện thực 4 hàm TODO trong `src/phase_b_judge.py`:**
   - `pairwise_judge(question, answer_a, answer_b, reference)`: Prompt cho LLM so sánh A vs B theo 3 tiêu chí (Accuracy, Completeness, Conciseness) dựa trên `reference`, trả JSON format `{winner, reasoning, scores}`.
   - `swap_and_average(question, answer_a, answer_b, reference)`: Đánh giá 2 lượt đảo vị trí (A/B và B/A). Chỉ công nhận winner khi cả 2 lượt cùng chọn A (hoặc B), nếu mâu thuẫn thì xử là `"tie"`.
   - `cohen_kappa(judge_labels, human_labels)`: Tính hệ số tương quan Cohen's $\kappa$ giữa 10 nhãn nhị phân LLM và 10 nhãn người từ `human_labels_10q.json`:
     $$\kappa = \frac{p_o - p_e}{1 - p_e}$$
   - `bias_report(judge_results)`: Đo lường tỷ lệ Position Bias (thay đổi kết quả khi đảo vị trí) và Verbosity Bias (ưu tiên câu dài hơn).
2. **Kiểm thử & Báo cáo:**
   - Chạy test offline: `python -m pytest tests/test_phase_b.py -q`
   - Chạy thực nghiệm live: `python scripts/run_experiments.py --phase b --live` *(sau khi có `answers_50q.json`)*
   - Điền báo cáo `doc/reports/bias_report.md`.

---

### 3. NGUYỄN VĂN ĐẠI (Thành viên — Phase C: Guardrails Stack & P95 Latency)

#### A. Nhiệm vụ:
1. **Hiện thực 5 hàm TODO trong `src/phase_c_guard.py`:**
   - `pii_scan(text, analyzer, anonymizer)`: Tích hợp Presidio để nhận diện và che giấu (anonymize) CCCD (12 số), CMND (9 số), SĐT Việt Nam (`0[3-9]\d{8}`) và Email.
   - `check_input_rail(text, rails)`: Gọi NeMo async input rail, đọc cờ `rail.stop` để phát hiện câu hỏi jailbreak / off-topic.
   - `run_adversarial_suite(adversarial_set, ...)`: Chạy full bộ 28 câu (20 attacks + 8 clean). Chạy qua Presidio trước, sau đó qua NeMo input rail. Mục tiêu: $\ge 15/20$ attacks bị chặn và $8/8$ clean allowed.
   - `check_output_rail(question, answer, rails)`: Chạy NeMo output rail kiểm tra câu trả lời sinh ra (chặn rò rỉ dữ liệu mật/PII).
   - `measure_p95_latency(test_inputs, n_runs=20, ...)`: Thực hiện 2 lần warm-up thật (loại khỏi mẫu), thu thập $\ge 20$ mẫu đo tuần tự (Presidio + NeMo Input) bằng `time.perf_counter()`, tính P50, P95, P99 (ngân sách P95 $\le 500$ ms).
2. **Kiểm thử & Báo cáo:**
   - Chạy test offline: `python -m pytest tests/test_phase_c.py -q`
   - Chạy thực nghiệm live: `python scripts/run_experiments.py --phase c --live --latency-samples 20`
   - Điền báo cáo `doc/reports/blueprint.md` (bảng số đo latency thực tế, đề xuất kiến trúc Guardrail, CI Quality Gate và Monitoring).

---

## 🔄 QUY TRÌNH GIT & PHỐI HỢP CỦA NHÓM

> ⚠️ **LƯU Ý QUAN TRỌNG:** Rubric bài lab yêu cầu **tất cả 3 thành viên đều phải có commit** trên GitHub repository. Không để 1 người commit thay toàn bộ.

1. **Phạm Đình Hải (Leader):**
   - Push commit phân công công việc lên nhánh `main`.
   - Setup RAG pipeline, sinh `artifacts/answers_50q.json`.
   - Hoàn thành `phase_a_ragas.py`, commit và push lên nhánh cá nhân `hai-phase-a`.
2. **Nguyễn Minh Ngọc:**
   - Pull `main` về máy.
   - Hoàn thành `phase_b_judge.py`, chạy test PASS, chạy thực nghiệm live, viết `bias_report.md`.
   - Commit và push bằng tài khoản của Ngọc.
3. **Nguyễn Văn Đại:**
   - Pull `main` về máy.
   - Hoàn thành `phase_c_guard.py`, chạy test PASS, chạy thực nghiệm live, viết `blueprint.md`.
   - Commit và push bằng tài khoản của Đại.
4. **Kiểm tra cuối cùng:**
   - Cả 3 cùng xem lại `doc/TEAM.md`, điền đúng MSSV thật của mình.
   - Chạy `python scripts/check_lab.py --with-tests` để đảm bảo hệ thống chấm PASS 100%.
