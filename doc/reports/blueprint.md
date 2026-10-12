# Blueprint CI/CD cho RAG và guardrails

Nhóm: **Latentia**. Người tổng hợp: **Nguyễn Minh Thắng — 2A202602706**.
Phase A: Nguyễn Minh Tuấn; Phase B: Nguyễn Minh Thắng; Phase C: Nguyễn Thị Vàng.
Đây là **đề xuất**, chưa có CI workflow hoặc deployment được thực thi.

Nguồn A: `artifacts/ragas_50q.json`, timestamp `2026-10-12T05:07:01.841963+00:00`.
Metadata A không khớp hashes của answers/test set hiện tại; các số A dưới đây là
số đang lưu để phân tích, chưa đạt kiểm chứng provenance để dùng làm gate nộp bài.
Nguồn B: `artifacts/judge_results.json`, timestamp `2026-10-12T13:18:45.107165+00:00`,
đã qua schema và provenance. `guard_results.json` chưa có, Phase C còn TODO.
Models generation: `gpt-4o-mini-2024-07-18`;
evaluator A khai báo `BAAI/bge-m3, gpt-4o-mini`;
judge B: `gpt-4o-mini`.
Guard model cấu hình dự kiến `gpt-4o-mini`; chưa có report C chứng minh lượt inference.

## Kiến trúc và failure action

Kiến trúc mục tiêu: Input → Presidio → NeMo input → RAG → NeMo output → response.
Presidio phát hiện/redact PII; input rail chặn yêu cầu ngoài phạm vi hoặc jailbreak;
RAG lấy context, rerank và sinh answer; output rail kiểm tra tiết lộ dữ liệu/
nội dung không an toàn trước trả kết quả. Request thật dừng sớm khi bị chặn.

Đối chiếu source hiện tại: m2 đang triển khai BM25, chưa có dense/Qdrant retrieval;
m3 dùng FlashRank và có fallback lấy top search khi reranker lỗi. Qdrant có thể
chạy nhưng không đủ chứng minh m2 đang sử dụng nó. Kết quả A/B là bằng chứng
của pipeline và source đang lưu, không tự chứng minh kiến trúc mục tiêu đầy đủ.

Đề xuất fail closed khi guard/provider lỗi: trả lời từ chối an toàn, log loại lỗi
và request id, không log key hoặc toàn bộ PII. Khi retrieval không đủ, abstain rõ
ràng; không đưa ground truth của bộ kiểm thử vào generation. Extractive fallback
phải gắn generation_mode và null model, không giả là LLM response.
Secrets qua `.env`/secret manager, tách dev/test/production; log phải redact.

## Phạm vi latency và số đo

Task 12 bắt buộc đo **input_layers_sequential**, luôn chạy Presidio và NeMo input,
engines tạo trước, 2 warm-up thật loại khỏi thống kê, ít nhất 20 timed samples.
Percentiles nội suy tuyến tính; P95 tổng tính từ từng tổng sample, không cộng P95 tầng.

| Scope | P50 ms | P95 ms | P99 ms | Tình trạng |
|---|---|---|---|---|
| Presidio | Chưa đo | Chưa đo | Chưa đo | Task 12 còn thiếu, Vàng phụ trách |
| NeMo input | Chưa đo | Chưa đo | Chưa đo | Task 12 còn thiếu, Vàng phụ trách |
| Input guard sequential | Chưa đo | Chưa đo | Chưa đo | Chưa có raw samples |
| RAG | Chưa đo | Chưa đo | Chưa đo | Ngoài phạm vi bắt buộc Task 12 |
| NeMo output | Chưa đo | Chưa đo | Chưa đo | Ngoài phạm vi bắt buộc Task 12 |
| Full guard/request short-circuit | Chưa đo | Chưa đo | Chưa đo | Không suy từ input_guard_ms |

Timed samples, warm-up, latency_budget_ok: chưa có artifact để xác nhận.
Target input-layer P95: 500ms. Các mục Task 12 chưa đo là **công việc chưa hoàn tất**,
không được coi là pass chỉ vì bảng Markdown đã điền. Sau khi có report C, điền
số thật và phân tích bottleneck nếu vượt target, không chỉnh số cho đạt.
Phần ngoài Task 12 cần benchmark riêng với warm-up, timestamps, số mẫu và scopes.

## CI gates đề xuất

1. Job offline: `python -m pytest tests/ -m "not integration" -q`;
   dừng khi còn student test fail/TODO, không gọi provider trong unit tests.
2. Evidence job: `python scripts/check_lab.py`; dừng nếu thiếu schema, id,
   nguồn/hashes, artifact hay Markdown bắt buộc. Hiện job chưa pass toàn nhóm.
3. Quality job đề xuất: faithfulness ≥0.75, avg_score ≥0.65, κ >0.6;
   attacks ≥18/20, clean 8/8 allowed, output 4/4 đúng. Script gate cần đọc số và
   trả nonzero thật; việc đặt MIN_* chưa tự tạo gate. Không có workflow đã triển khai.
4. Lab bắt buộc vẫn attacks ≥15/20; bonus/CI đề xuất ≥18/20 chỉ khi clean controls đạt.
5. Full guard P95 <500ms chỉ xét sau khi đo đúng full scope, không dùng input P95.

Số A đang lưu: mean faithfulness **0.4964**, mean avg_score **0.5387**,
nhóm yếu nhất **multi_hop**, avg **0.4273**.
Các số này thấp hơn target đề xuất và provenance A còn lỗi, nên chưa qua gate.
B: κ **1.0**, inconsistency **40%**, longer winner proxy **100%** trên 3 decisive cặp.
C: attacks, clean false-positive rate và output accuracy chưa đo; chưa đánh giá gate.

## Monitoring và cải tiến

- Theo dõi retrieval-empty/abstention, RAGAS faithfulness/recall, và chất lượng từng
  distribution trên mẫu review hằng tuần; cảnh báo khi giảm so với baseline đã validate.
- Log disagreement giữa hai lượt judge và case lệch human; tỷ lệ 40% của 5 cặp chỉ
  là tín hiệu điều tra. Xây holdout có số lượng lớn hơn, review ID 12 và 41 trước tự động hóa.
- Theo dõi guard allow/block và false positives trên clean controls; lỗi policy
  hoặc provider phải tạo alert cho người phụ trách, không im lặng bỏ guard.
- Theo dõi P50/P95/P99, timeout, token usage và cost; kiểm tra scope đo trước gọi là
  full latency. Tối thiểu 20 mẫu chỉ là yêu cầu lab, chưa đủ SLA production.
- Redact PII trước log, hạn chế lưu raw prompt, phân quyền artifact và retention;
  dùng dữ liệu mẫu khi thử nghiệm. Không commit key/cache/environment.

Ưu tiên kiểm chứng: (1) Tuấn chạy lại A với đúng source để sửa provenance;
(2) kiểm tra retrieval cho ID 41 và bổ sung version metadata/parent retrieval;
(3) thử độ dài độc lập correctness để đo verbosity effect của B;
(4) Vàng hoàn thành C, chạy attacks + clean + outputs và latency;
(5) tổng hợp lại blueprint và chạy checker trước trưởng nhóm nộp.
