# Blueprint CI/CD cho RAG và guardrails

Nhóm: ThienBinh

Người phụ trách: {{Họ tên và MSSV}}

Đây là **đề xuất CI/CD**, không phải workflow đã được triển khai/chạy.
Nguồn kết quả: artifacts/ragas_50q.json, judge_results.json, guard_results.json.
Run timestamp: 2026-10-12T14:52:11.518701+00:00 (guard_results.json); guard models: `gemini-3.5-flash-lite`.
Models generation/evaluator/judge từ A/B: generation = `gemini-3.5-flash-lite`, `gemini-3.6-flash`,
`gemini-3.7-flash`, `gemini-3.8-flash` (ragas_50q.json và judge_results.json); evaluator =
`gemini-3.1-flash-lite`, `gemini-3.5-flash`, `gemini-3.5-flash-lite`, `gemini-3.6-flash`,
`gemini-3.7-flash`, `gemini-flash-latest`, `gemini-flash-lite-latest`, `gemini-embedding-001`
(ragas_50q.json, m4); judge = `gemini-3.5-flash-lite` (judge_results.json).

## Kiến trúc và failure action

Input → Presidio → NeMo input → RAG → NeMo output → response.
Request thực dừng sớm khi bị chặn; khác phép đo input layers chạy đủ hai tầng.

Data flow và failure action:

1. **Presidio (local, khoảng 20ms):** quét PII dạng pattern: VN_CCCD (9/12 số), VN_PHONE, EMAIL,
   PHONE_NUMBER, thẻ/tài khoản… Nhóm loại các nhãn NER `PERSON/LOCATION/NRP/DATE_TIME/URL` và chỉ
   giữ kết quả có score ≥ 0.5, vì model spaCy tiếng Anh gắn nhầm `PERSON` cho cụm từ tiếng Việt
   ("bao nhiêu", "Xin lỗi"), làm 7/8 câu sạch bị chặn ở lần chạy đầu. Có PII thì chặn ngay, trả
   câu từ chối chuẩn, không gọi LLM.
2. **NeMo input rail (`self check input`):** chặn jailbreak, prompt injection, off-topic, và yêu cầu
   PII không kèm số cụ thể (ví dụ hỏi CCCD của một nhân viên có tên). Khi bị chặn thì trả câu từ
   chối của `rails.co`.
3. **RAG:** hybrid search (BM25 + BGE-M3/Qdrant) → rerank top-3 → generation chỉ dựa trên context.
4. **NeMo output rail (`self check output`):** chặn answer chứa CCCD/SĐT/email cá nhân, lương cá
   nhân, credential. Khi bị chặn thì thay bằng câu từ chối; answer gốc không được trả cho user.

Log/redact: chỉ log input đã qua `pii_scan().anonymized` (PII thay bằng `<VN_CCCD>`…), kèm lớp chặn
(`blocked_by`), id request, model và latency. Không log answer bị output rail chặn ở dạng thô.

Secrets: API key nằm trong `.env` local (đã có trong `.gitignore`); `.env.example` không chứa giá
trị. Trên CI dùng secret của repo (ví dụ `OPENAI_API_KEY`, `OPENAI_BASE_URL`), không in ra log.

Fallback:
- Nếu LLM của NeMo lỗi hoặc timeout: **fail-closed**, tức là chặn và trả "hệ thống bận" thay vì cho
  request đi tiếp mà không qua guard.
- Generation xoay vòng model khi hết quota ngày (`src/llm.py`). Khi không còn model nào, request
  báo lỗi rõ ràng, không âm thầm trả extractive answer.

## Phạm vi và số đo latency

Bắt buộc Task 12: **input_layers_sequential**, Presidio + NeMo input, không
short-circuit. Engines tạo trước đo; có hai warm-up thật không tính vào mẫu.
Percentile nội suy tuyến tính từ raw samples; tổng từ tổng từng sample.

Số mẫu timed: 20; warm-up: 2;
phương pháp: linear.

| Layer / scope | P50 ms | P95 ms | P99 ms | Tình trạng |
|---|---|---|---|---|
| Presidio | 18.5 | 32.0 | 90.8 | Đạt; local, không gọi mạng |
| NeMo input | 866.4 | 1198.6 | 1386.9 | Vượt budget; 1 lượt gọi Gemini `gemini-3.5-flash-lite` mỗi request |
| Input guard sequential | 888.3 | 1237.5 | 1414.8 | Vượt budget 500ms (latency_budget_ok = false) |
| RAG | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| NeMo output | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| Full guard / short-circuit request | chưa đo | chưa đo | chưa đo | Không suy từ input_guard_ms |

Input-layer budget target: 500ms; kết quả thực tế/budget_ok: P95 = 1237.5ms, `latency_budget_ok = false`.

Bottleneck là NeMo input: khoảng 97% thời gian của input guard (866/888ms ở P50) là round-trip tới
Gemini qua internet; Presidio chỉ khoảng 2%. Lưu ý về cách đo: free tier giới hạn 15 request/phút
cho model này, nên runner giãn mỗi lượt gọi cách nhau ≥ 4.5s. Khoảng chờ này nằm **ngoài** vùng
`perf_counter`, nên số trên không bao gồm thời gian chờ rate limit. Ở lần chạy trước khi thêm giãn
cách, các mẫu bị 429 làm P95 lên khoảng 16s.

Hướng giảm latency, cần đo lại sau mỗi thay đổi:
- dùng model guard nhỏ chạy local hoặc cùng region;
- cache kết quả self-check cho input lặp lại;
- chạy Presidio và NeMo input song song khi không cần short-circuit;
- dùng endpoint trả phí không có throttle.

Kế hoạch đo các phần "chưa đo": cùng phương pháp (engines tạo trước, 2 warm-up, ≥ 20 mẫu
`perf_counter`, percentile linear), ghi timestamp từng tầng trong một request thật:
`t_presidio`, `t_nemo_in`, `t_retrieve`, `t_rerank`, `t_generate`, `t_nemo_out`. Full guard P95 lấy
từ tổng theo từng request, không cộng các P95 riêng lẻ. Request bị chặn sớm (short-circuit) đo
riêng.

## CI gates đề xuất

- RAGAS faithfulness ≥0.75, avg_score ≥0.65 trên 50 câu.
- Attacks ≥18/20 cho CI đề xuất; clean 8/8 allowed; output cases đúng.
- Full guard P95 <500ms chỉ áp dụng sau khi thực sự đo full guard.

Mốc bắt buộc lab vẫn attacks ≥15/20; bonus ≥18/20 kèm clean controls đạt.

Đối chiếu với lần chạy hiện tại: faithfulness 0.855 (đạt ≥ 0.75); avg_score trung bình 50 câu
0.821 (đạt ≥ 0.65); attacks 20/20 (đạt ≥ 18/20); clean 8/8 allowed; output 4/4 đúng.

Job đề xuất (chưa triển khai; repo hiện chưa có workflow CI):

```yaml
# .github/workflows/eval-guard.yml  (ĐỀ XUẤT)
jobs:
  unit:            # mỗi PR, không gọi API
    steps:
      - run: python -m pytest tests/ -q
  submission-check: # mỗi PR, chỉ đọc artifacts, không gọi API
    steps:
      - run: python scripts/check_lab.py
  live-eval:       # chạy tay hoặc nightly, có chi phí API, dùng repo secrets
    steps:
      - run: python scripts/run_experiments.py --phase a --live
      - run: python scripts/run_experiments.py --phase b --live
      - run: python scripts/run_experiments.py --phase c --live --latency-samples 20
      - run: python scripts/quality_gate.py   # script đề xuất, chưa có trong repo
```

`pytest` và `check_lab.py` đã trả mã khác 0 khi fail. `quality_gate.py` là script đề xuất: đọc 3
JSON trong `artifacts/`, so với các biến `MIN_FAITHFULNESS=0.75`, `MIN_AVG_SCORE=0.65`,
`MIN_ATTACKS_PASSED=18`, `MAX_CLEAN_FPR=0`, rồi `sys.exit(1)` nếu bất kỳ ngưỡng nào không đạt. Các
biến `MIN_*` chỉ là đề xuất; runner hiện tại **không** tự kiểm tra các ngưỡng này (Phase C lưu kết
quả với `require_quality=False`), nên chưa phải là quality gate thật.

## Monitoring và cải tiến

Metric theo dõi khi chạy thật (lấy mẫu log đã redact):

| Metric | Cách lấy | Ngưỡng cảnh báo đề xuất | Người xử lý |
|---|---|---|---|
| Tỉ lệ chặn của input guard | đếm `blocked_by` theo ngày | tăng/giảm > 2× so với tuần trước | owner guardrails |
| False positive | user báo "bị chặn nhầm" và review mẫu 20 request bị chặn/tuần | > 5% mẫu review là chặn nhầm | owner guardrails |
| Tỉ lệ answer "Không tìm thấy" | đếm trên log generation | > 15% request | owner RAG |
| RAGAS faithfulness (mẫu) | chấm hằng tuần 50 câu cố định cộng 20 câu mới lấy từ log | < 0.75 | owner RAG |
| Input guard P95 | `perf_counter` từng tầng | > 1500ms (hiện tại 1237ms) | owner hạ tầng |
| Lỗi/timeout LLM, hết quota | đếm exception theo model | > 1% request hoặc model bị loại khỏi vòng xoay | owner hạ tầng |

Drift: khi tài liệu chính sách có phiên bản mới (như v2023 → v2024), chạy lại bộ 50 câu và thêm câu
version-conflict cho tài liệu đó. Privacy: không lưu input thô chứa PII; mẫu review chỉ dùng bản đã
anonymize.

Giới hạn của bộ đánh giá: 50 câu RAG, 20 attack, 8 câu sạch, 4 output case là bộ nhỏ, được viết tay.
Kết quả 20/20 và 8/8 chỉ cho thấy guard xử lý tốt đúng các mẫu này, chưa đo được các biến thể
attack mới hay câu hỏi sạch có chứa từ nhạy cảm.

RAGAS mean/worst distribution: mean avg_score 0.821 (faithfulness 0.855); worst distribution adversarial = 0.700.
Cohen’s κ: 1.0 (10/10 nhãn khớp human).
Attacks passed: 20/20; clean false_positive_rate: 0.0.

Cải tiến có thể kiểm tra:

1. Sửa prompt generation để phân biệt "không có thông tin" với "thông tin là phủ định". Kỳ vọng các
   câu 46/47/48/50 không còn "Không tìm thấy" và faithfulness adversarial tăng từ 0.675 lên > 0.85.
2. Tăng `RERANK_TOP_K` từ 3 lên 5 hoặc tách sub-query cho câu multi-hop. Kỳ vọng context_recall
   multi_hop tăng từ 0.729, kiểm tra cùng 50 câu và cùng evaluator.
3. Thêm metadata filter ưu tiên tài liệu đang hiệu lực. Kiểm tra trên câu 41/49 và cặp mật khẩu
   v1.0/v2.0.
4. Thay NeMo input bằng guard model local hoặc cache self-check. Đo lại input guard P95 (hiện tại
   1237ms) với 20 mẫu và 2 warm-up.
5. Mở rộng bộ attack và clean (ví dụ thêm câu sạch có tên người hoặc số thứ tự) để đo false positive
   của Presidio sau khi đã lọc nhãn NER.
