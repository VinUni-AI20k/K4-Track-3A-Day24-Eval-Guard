# Blueprint CI/CD cho RAG và guardrails

Nhóm: {{Tên nhóm}}

Người phụ trách: {{Họ tên và MSSV}}

Đây là **đề xuất CI/CD**, không phải workflow đã được triển khai/chạy.
Nguồn kết quả: artifacts/ragas_50q.json, judge_results.json, guard_results.json.
Run timestamp: {{created_at}}; guard models: {{metadata.models.guard}}.
Models generation/evaluator/judge từ A/B: {{models theo từng vai trò và nguồn report}}.

## Kiến trúc và failure action

Input → Presidio → NeMo input → RAG → NeMo output → response.
Request thực dừng sớm khi bị chặn; khác phép đo input layers chạy đủ hai tầng.

{{Mô tả data flow, failure action, log/redact, nơi giữ secrets và điều kiện fallback.}}

## Phạm vi và số đo latency

Bắt buộc Task 12: **input_layers_sequential**, Presidio + NeMo input, không
short-circuit. Engines tạo trước đo; có hai warm-up thật không tính vào mẫu.
Percentile nội suy tuyến tính từ raw samples; tổng từ tổng từng sample.

Số mẫu timed: 20; warm-up: 2;
phương pháp: linear.

| Layer / scope | P50 ms | P95 ms | P99 ms | Tình trạng |
|---|---|---|---|---|
| Presidio | 17.3 | 20.8 | 22.9 | đã đo, Task 12 |
| NeMo input | 747.0 | 1605.5 | 1637.9 | đã đo, Task 12 |
| Input guard sequential | 763.6 | 1621.1 | 1653.8 | đã đo, Task 12 |
| RAG | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| NeMo output | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| Full guard / short-circuit request | chưa đo | chưa đo | chưa đo | Không suy từ input_guard_ms |

Input-layer budget target: 500ms; kết quả thực tế/budget_ok: P95 1621.1 ms, latency_budget_ok: False.

Kết quả đo đạc thực tế cho thấy tầng NeMo input là nút thắt cổ chai chính với P95 đạt 1605.5 ms, chiếm hơn 99% tổng thời gian hai tầng đầu vào, trong khi Presidio chạy cục bộ rất nhanh chỉ mất 20.8 ms (P95). Mức P95 thực tế của chuỗi input guard đạt 1621.1 ms, vượt ngưỡng ngân sách 500 ms. Lý do cấu trúc là do NeMo Guardrails phải thực hiện một lượt gọi mạng từ xa tới OpenRouter (mô hình `openai/gpt-4o-mini`) cho mỗi kiểm tra đầu vào, phụ thuộc hoàn toàn vào độ trễ mạng và thời gian phản hồi của nhà cung cấp LLM, trong khi Presidio chỉ chạy suy luận Regex và NLP cục bộ trên CPU. Kết quả `input_guard_ms` không được dùng để suy đoán độ trễ của toàn bộ pipeline full guard vì hệ thống còn bao gồm tầng truy xuất RAG (Qdrant và reranker) và tầng NeMo output rail, cả hai đều chưa được đo lường trong Task 12. Kế hoạch đo lường bổ sung cho các thành phần còn thiếu bao gồm: thu thập tối thiểu 20 mẫu cho từng tầng RAG, NeMo output và full request hoàn chỉnh với cơ chế short-circuit khi phát hiện vi phạm sớm; thực hiện tối thiểu 2 lượt warm-up độc lập trước mỗi đợt đo; ghi nhận thời gian bằng `time.perf_counter()` tại các mốc bắt đầu và kết thúc của từng tầng. Giới hạn của phép đo hiện tại là kích thước mẫu còn nhỏ (20 mẫu), thu thập trong một lượt chạy duy nhất trên một máy đơn lẻ qua mạng gia đình; đồng thời quy trình đo của Task 12 bắt buộc chạy tuần tự cả hai tầng Presidio và NeMo mà không áp dụng ngắt sớm, khác với hành vi triển khai thực tế vốn sẽ dừng xử lý ngay khi Presidio phát hiện PII.

## CI gates đề xuất

- RAGAS faithfulness ≥0.75, avg_score ≥0.65 trên 50 câu.
- Attacks ≥18/20 cho CI đề xuất; clean 8/8 allowed; output cases đúng.
- Full guard P95 <500ms chỉ áp dụng sau khi thực sự đo full guard.

Mốc bắt buộc lab vẫn attacks ≥15/20; bonus ≥18/20 kèm clean controls đạt.
{{Đề xuất lệnh job và cách script trả nonzero khi không đạt. MIN_* là biến đề
xuất, không tự làm quality gate nếu runner chưa kiểm tra ngưỡng. Ghi rõ workflow
chưa triển khai, hoặc dẫn bằng chứng nếu nhóm thực sự đã triển khai.}}

## Monitoring và cải tiến

{{Nêu metric, ngưỡng cảnh báo, cách lấy samples, xử lý false positives, drift,
privacy và người xử lý. Dùng kết quả thật và ghi giới hạn của bộ 50/20/8/4.}}

RAGAS mean/worst distribution: {{giá trị}}.
Cohen’s κ: {{giá trị}}.
Attacks passed: {{số lượng}}/20; clean false_positive_rate: {{giá trị}}.
{{Nêu 3–5 câu cải tiến có thể kiểm tra, gắn với bằng chứng của nhóm.}}
