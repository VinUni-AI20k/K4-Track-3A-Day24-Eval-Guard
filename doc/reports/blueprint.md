# Blueprint CI/CD cho RAG và guardrails

Nhóm: K4-Track-3A-Team

Người phụ trách: Nguyễn Hoàng Nam

Đây là **đề xuất CI/CD**, không phải workflow đã được triển khai/chạy.
Nguồn kết quả: artifacts/ragas_50q.json, judge_results.json, guard_results.json.
Run timestamp: 2026-10-12T11:33:14.981746+00:00; guard models: ["gpt-4o-mini"].
Models generation/evaluator/judge từ A/B: Chưa chạy Phase A và Phase B trong đợt này (ghi nhận từ artifacts tương ứng khi hoàn tất).

## Kiến trúc và failure action

Input → Presidio → NeMo input → RAG → NeMo output → response.
Request thực dừng sớm khi bị chặn; khác phép đo input layers chạy đủ hai tầng.

Kiến trúc dữ liệu luồng xử lý:

1. **Tầng 1 - Presidio PII Detection (Input Guard)**: Quét nhận diện các thực thể PII nhạy cảm định tuyến theo regex và pattern (VN_CCCD, VN_PHONE, EMAIL_ADDRESS, PHONE_NUMBER). Nếu phát hiện chuỗi chứa PII trong query: lập tức dừng xử lý (short-circuit), log lại loại PII và trả về thông báo từ chối cung cấp dữ liệu cá nhân.
2. **Tầng 2 - NeMo Input Rails (Topic & Security Guard)**: Kiểm tra thông điệp đầu vào bằng self-check prompt để phát hiện jailbreak, prompt injection, đóng vai giả mạo, hoặc hỏi ngoài phạm vi chính sách công ty. Nếu vi phạm `rail.stop = True`, hệ thống trả về thông báo từ chối từ `rails.co`.
3. **Tầng 3 - RAG Pipeline**: Chỉ được gọi khi vượt qua an toàn cả 2 tầng input guardrails. Thực hiện hybrid retrieval kết hợp reranking và LLM generation.
4. **Tầng 4 - NeMo Output Rails (Content & Leakage Guard)**: Kiểm duyệt câu trả lời trước khi trả về cho người dùng. Nếu phát hiện rò rỉ PII, mật khẩu hoặc dữ liệu nhân sự nhạy cảm, thực hiện che giấu (redact) hoặc thay thế bằng thông báo từ chối an toàn.

- **Bảo mật và Fallback**: Secrets (API keys) được lưu an toàn trong biến môi trường hoặc Vault, không bao giờ xuất hiện trong log hay mã nguồn. Trong trường hợp LLM guard bị timeout hoặc lỗi mạng, hệ thống áp dụng fallback an toàn (fail-closed cho security guard, chuyển sang câu từ chối chuẩn).

## Phạm vi và số đo latency

Bắt buộc Task 12: **input_layers_sequential**, Presidio + NeMo input, không
short-circuit. Engines tạo trước đo; có hai warm-up thật không tính vào mẫu.
Percentile nội suy tuyến tính từ raw samples; tổng từ tổng từng sample.

Số mẫu timed: 20; warm-up: 2;
phương pháp: linear.

| Layer / scope                      | P50 ms    | P95 ms    | P99 ms    | Tình trạng                  |
| ---------------------------------- | --------- | --------- | --------- | ----------------------------- |
| Presidio                           | 14.37     | 17.52     | 18.16     | Hoàn thành đo Task 12      |
| NeMo input                         | 988.55    | 1737.15   | 1760.30   | Hoàn thành đo Task 12      |
| Input guard sequential             | 1002.60   | 1749.34   | 1774.33   | Hoàn thành đo Task 12      |
| RAG                                | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc    |
| NeMo output                        | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc    |
| Full guard / short-circuit request | chưa đo | chưa đo | chưa đo | Không suy từ input_guard_ms |

Input-layer budget target: 500ms; kết quả thực tế/budget_ok: 1749.34ms (False).
Bottleneck chính nằm ở NeMo input rail khi gọi API LLM từ xa qua mạng (mất khoảng 800-1700ms/lần gọi cho `self_check_input`). Tầng Presidio chạy cục bộ rất nhanh (P95 chỉ 17.52ms). Các phạm vi RAG, NeMo output và full-request hiện được ghi nhận "chưa đo" đúng theo quy định hợp đồng Task 12; kế hoạch đo tiếp theo sẽ mở rộng thêm timer riêng cho từng module sau khi RAG hoàn tất tích hợp.

## CI gates đề xuất

- RAGAS faithfulness ≥0.75, avg_score ≥0.65 trên 50 câu.
- Attacks ≥18/20 cho CI đề xuất; clean 8/8 allowed; output cases đúng.
- Full guard P95 <500ms chỉ áp dụng sau khi thực sự đo full guard.

Mốc bắt buộc lab vẫn attacks ≥15/20; bonus ≥18/20 kèm clean controls đạt.
Đề xuất triển khai GitHub Actions Workflow chạy script `check_lab.py --with-tests` tự động tại mỗi Pull Request. Nếu tỷ lệ attack pass < 15/20 hoặc clean allowed < 8/8, script sẽ trả mã thoát nonzero (`exit 1`) làm fail CI build. Các biến MIN_* là đề xuất chất lượng, quy trình CI này hiện ở mức thiết kế kiến trúc chuẩn bị triển khai.

## Monitoring và cải tiến

Giám sát thời gian thực các chỉ số:

- **Tỷ lệ chặn (Block Rate)**: Cảnh báo khi tỷ lệ block đột biến > 20% trong 1 giờ (dấu hiệu tấn công hoặc false positive).
- **False-positive Tracking**: Định kỳ lấy ngẫu nhiên 5% các truy vấn bị chặn để con người gán nhãn kiểm tra chéo.
- **Latency Monitoring**: Ghi log P95 latency của từng tầng, phát hiện suy thoái hiệu năng mạng gọi LLM.
- **Bảo mật và Quyền riêng tư**: Tất cả log PII trước khi lưu trữ phải được anonymize triệt để.

RAGAS mean/worst distribution: chưa đo (thuộc Phase A).
Cohen’s κ: chưa đo (thuộc Phase B).
Attacks passed: 19/20; clean false_positive_rate: 0.0.

Các hướng cải tiến cụ thể:

1. **Tối ưu hóa Latency NeMo**: Chuyển đổi model `self_check_input` từ gọi cloud API sang một Small Language Model (SLM) cục bộ (như Llama-3.2-1B hoặc Qwen-2.5-0.5B được fine-tune) để hạ P95 latency từ 1749ms xuống dưới 100ms.
2. **Nâng cao khả năng chặn Off-topic**: Tinh chỉnh prompt của NeMo input rail để phân biệt chặt chẽ hơn các câu hỏi làm thơ, tán gẫu ngoài lề (hiện tại câu làm thơ về mùa thu lọt qua tầng guard).
3. **Mở rộng bộ từ điển PII**: Bổ sung thêm nhận diện mã số thuế cá nhân và số tài khoản ngân hàng nội địa Việt Nam.
