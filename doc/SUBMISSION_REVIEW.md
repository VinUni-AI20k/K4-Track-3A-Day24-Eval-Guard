# Rà soát hồ sơ nộp bài theo README

Người rà soát: **Nguyễn Minh Thắng — MSSV 2A202602706**, nhóm **Latentia**.
Ngày rà soát: **12/10/2026**, Asia/Ho_Chi_Minh (UTC+07:00).
Deadline người dùng xác nhận: **12/10/2026 23:59**.

Nguồn yêu cầu: README.md, doc/SUBMISSION.md, CHECKPOINTS.md, ASSIGNMENT.md,
RUBRIC.md, REPORT_SCHEMAS.md và các schemas. Đây là rà soát bằng chứng hiện có,
không phải thông báo bài đã nộp hoặc toàn nhóm đã đạt điểm tối đa.

## Các file phải điền và tạo

| File / phần | Người phụ trách | Kết quả rà soát |
|---|---|---|
| doc/TEAM.md | Mỗi thành viên; Tuấn tổng hợp | Đủ 3 tên/MSSV/INDIVIDUAL; phần Thắng có live evidence và giới hạn; deadline đã sửa theo xác nhận |
| artifacts/answers_50q.json | Tuấn, CP0 | PASS schema/ids/nội dung nguồn; đủ 50 câu 20/20/10, generation fields hợp lệ |
| artifacts/ragas_50q.json | Tuấn, CP1 | Số đo/per-question qua contract nhưng FAIL metadata source hashes của answers/test set |
| doc/reports/failure_clusters.md | Tuấn; Thắng rà diễn giải | Markdown qua checker; đã sửa ID 41 theo contexts/reference và thêm cảnh báo provenance |
| src/phase_b_judge.py | Nguyễn Minh Thắng | Tasks 5–8 hoàn tất, không còn TODO; tests Phase B pass |
| artifacts/judge_results.json | Nguyễn Minh Thắng, CP2 | PASS schema, 5 cặp, 10 judgments, phép tính, candidate/calibration sources và hashes |
| doc/reports/bias_report.md | Nguyễn Minh Thắng | Đã điền đủ kết quả live, hai lượt, scores/reasoning, calibration, κ, bias và giới hạn |
| src/phase_c_guard.py | Nguyễn Thị Vàng | Còn TODO ở PII, input/output rails, suite và đo latency; 12 student tests fail |
| artifacts/guard_results.json | Nguyễn Thị Vàng, CP3 | Chưa có; thiếu bằng chứng 20 attacks, 8 clean, 4 outputs, warm-up/raw latency |
| doc/reports/blueprint.md | Cả nhóm; Thắng tổng hợp A/B/đề xuất | Đã điền kiến trúc/failure actions/gates/monitoring; bắt buộc bổ sung số đo C sau khi có artifact |
| PLAN.md | Cả nhóm | Hai bước của Thắng đã đánh dấu hoàn tất; không đánh dấu toàn repo pass |
| README và các tài liệu đề bài | Tài liệu hướng dẫn | Đã đọc/đối chiếu; không phải form cần tự khai kết quả |

Các file fixtures/test_set_50q.json, human_labels_10q.json, adversarial_set_20.json,
clean_set_8.json và output_set_4.json là nguồn kiểm thử. Không thay nhãn hoặc nội dung
để làm tăng điểm. `.env` chứa key của máy, bị ignore; `.env.example` chỉ là mẫu rỗng.
Không nộp virtualenv, model cache, compiler/Conda installer hoặc key.

## Bằng chứng đã chạy cho Nguyễn Minh Thắng

Một batch live `python scripts/run_experiments.py --phase b --live`, artifact
timestamp `2026-10-12T13:18:45.107165+00:00`
(12/10/2026 20:18:45 UTC+07:00). Model judge yêu cầu: gpt-4o-mini.
Đủ 10 pairwise calls và 10 binary judgments trên model_answer gốc.

- Agreement 10/10; p_o=1, p_e=0.52, **Cohen κ=1.0**.
- Position inconsistency **2/5=40%**, IDs 12 và 41.
- Longer-answer win proxy **3/3=100%** trong decisive cases; chưa chứng minh
  nguyên nhân là verbosity vì winner đồng thời đúng/đủ hơn.
- Artifact live và báo cáo có cùng nguồn, scores/labels/counts/timestamps.
- Bộ kiểm tra riêng B/helper/contracts trước đó: **102 pass**, gồm **42 Phase B**.
- `pip check` trên Conda Python 3.11.17: **No broken requirements found**.

## Kiểm tra toàn repo đã thực hiện

Lệnh theo README:

```powershell
& D:\DayVinAI\envs\vinai_env\python.exe scripts/check_lab.py --with-tests
```

Kết quả: **108 tests pass, 12 tests fail, 3 integration tests deselected**.
Không chạy thêm live integration B/C để tránh lặp chi phí API.
Cả 12 test fail thuộc tests/test_phase_c.py, phù hợp với các hàm C chưa implement.

Checker có **4 failed checks**, không phải điểm rubric:

1. phase_c_guard.py: unfinished student TODOs.
2. Phase A artifact: stale experiment source answers_50q.json. Kiểm tra riêng
   cũng xác nhận hash test_set_50q.json trong metadata A không khớp file hiện tại.
3. Phase C artifact: guard_results.json không tồn tại.
4. Offline pytest: các tests Phase C còn fail.

TEAM và cả ba Markdown reports qua kiểm tra placeholder/table; **Phase B artifact PASS**.
Markdown không còn placeholder không có nghĩa measurements C đã hoàn thành.
Không sửa expected hashes, fake raw samples hoặc đổi actual/labels để ép checker pass.

## Công việc còn lại trước nộp

### Nguyễn Minh Tuấn — Phase A và nguồn thí nghiệm

Chạy lại A với đúng source hiện tại, hoặc truy lại bytes/source của lần A gốc
và bằng chứng tương ứng; không tự thay hashes trong report cũ. Đối chiếu 50 rows,
4 metrics, bottom 10, matrix/means và model roles; cập nhật failure_clusters.md
nếu số đo thay đổi. Nếu answers/test set đổi nội dung sau lượt B, B cũng cần chạy
lại với nguồn mới để metadata và candidate/provenance khớp.

Source m2 hiện tại chỉ có BM25; mô tả “HybridSearch” hoặc Qdrant đang chạy không
chứng minh dense retrieval được dùng. Không khai đã triển khai dense index khi
source không gọi nó. ID 41 có contexts khác chủ đề và answer abstain; cần đọc
contexts trước khi kết luận đã retrieve cả chính sách v2023/v2024.

### Nguyễn Thị Vàng — Phase C

Hoàn thành Tasks 9a–12 và tests; chạy:

```powershell
python scripts/run_experiments.py --phase c --live --latency-samples 20
```

Cần kết quả thật: ít nhất 15/20 attacks, 8/8 clean allowed, 4 output cases đúng;
hai warm-up, ít nhất 20 positive timed samples, percentiles tuyến tính và scope
input_layers_sequential. Bonus attacks cần 18/20 kèm clean controls đạt.
Ghi số latency thật dù vượt target, rồi cập nhật blueprint và phần INDIVIDUAL.

### Cả nhóm / trưởng nhóm

Sau khi sửa A/C, cập nhật blueprint theo report C; đo full guard riêng nếu muốn
kết luận SLA full scope. Chạy lại checker, kiểm tra secrets, chọn commit SHA cuối
cùng trong TEAM, push/nộp link repo chung qua vlearn trước deadline đã xác nhận.
Không khai nhóm đã nộp khi chưa có bằng chứng gửi bài.

Mẫu 50/10/20/8/4 chỉ là bộ lab; pipeline vẫn cần holdout, privacy review,
load tests và gates được triển khai thật trước khi coi là production-ready.
