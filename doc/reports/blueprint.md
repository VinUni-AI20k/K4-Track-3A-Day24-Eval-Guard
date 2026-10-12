# Blueprint CI/CD cho RAG va guardrails

Nhom: NhomBotVN
Nguoi phu trach: Nguyen Van Dai (MSSV: 2A202602477) - Nhanh lam viec: dai-phase-c

Day la de xuat CI/CD, chua phai workflow da trien khai. Nguon ket qua la ba artifact trong `artifacts/`; model IDs va timestamp phai lay tu metadata live run, khong suy dien khi artifact chua co.

## Kien truc va failure action

Input -> Presidio -> NeMo input -> RAG -> NeMo output -> response.

Presidio phat hien/anonymize PII truoc khi chuyen tiep; NeMo input rail chan jailbreak/off-topic. Request dung som khi bi chan. Output rail redaction cau tra loi nhay cam. Log chi ghi request id, category va rail decision, khong ghi plaintext PII. Secrets chi qua bien moi truong; fallback extractive chi dung khi generation that bai.

## Pham vi va so do latency

Task 12 co scope `input_layers_sequential`: Presidio + NeMo input, khong short-circuit; engine tao truoc do, 2 warm-up that, percentile noi suy tuyen tinh, tong `input_guard_ms` tinh tu tung sample. So lieu duoc do truc tiep tu live run va ghi nhan trong `artifacts/guard_results.json`.

| Layer / scope | P50 ms | P95 ms | P99 ms | Trang thai |
|---|---:|---:|---:|---|
| Presidio | 7.22 | 8.28 | 10.23 | Da do (live) |
| NeMo input | 630.92 | 741.45 | 908.10 | Da do (live) |
| Input guard sequential | 637.88 | 749.10 | 915.23 | Da do (live) |
| RAG | chua do | chua do | chua do | Ngoai pham vi bat buoc |
| NeMo output | chua do | chua do | chua do | Ngoai pham vi bat buoc |
| Full guard / short-circuit request | chua do | chua do | chua do | Khong suy tu input_guard_ms |

Budget input-layer la 500 ms. So do thuc te P95 dat 749.10 ms (Presidio 8.28 ms, NeMo input 741.45 ms). Phan lon do tre tap trung o tang NeMo input goi API gpt-4o-mini qua mang internet (~600-700ms round-trip). Presidio cuc bo cuc ky nhanh (<9ms P95). De toi uu duoi 500ms: can cache intent cho cac cau hoi pho bien, hoac dung model small local (vLLM on-premise) thay vi goi cloud API. RAG/output/full request can phep do rieng.

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
