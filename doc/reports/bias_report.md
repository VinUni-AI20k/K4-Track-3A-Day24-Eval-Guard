# Đánh giá LLM Judge Phase B

Nhóm: Latentia. Người phụ trách: Nguyễn Minh Thắng — 2A202602706.
Ngày kiểm tra code: 12/10/2026 (Asia/Ho_Chi_Minh).
Nhánh: `feat/phase-b-minh-thang`.

## Trạng thái bằng chứng

Tasks 5–8 đã implement. Bộ kiểm tra Phase B có 42 tests pass;
cùng helper và report contracts có 102 tests pass, tất cả offline.
Key OpenAI để người dùng cập nhật sau, nên chưa chạy judge live và chưa tạo
`artifacts/judge_results.json`. Chưa có timestamp hoặc số đo judge thật.
Kết quả mock chỉ nằm trong thư mục tạm của test, không dùng làm artifact nộp bài.
Judge cấu hình: `config.JUDGE_MODEL` (`gpt-4o-mini`). Metadata model của lượt live
sẽ được runner ghi vào JSON.

## Năm cặp A/B và hai lượt

Nguồn cố định: A từ `artifacts/answers_50q.json:answer`; B từ
`fixtures/human_labels_10q.json:model_answer`; reference từ
`fixtures/test_set_50q.json:ground_truth`. Hai lượt dùng cùng question/reference.

| Question id | Ký tự candidate A | Ký tự candidate B | Kết quả hai lượt |
|---|---:|---:|---|
| 1 | 15 | 57 | Chưa chạy |
| 5 | 43 | 33 | Chưa chạy |
| 12 | 89 | 50 | Chưa chạy |
| 21 | 15 | 82 | Chưa chạy |
| 41 | 15 | 37 | Chưa chạy |

Task 5 đánh giá accuracy, completeness, conciseness theo reference và yêu cầu
JSON A/B/tie, reasoning không rỗng, scores hữu hạn trong [0,1]. Bool, NaN,
Infinity, thiếu trường hoặc điểm ngoài khoảng đều bị từ chối. Candidate và
reference được gửi dưới dạng dữ liệu JSON với chỉ dẫn không làm theo instructions
bên trong; chưa có thực nghiệm để khẳng định khả năng chống prompt injection.

Task 6 đổi thứ tự A/B ở lượt hai, quy đổi cả winner và scores về thứ tự gốc;
đồng thuận thì giữ winner, bất nhất thì tie. Task 8 tính position inconsistency
trên tất cả cặp; longer-answer win rate trên các cặp decisive A/B, không tính tie
hoặc answer dài bằng nhau là longer-answer win. Các tỷ lệ không làm tròn sớm.

Position bias count/rate và verbosity win rate: **chưa đo**. Đây là proxy quan sát,
không chứng minh nguyên nhân là position hay verbosity; phải đọc nội dung và accuracy.

## Calibration đúng model_answer

Runner đánh giá đúng question/model_answer của human fixture và ground_truth
cùng id. Không thay bằng answer mới của pipeline. Prompt chỉ nhận question,
answer, reference; không gửi human_label, human_note hay phân bố nhãn.
Bảng human dưới đây chỉ để đối chiếu sau judge.

| Question id | Human label từ fixture | Judge label | Agree |
|---|---:|---|---|
| 1 | 1 | Chưa chạy | Chưa đối chiếu |
| 5 | 0 | Chưa chạy | Chưa đối chiếu |
| 12 | 1 | Chưa chạy | Chưa đối chiếu |
| 21 | 1 | Chưa chạy | Chưa đối chiếu |
| 23 | 1 | Chưa chạy | Chưa đối chiếu |
| 29 | 0 | Chưa chạy | Chưa đối chiếu |
| 33 | 1 | Chưa chạy | Chưa đối chiếu |
| 41 | 0 | Chưa chạy | Chưa đối chiếu |
| 46 | 1 | Chưa chạy | Chưa đối chiếu |
| 50 | 0 | Chưa chạy | Chưa đối chiếu |

Cohen’s κ, observed agreement và chance agreement: **chưa đo**.
Task 7 dùng `p_o = số nhãn trùng/n`,
`p_e = tổng_c(n_judge,c * n_human,c)/n²`, `κ = (p_o-p_e)/(1-p_e)`.
Theo quy ước của scaffold, rỗng hoặc p_e=1 trả 0; khác độ dài, bool hoặc nhãn
không phải integer 0/1 bị từ chối. Bộ calibration thật có hai lớp.
Chưa có bằng chứng đạt bonus κ >0.6.

## Kiểm thử và chạy live

```powershell
& D:\DayVinAI\envs\vinai_env\python.exe -m pytest tests/test_phase_b.py tests/test_phase_b_edges.py tests/test_support.py tests/test_report_contracts.py -q
```

Test runner dùng các hàm Phase B thật, 20 phản hồi SDK giả lập, kiểm tra 5 cặp,
10 model_answer gốc, prompt không leak nhãn/notes, schema và source hashes.
SDK mock kiểm tra logic/contracts, không đo chất lượng judgment của LLM.

Sau khi điền key hợp lệ trong `.env`, mở Miniconda Prompt:

```powershell
conda activate vinai_env
python scripts/run_experiments.py --phase b --live
```

Runner thực hiện 10 pairwise calls và 10 binary calls, validate schema/nguồn và
ghi JSON. Khi có JSON thật, bổ sung winner, scores, reasoning của hai lượt,
10 nhãn judge, κ và bias rates vào báo cáo này.

## Giới hạn

Chỉ có 5 cặp và 10 nhãn; reference có thể thiếu ý, judge có thể chịu prompt
injection hoặc thiên lệch ngữ nghĩa. Đọc từng case bất nhất/lệch human trước khi
kết luận; không xem judge là đáp án tuyệt đối. Chưa chạy inference API do thiếu key.

## Hash của dữ liệu đầu vào hiện tại

- `artifacts/answers_50q.json`: `8cab4c87cfb06d2fad7f8d3b9c835a460c27ea04dca844b94c6e91b821369ffd`.
- `fixtures/test_set_50q.json`: `3ad288426e3066e561737b35b66b671e6c411697dffd0d1161cc7b801e5954cc`.
- `fixtures/human_labels_10q.json`: `37231c1f4a635801e27a98333898d2d4c9c3c71167e8b9e7259b90cec5956782`.

Nguồn/AI hỗ trợ: đề bài, rubric và scaffold của repo; Codex hỗ trợ implementation,
kiểm tra biên song song và kiểm chứng offline. Không khai mock thành thực nghiệm live.
