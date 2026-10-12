# Blueprint CI/CD cho RAG và guardrails

Nhóm: LGBTree

Người phụ trách: Hà Anh Tuấn (2A202602376).

Đây là **đề xuất CI/CD**, chưa phải workflow đã triển khai. Bằng chứng là các JSON trong `artifacts/`, với metadata phiên bản 2, timestamp và SHA-256 nguồn; không coi unit tests là bằng chứng chạy API.

| Phase | Artifact | Run timestamp UTC | Model thực tế |
|---|---|---|---|
| A | ragas_50q.json | 2026-10-12T09:52:39.902165+00:00 | Evaluator: gpt-4o-mini, text-embedding-3-small |
| B | judge_results.json | 2026-10-12T09:48:07.947355+00:00 | Judge: gemini-3.5-flash |
| C | guard_results.json | 2026-10-12T11:36:44.232309+00:00 | Guard: gpt-4o-mini |

Phase C hoàn tất lúc 18:36:44 ngày 12/10/2026 (UTC+07:00). `answers_50q.json` có 50 answers dùng `extractive_fallback`, generation model null; không khai đó là câu trả lời được LLM sinh. A/B là kết quả do thành viên phụ trách cung cấp, được giữ nguyên trong lần tích hợp này.

## Kiến trúc và failure action

Input → Presidio → NeMo input → RAG m1–m5 → NeMo output → response.

Implementation Tasks 9a–12 giữ luồng TODO, imports và helpers. Task 9a bổ sung bộ lọc VN_CCCD, VN_PHONE, EMAIL_ADDRESS và PHONE_NUMBER vì NER tiếng Anh gán nhầm cụm tiếng Việt thành PERSON. Nếu có định danh thuộc phạm vi này, request dừng tại Presidio; bản anonymized phục vụ xử lý/log có kiểm soát. NeMo kiểm tra các input chưa bị chặn và output, gồm yêu cầu tiết lộ tên/hồ sơ/lương cá nhân. Prompt input làm rõ thứ tự chặn override/PII/credentials, cho phép HR/IT/quy định mật khẩu chung và chặn mọi yêu cầu ngoài phạm vi dù vô hại. Không thêm ngoại lệ theo fixtures hay id; đây chưa phải bộ nhận diện toàn bộ PII tiếng Việt.

Input/output quyết định theo `activated_rails.stop`, không dò từ “xin lỗi” trong câu trả lời. Output sạch giữ nguyên; output bị chặn thay bằng câu từ chối. Public helpdesk `helpdesk@cty.vn` được phép trong output theo policy. Self-check output không xác nhận factual accuracy hay thay thế RAGAS faithfulness.

Các hàm hiện tại truyền lỗi API/runtime lên, không chuyển lỗi thành allowed/safe. Khi triển khai dịch vụ, đề xuất bắt lỗi tại biên request, trả thông báo tạm không xử lý được, không trả answer chưa kiểm tra. Không giảm guard thành allow-all khi timeout. Key giữ trong `.env`/secret store, không log raw PII, credentials hay key; log model, policy version, layer quyết định, request ID và latency đã loại dữ liệu nhạy cảm. Failure handler/log ở dịch vụ production chưa triển khai trong lab.

## Phạm vi và số đo latency

Phase C với bộ lọc PII và prompt input hiện tại: **17/20 attacks (85%)**, **8/8 clean allowed**, false-positive rate **0%**; **4/4 output cases đúng**. Đạt yêu cầu lab ≥15/20 kèm 8/8 clean allowed và output cases đúng; chưa đạt bonus ≥18/20. Attacks id 12 (nấu ăn), 14 (toán) và 15 (phim) còn allowed qua NeMo. Không sửa fixtures hoặc ngoại lệ theo id để che các lỗi này; cần kiểm chứng phạm vi chủ đề trên holdout trước production.

Task 12 có scope `input_layers_sequential`: engines tạo trước đo, hai warm-up thật mỗi tầng trong cùng event loop bị loại, sau đó **20 timed samples** luân phiên clean inputs. Luôn đo cả Presidio và NeMo, kể cả khi PII chặn; request thật dừng sớm không nằm trong phép đo này. Dùng `perf_counter`, raw milliseconds và percentile tuyến tính tại `(n-1)*q`; tổng tính từng sample trước khi tính percentile.

| Layer / scope | P50 ms | P95 ms | P99 ms | Tình trạng |
|---|---:|---:|---:|---|
| Presidio | 17.455450 | 50.661685 | 53.082817 | Đã đo |
| NeMo input | 674.660800 | 817.407230 | 1010.280486 | Đã đo, điểm nghẽn |
| Input guard sequential | 692.536950 | 833.754435 | 1030.173927 | Đã đo, vượt target |
| RAG | chưa đo | chưa đo | chưa đo | Ngoài phạm vi Task 12 |
| NeMo output | chưa đo | chưa đo | chưa đo | Ngoài phạm vi Task 12 |
| Full guard / request dừng sớm | chưa đo | chưa đo | chưa đo | Không suy từ input_guard_ms |

Budget target: 500ms; `latency_budget_ok=false`. P95 tổng cao hơn target 333.754435ms. NeMo input gồm round-trip API và xử lý model; chưa có instrumentation tách hai phần. Không cộng P95 từng layer để suy P95 tổng. Theo rubric, vượt target vẫn phải ghi đúng và phân tích, không tự sửa số liệu.

## CI gates đề xuất

Job offline chạy `python -m pytest tests/ -m "not integration" -q`; job kiểm tra bằng chứng chạy `python scripts/check_lab.py`. Hai lệnh trả nonzero khi tests/contract không đạt. Job live có secret riêng, chạy từng phase một lần; `--live` có chi phí nên không chạy lại đồng thời với integration tests API.

Checker hiện kiểm tra ≥15/20 attacks, 8/8 clean allowed, 4 output decisions, schemas/provenance và phép tính latency. Runner giữ cả kết quả không đạt để phân tích; runner không tự thực thi CI gate bonus hay budget. Đề xuất thêm bước quality gate đọc JSON và trả nonzero nếu faithfulness <0.75, avg_score <0.65, attacks <18/20, clean không đủ 8/8 hoặc output sai. Đây là bước chưa triển khai; đặt biến MIN_* đơn thuần không tạo gate.

Ngưỡng full-guard P95 <500ms chỉ áp dụng sau khi đo full request thật. Với kết quả hiện tại, gate input-layer 500ms không đạt; cần tối ưu và đo lại trước khi dùng gate đó làm điều kiện release. Không nới gate hoặc đổi scope để che việc vượt mục tiêu.

## Monitoring và cải tiến

RAGAS weighted means trên 50 câu: faithfulness 0.9910, answer relevancy 0.3765, context precision 0.9517, context recall 0.7883, avg_score 0.7769. Distribution avg_score: factual 0.7817, multi_hop 0.7797, adversarial 0.7614; adversarial yếu nhất. Worst metric của 48/50 câu là answer relevancy. Judge κ=1.0 trên 10 nhãn, position bias 0/5 và verbosity win rate 0.4 trên 5 cặp; mẫu nhỏ không chứng minh judge đáng tin trong mọi tình huống.

- Bổ sung holdout tiếng Việt cho tên người, câu HR/IT hợp lệ và câu ngoài phạm vi; đo false positives/negatives trước khi đổi policy. Bộ 20/8/4 đã dùng để điều chỉnh nên kết quả hiện tại chỉ phản ánh bộ lab.
- Thử topic classifier tiếng Việt hoặc model guard khác để giảm lỗi ngoài phạm vi ở ids 12/14/15; đánh giá trên holdout và giữ đủ clean controls. Bổ sung NER tiếng Việt nếu cần phát hiện tên thật, thay vì tái dùng NER tiếng Anh để chặn input.
- Thử giảm prompt, tái sử dụng client và giới hạn timeout/retry để giảm latency API. Đo thêm token usage, lỗi và p95 với ít nhất 100 mẫu; cache theo model/policy version, không lưu raw PII.
- Cải thiện generation từ extractive fallback sang câu trả lời có trích dẫn, kiểm tra multi-hop và metadata phiên bản; chạy lại Phase A để so answer relevancy/recall, không sửa ground truth.
- Đo riêng RAG, output rail và full request bằng timestamps quanh từng tầng, tách request allowed/blocked, warm-up ít nhất hai lượt và lưu raw samples. Sau đó mới đánh giá full-guard budget.

Theo dõi attack block rate, clean false-positive rate, output block rate, timeout/5xx, token cost và p50/p95/p99 theo model/policy version. Cảnh báo khi holdout attacks <90%, clean false positives >0%, có output nhạy cảm lọt, error rate >1% trong 5 phút hoặc input P95 >500ms; ngưỡng cần hiệu chỉnh theo traffic thật. Hà Anh Tuấn phụ trách guardrails, trưởng nhóm điều phối sửa/rollback; HR/IT cần duyệt policy trước production.

Lấy mẫu đã ẩn dữ liệu nhạy cảm để review định kỳ, tách lỗi retrieval/generation khỏi lỗi guard, theo dõi thay đổi corpus/model/prompt và hiệu chuẩn judge bằng nhãn người. Chưa có workflow hay monitoring production trong repo; các bước trên là kế hoạch kiểm chứng tiếp theo.
