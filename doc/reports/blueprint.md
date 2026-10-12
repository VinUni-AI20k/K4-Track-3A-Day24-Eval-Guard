# Blueprint CI/CD cho RAG va guardrails

Nhom: NhomBotVN
Nguoi phu trach: Nguyen Van Dai - 02477

Day la de xuat CI/CD, chua phai workflow da trien khai. Nguon ket qua la ba artifact trong `artifacts/`; model IDs va timestamp phai lay tu metadata live run, khong suy dien khi artifact chua co.

## Kien truc va failure action

Input -> Presidio -> NeMo input -> RAG -> NeMo output -> response.

Presidio phat hien/anonymize PII truoc khi chuyen tiep; NeMo input rail chan jailbreak/off-topic. Request dung som khi bi chan. Output rail redaction cau tra loi nhay cam. Log chi ghi request id, category va rail decision, khong ghi plaintext PII. Secrets chi qua bien moi truong; fallback extractive chi dung khi generation that bai.

## Pham vi va so do latency

Task 12 co scope `input_layers_sequential`: Presidio + NeMo input, khong short-circuit; engine tao truoc do, 2 warm-up that, percentile noi suy tuyen tinh, tong `input_guard_ms` tinh tu tung sample. Live latency artifact chua co trong starter checkout.

| Layer / scope | P50 ms | P95 ms | P99 ms | Trang thai |
|---|---:|---:|---:|---|
| Presidio | chua do | chua do | chua do | Cho live run |
| NeMo input | chua do | chua do | chua do | Cho live run |
| Input guard sequential | chua do | chua do | chua do | Cho live run |
| RAG | chua do | chua do | chua do | Ngoai pham vi bat buoc |
| NeMo output | chua do | chua do | chua do | Ngoai pham vi bat buoc |
| Full guard / short-circuit request | chua do | chua do | chua do | Khong suy tu input_guard_ms |

Budget input-layer la 500 ms. Khi co live run, ghi raw samples/warm-up; neu vuot budget thi profile rieng Presidio/NeMo va danh gia caching. RAG/output/full request can phep do rieng.

## CI gates de xuat

- RAGAS faithfulness >= 0.75 va avg_score >= 0.65 tren 50 cau.
- Attacks >= 18/20, clean 8/8 allowed, output cases dung.
- Full guard P95 < 500 ms chi ap dung sau khi do full guard that.
- Lab gate bat buoc: attacks >= 15/20 va clean 8/8; script tra non-zero khi khong dat.

Workflow nay la de xuat, chua duoc trien khai trong repo.

## Monitoring va cai tien

Theo doi attack pass rate, clean false-positive rate, output flags, P95 input latency va drift theo category. Alert khi clean < 8/8, attack < 18/20 hoac P95 >= 500 ms. Redact PII trong log; sampling dung request id. Gioi han mau hien tai la 50/20/8/4 theo artifact.

RAGAS mean/worst distribution: xem `artifacts/ragas_50q.json`.
Cohen's kappa: xem `artifacts/judge_results.json`.
Attacks passed va clean false-positive rate: xem `artifacts/guard_results.json`.

Cai tien: bo sung attack variants theo drift; benchmark Presidio/NeMo theo release; ra soat false positives tren clean controls; kiem tra output redaction tren 4 cases; tang mau latency khi thay doi model.
