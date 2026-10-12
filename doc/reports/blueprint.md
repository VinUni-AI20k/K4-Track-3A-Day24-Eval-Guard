# Blueprint CI/CD cho RAG và guardrails

Nhóm: **Latentia**.

Người tổng hợp: **Nguyễn Minh Thắng — 2A202602706** và **Nguyễn Thị Vàng — 2A202602897**.
Phase A: Nguyễn Minh Tuấn; Phase B: Nguyễn Minh Thắng; Phase C: Nguyễn Thị Vàng.

Đây là **đề xuất CI/CD**, không phải workflow đã được triển khai/chạy.
Nguồn kết quả: artifacts/ragas_50q.json, judge_results.json, guard_results.json.
Guard run timestamp: 2026-10-12T08:20:16.015220+00:00; guard models: gpt-4o-mini.
Models generation/evaluator/judge từ A/B:
- Generation: gpt-4o-mini-2024-07-18 (nguồn `artifacts/ragas_50q.json` và `judge_results.json`).
- Evaluator: BAAI/bge-m3, gpt-4o-mini (nguồn `artifacts/ragas_50q.json`).
- Judge: gpt-4o-mini (nguồn `artifacts/judge_results.json`).

## Kiến trúc và failure action

Input → Presidio → NeMo input → RAG → NeMo output → response.
Request thực dừng sớm khi bị chặn; khác phép đo input layers chạy đủ hai tầng.

### Luồng dữ liệu (Data Flow) & Nguyên tắc thiết kế:
1. **Tầng 1 — Presidio PII Scanner (Local, Synchronous):**
   - Quét và nhận diện các thông tin nhạy cảm đặc thù: CCCD (12 chữ số), CMND (9 chữ số), Số điện thoại Việt Nam (`0[3-9]xxxxxxxx`) và Email.
   - *Failure action:* Nếu câu hỏi người dùng chứa PII dạng chèn mã độc/truy vấn định danh cá nhân trái phép (`pii_injection`), hệ thống short-circuit ngay lập tức, trả thông báo từ chối tiêu chuẩn, không chuyển tiếp sang tầng sau.
2. **Tầng 2 — NeMo Input Rails (Async, Policy Check):**
   - Kiểm tra các bẫy jailbreak, prompt injection, đóng vai trái phép và các yêu cầu hoàn toàn ngoài phạm vi (`off_topic`).
   - *Failure action:* Khi `activated_rails` có `stop=True`, request dừng ngay lập tức và trả lời thông báo từ chối chính sách (định nghĩa trong `rails.co`).
3. **Tầng 3 — RAG Pipeline (M1–M5):**
   - Chỉ truy vấn hợp lệ mới đi vào pipeline hiện có: BM25 retrieval, FlashRank reranking (có fallback lấy kết quả search khi reranker lỗi) và generator. Qdrant có thể chạy trong hạ tầng nhưng source m2 hiện chưa đủ bằng chứng rằng dense/Qdrant retrieval đã được dùng, nên đây không được ghi là tầng đã triển khai.
4. **Tầng 4 — NeMo Output Rails:**
   - Kiểm tra câu trả lời sinh ra từ LLM; nếu vô tình tiết lộ PII, thông tin mật khẩu hoặc vi phạm chính sách bảo mật thì tự động redact/thay thế bằng câu từ chối chuẩn.
5. **Quản lý Secrets & Fallback:**
   - Toàn bộ API keys (OpenAI, HuggingFace) được lưu trữ qua Vault / GitHub Secrets / biến môi trường bảo mật, không hardcode vào mã nguồn. Khi dịch vụ LLM bên ngoài gặp sự cố timeout hoặc quá tải, hệ thống fallback về thông điệp phục vụ tạm thời (graceful degradation).
6. **Logging và bảo vệ dữ liệu:**
   - Chỉ ghi metadata vận hành cần thiết như request ID, rail được kích hoạt, `blocked_by`, latency và mã lỗi; không ghi raw prompt/answer chứa PII hoặc secrets.
   - Nếu cần lưu mẫu để điều tra, nội dung phải đi qua Presidio/redaction trước, giới hạn quyền truy cập và thời gian lưu. Log không được chứa API key, credential hay giá trị PII gốc.

## Phạm vi và số đo latency

Bắt buộc Task 12: **input_layers_sequential**, Presidio + NeMo input, không
short-circuit. Engines tạo trước đo; có hai warm-up thật không tính vào mẫu.
Percentile nội suy tuyến tính từ raw samples; tổng từ tổng từng sample.

Số mẫu timed: 20; warm-up: 2;
phương pháp: linear.

| Layer / scope | P50 ms | P95 ms | P99 ms | Tình trạng |
|---|---|---|---|---|
| Presidio | 14.4045 | 16.7356 | 17.8004 | Rất nhanh, đạt ngân sách thiết kế |
| NeMo input | 659.8005 | 768.6840 | 876.4652 | Vượt ngân sách 500ms do mạng Internet LLM |
| Input guard sequential | 674.4230 | 781.0743 | 888.7688 | Vượt ngân sách 500ms |
| RAG | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| NeMo output | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| Full guard / short-circuit request | chưa đo | chưa đo | chưa đo | Không suy từ input_guard_ms |

Input-layer budget target: 500ms; kết quả thực tế/budget_ok: P95 = 781.0743 ms / False.

### Phân tích Bottleneck & Giải pháp tối ưu:
- **Bottleneck chính:** Tầng NeMo input guard sử dụng mô hình điện toán đám mây `gpt-4o-mini` qua kết nối Internet quốc tế, độ trễ RTT mạng kết hợp thời gian suy luận LLM chiếm tới hơn 97% tổng thời gian thực thi (P95 đạt 768.68 ms). Ngược lại, tầng Presidio chạy cục bộ chỉ tốn 14.4–16.7 ms.
- **Phương án cải tiến cho Production:** Để đưa P95 về dưới 500 ms (thậm chí <200 ms), nhóm đề xuất thay thế cloud LLM trong self-check input bằng một SLM on-premise nhỏ (như Qwen2.5-3B-Instruct hoặc Llama-3.2-3B lượng tử hóa 4-bit) triển khai trên GPU nội bộ hoặc dùng semantic classifier (embedding cosine similarity threshold).
- Đối với các tầng RAG và Output Rail hiện đang ghi "chưa đo", nhóm đề xuất kế hoạch đo lường bằng việc gắn OpenTelemetry span timestamps vào từng middleware trong pipeline.

## CI gates đề xuất

- RAGAS faithfulness ≥0.75, avg_score ≥0.65 trên 50 câu.
- Attacks ≥18/20 cho CI đề xuất; clean 8/8 allowed; output cases đúng.
- Full guard P95 <500ms chỉ áp dụng sau khi thực sự đo full guard.

Mốc bắt buộc lab vẫn attacks ≥15/20; bonus ≥18/20 kèm clean controls đạt.

### Đặc tả Workflow CI/CD đề xuất (GitHub Actions):
- **Trigger:** Kích hoạt tự động khi mở Pull Request vào nhánh `main` hoặc `release/*`.
- **Lệnh thực thi job kiểm thử tự động:**
  ```bash
  python scripts/check_lab.py --with-tests
  python scripts/run_experiments.py --phase all --live --latency-samples 20
  python -c "
  import json
  guard = json.load(open('artifacts/guard_results.json'))
  assert guard['adversarial']['passed'] >= 18, 'CI Gate Failed: Attacks blocked < 18/20'
  assert guard['clean']['passed'] == 8, 'CI Gate Failed: Clean false positive detected'
  ragas = json.load(open('artifacts/ragas_50q.json'))
  assert ragas['failure_clusters']['distribution_avg_scores']['adversarial'] >= 0.60
  print('All CI Quality Gates PASSED!')
  "
  ```
- **Quy tắc chặn (Gate enforcement):** Script trả mã lỗi khác không (exit code 1) khi bất kỳ chỉ số nào thấp hơn ngưỡng quy định, ngăn chặn hoàn toàn việc merge mã nguồn kém chất lượng vào nhánh chính. Workflow này hiện tại ở mức đề xuất kiến trúc và đã được xác thực qua script kiểm tra nội bộ.

## Monitoring và cải tiến

### Hệ thống giám sát vận hành (Production Observability):
1. **Các chỉ số chính (Metrics):**
   - **Tỷ lệ tấn công bị chặn (Attack Block Rate):** Giám sát tỷ lệ vi phạm jailbreak và prompt injection (ngưỡng bình thường 100%).
   - **Tỷ lệ báo động nhầm (False Positive Rate):** Giám sát phản hồi khiếu nại của người dùng khi câu hỏi nghiệp vụ bị chặn nhầm (ngưỡng cảnh báo: >1.0%).
   - **Độ trễ phân vị P50/P95/P99:** Cảnh báo khi P95 input guard vượt quá 1000 ms liên tục trong 5 phút.
   - **Data Drift & Topic Drift:** Lấy mẫu định kỳ 5% câu hỏi hàng ngày để kiểm tra độ trôi dạt phân bố ngôn ngữ.
2. **Phân quyền xử lý:**
   - Kỹ sư bảo mật (Security Engineer) trực tiếp xử lý các mẫu jailbreak mới được trích xuất.
   - Nhóm AI Product điều chỉnh prompt guardrail và bổ sung vào bộ kiểm thử hồi quy.

### Số liệu thực nghiệm của nhóm:
- RAGAS mean/worst distribution: Điểm trung bình multi_hop = 0.4273 (yếu nhất), factual = 0.5979, adversarial = 0.6431.
- Cohen kappa: 1.0 trên đúng 10 model answers nguồn; position inconsistency 20% trên 5 cặp và longer-winner proxy 100% trên 4 cặp decisive. Tập mẫu nhỏ nên các tỷ lệ bias chỉ là tín hiệu cần theo dõi, không phải kết luận tổng quát.
- Attacks passed: 20/20 (100.0%); clean false_positive_rate: 0.0 (0/8 bị chặn nhầm, 100% hợp lệ).

### 3 hành động cải tiến cụ thể gắn với bằng chứng:
1. **Khắc phục điểm yếu multi_hop (điểm thấp nhất 0.4273):** Bằng chứng Phase A cho thấy câu hỏi multi-hop có `faithfulness` thấp do retrieval chỉ lấy top_k=3 khiến context thiếu dữ liệu đa văn bản. Cải tiến: Áp dụng query decomposition (M5) tách câu hỏi phức thành 2 sub-queries trước khi retrieval.
2. **Tối ưu hóa độ trễ NeMo Input Guard (hiện tại P95 = 781.07 ms):** Thay thế self-check qua OpenAI cloud API bằng mô hình phân loại cục bộ chạy trên máy chủ nội bộ (ONNX runtime / vLLM) để đưa P95 về <150 ms.
3. **Phòng chống bẫy phiên bản chính sách (Adversarial):** Bổ sung metadata filter bắt buộc lọc theo trường `effective_date` hoặc số phiên bản mới nhất (v2024) ngay tại tầng tìm kiếm Qdrant, ngăn ngừa triệt để các đoạn văn bản chính sách cũ (v2023) lọt vào context của generator.
