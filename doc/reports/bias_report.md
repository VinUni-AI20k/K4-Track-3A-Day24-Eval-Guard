# Đánh giá LLM Judge Phase B

Nhóm: **Latentia**. Người phụ trách: **Nguyễn Minh Thắng — 2A202602706**.
Nguồn thực nghiệm: `artifacts/judge_results.json`, `run_kind=live`, format version 2.
Thời điểm lưu: **12/10/2026 20:18:45 UTC+07:00**; UTC gốc: `2026-10-12T13:18:45.107165+00:00`.
Models generation: `gpt-4o-mini-2024-07-18`.
Model judge thực sự được yêu cầu: `gpt-4o-mini`.

Đã chạy một batch bằng `python scripts/run_experiments.py --phase b --live`:
5 cặp, 10 lượt pairwise và 10 đánh giá binary. Không chọn lại candidate sau khi
xem kết quả, không dùng mock hoặc thay answer bằng ground truth. Artifact đã qua
schema, kiểm tra phép tính, ids, nguồn candidate/calibration và source hashes.

## Năm cặp A/B và hai lượt

Nguồn cố định: A từ `artifacts/answers_50q.json:answer`; B từ
`fixtures/human_labels_10q.json:model_answer`; reference từ
`fixtures/test_set_50q.json:ground_truth`. Hai lượt cùng question/reference.

| ID | Candidate A gốc | Candidate B gốc |
|---|---|---|
| 1 | Không tìm thấy. | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. |
| 5 | Cần phê duyệt của Giám đốc điều hành (CEO). | Cần Giám đốc phòng ban phê duyệt. |
| 12 | Thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên là **1 tháng lương**. | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. |
| 21 | Không tìm thấy. | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. |
| 41 | Không tìm thấy. | Nhân viên được nghỉ 12 ngày phép năm. |

| ID | Winner lượt 1 | Winner lượt 2 đã quy đổi | Final | Nhất quán | Scores lượt 1 | Scores lượt 2 đã quy đổi |
|---|---|---|---|---|---|---|
| 1 | B | B | B | Có | A=0; B=1 | A=0; B=1 |
| 5 | A | A | A | Có | A=1; B=0 | A=1; B=0 |
| 12 | A | tie | tie | Không | A=1; B=0.8 | A=1; B=1 |
| 21 | B | B | B | Có | A=0; B=1 | A=0; B=1 |
| 41 | B | A | tie | Không | A=0; B=0.5 | A=1; B=0 |

Ở lượt hai, A hiển thị là B gốc, B hiển thị là A gốc. Bảng đã đổi winner và
scores về A/B gốc; reasoning bên dưới được giữ nguyên phản hồi provider, nên
tên A/B trong reasoning lượt hai vẫn chỉ thứ tự hiển thị đã hoán đổi.
Final là consensus; không dùng trung bình scores để che bất nhất.

### Cặp 1 — Nhân viên được nghỉ bao nhiêu ngày khi kết hôn?

- Lượt 1 (A gốc trước, B gốc sau): Answer B accurately reflects the information provided in the reference, stating that employees are entitled to 3 days of paid leave when getting married. Answer A, on the other hand, does not provide any relevant information and is therefore incomplete.
- Lượt 2 (B gốc trước, A gốc sau): Answer A accurately reflects the information provided in the reference, stating that employees are entitled to 3 days of paid leave for marriage. Answer B, on the other hand, does not provide any relevant information and simply states that nothing was found, making it incomplete.

### Cặp 5 — Muốn mua thiết bị trị giá 55 triệu cần ai phê duyệt?

- Lượt 1 (A gốc trước, B gốc sau): Answer A correctly identifies that the approval of the CEO is required for purchases over 50 million VND, aligning with the reference. Answer B incorrectly states that the department head's approval is sufficient, which does not meet the requirement stated in the reference.
- Lượt 2 (B gốc trước, A gốc sau): Answer B correctly identifies that the approval of the CEO is required for purchases over 50 million VNĐ, aligning with the reference. Answer A incorrectly states that the department director's approval is sufficient, which does not meet the requirement stated in the reference.

### Cặp 12 — Thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên là bao nhiêu?

- Lượt 1 (A gốc trước, B gốc sau): Answer A provides a complete and accurate response by explicitly stating that the minimum Tết bonus for official employees with 6 months or more of service is 1 month of salary. Answer B, while correct, is less specific and does not mention the condition of having 6 months of service, making it less complete.
- Lượt 2 (B gốc trước, A gốc sau): Both answers accurately convey the information that employees with at least 6 months of service are entitled to a minimum of 1 month's salary as a Tet bonus. They are both complete and concise, providing the same essential information without unnecessary details.

### Cặp 21 — Một nhân viên Senior có 9 năm thâm niên được nghỉ bao nhiêu ngày phép năm và lương trong khoảng nào?

- Lượt 1 (A gốc trước, B gốc sau): Answer B provides a complete and accurate response to the question, detailing both the number of vacation days and the salary range for a Senior employee with 9 years of experience. Answer A, on the other hand, does not provide any relevant information and simply states 'Không tìm thấy' (Not found).
- Lượt 2 (B gốc trước, A gốc sau): Answer A provides a complete and accurate response to the question, detailing both the number of vacation days and the salary range for a Senior employee with 9 years of experience. Answer B, on the other hand, does not provide any relevant information and simply states that no information was found.

### Cặp 41 — Nhân viên được nghỉ bao nhiêu ngày phép năm?

- Lượt 1 (A gốc trước, B gốc sau): Answer B provides a specific number of leave days (12 days), which is relevant to the previous policy (v2023) but does not reflect the current policy (v2024). Answer A states 'Không tìm thấy' which does not provide any useful information. However, since the question asks for the number of leave days, Answer B is more informative despite being outdated.
- Lượt 2 (B gốc trước, A gốc sau): Answer A incorrectly states that employees are entitled to 12 days of leave, which is based on the outdated policy from 2023. Answer B, while not providing a specific answer, correctly indicates that there is no relevant information found, which aligns with the need to prioritize the current policy from 2024. Therefore, Answer B is more accurate in the context of the question.

## Position inconsistency và verbosity proxy

- Position inconsistency: **2/5 = 40%**, ở IDs **12 và 41**.
- Decisive cases: **3/5**, gồm IDs **1, 5 và 21**.
- Longer-answer wins: **3/3 = 100%**; A thắng và dài hơn ở ID 5,
  B thắng và dài hơn ở IDs 1 và 21. Tie không vào mẫu số verbosity.

ID 12 chuyển từ A thắng sang tie. A nêu rõ điều kiện nhân viên chính thức có ít
nhất 6 tháng, còn B ngắn hơn; lượt hai coi hai câu tương đương. Đây là dấu hiệu
tiêu chí completeness/diễn giải điều kiện chưa ổn định, không đủ tách nguyên nhân
vị trí khỏi biến động judgment.

ID 41 bất nhất B rồi A. Reference yêu cầu chính sách 2024 **15 ngày**; B dùng
2023 **12 ngày**, A chỉ nói không tìm thấy. Lượt một ưu tiên câu có số dù lỗi thời;
lượt hai ưu tiên abstention trước câu sai. Không thể coi winner tương đối là
nhãn tốt 1; consensus tie và binary label 0 của B phản ánh hai quy trình khác nhau.

Tỷ lệ dài hơn thắng 100% chưa chứng minh verbosity bias: ở cả 3 decisive cases,
winner đồng thời có thông tin đúng/đủ hơn (3 ngày kết hôn, đúng cấp CEO, đủ phép
và khung lương). Độ dài bị confound bởi accuracy/completeness. Cần thử các cặp
cùng nội dung đúng, chỉ thay lượng từ dư thừa, và đọc reasoning để kiểm chứng.

## Calibration trên đúng model_answer gốc

Prompt binary chỉ nhận question, model_answer và reference; không nhận
human_label, human_note hoặc phân bố nhãn. Các nhãn human chỉ được dùng đối chiếu
sau khi hoàn tất 10 judgments. Không lấy answer mới của pipeline để calibration.

| ID | Model answer gốc | Judge | Human | Agree | Reasoning của judge |
|---|---|---|---|---|---|
| 1 | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | 1 | 1 | Có | Câu trả lời chính xác theo reference, đầy đủ thông tin về số ngày nghỉ và điều kiện không trừ vào phép năm. |
| 5 | Cần Giám đốc phòng ban phê duyệt. | 0 | 0 | Có | Câu trả lời sai vì yêu cầu phê duyệt cho đơn hàng trên 50 triệu là từ Tổng Giám đốc, không phải Giám đốc phòng ban. |
| 12 | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | 1 | 1 | Có | Câu trả lời chính xác theo thông tin trong reference, nêu rõ điều kiện và mức thưởng cho nhân viên chính thức có từ 6 tháng trở lên. |
| 21 | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | 1 | 1 | Có | Câu trả lời chính xác theo reference, nêu rõ số ngày phép và khoảng lương cho nhân viên Senior có 9 năm thâm niên. |
| 23 | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | 1 | 1 | Có | Câu trả lời chính xác theo thông tin trong reference, nêu rõ rằng nhân viên phải hoàn trả 100% chi phí vì chưa đủ 1 năm cam kết. |
| 29 | Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu. | 0 | 0 | Có | Câu trả lời sai vì chỉ đề cập đến Trưởng phòng phê duyệt mà không nhắc đến Kế toán trưởng, và phí phạt được tính cho quá hạn 15 ngày chứ không phải là 2% trên 8 triệu cho toàn bộ thời gian. |
| 33 | Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng. | 1 | 1 | Có | Câu trả lời cung cấp đúng số ngày phép và tổng phụ cấp hàng tháng theo thông tin trong tài liệu tham khảo. |
| 41 | Nhân viên được nghỉ 12 ngày phép năm. | 0 | 0 | Có | Câu trả lời sai vì nó dựa trên chính sách cũ (v2023) thay vì chính sách hiện hành (v2024) là 15 ngày phép năm. |
| 46 | Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần. | 1 | 1 | Có | Câu trả lời chính xác theo reference, nêu rõ rằng nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần, đồng thời không bỏ qua điều kiện phê duyệt từ trưởng phòng. |
| 50 | Được, miễn là đảm bảo kết nối an toàn. | 0 | 0 | Có | Câu trả lời sai vì khẳng định cho phép sử dụng VPN cá nhân, trong khi reference rõ ràng cấm điều này. |

Judge và human đều có 6 nhãn 1, 4 nhãn 0, đồng ý **10/10**:

- `p_o = 10/10 = 1.00`.
- `p_e = (6/10 × 6/10) + (4/10 × 4/10) = 0.52`.
- `κ = (1 - 0.52)/(1 - 0.52) = 1.0`.

Lần chạy đạt ngưỡng bonus **κ >0.6** trên bộ calibration này. κ=1 chỉ chứng minh
agreement của 10 nhãn với fixture, không bảo đảm judge đúng trên dữ liệu mới hoặc
mọi reasoning đều faithful. Reasoning ở IDs 1, 12 và 46 suy thêm điều kiện
(không trừ phép năm, ít nhất 6 tháng, phê duyệt trưởng phòng) không được nêu rõ
trong chính model_answer. Reference chứa điều kiện không có nghĩa candidate đã
nêu điều kiện đó; cần audit reasoning riêng dù nhãn trùng human.

## Cách kiểm tra và giới hạn

Code Tasks 5–8 có commit riêng trên PR #1:
https://github.com/minhtuann1102/K4-L3-DAY24-Latentia-Eval-Guard/pull/1.
42 tests Phase B và 102 tests Phase B/helper/report-contract đã pass offline.
Test runner dùng SDK giả lập chỉ để kiểm tra schema/provenance và logic;
số đo trong báo cáo này lấy từ artifact live vừa tạo.

Pairwise dùng temperature=0, JSON mode, reference rubric accuracy/completeness/
conciseness, timeout 60s và tối đa 2 retries. Temperature=0 không đảm bảo phản hồi
provider luôn giống hệt. Candidate/reference được tuần tự hóa JSON với chỉ dẫn
coi là dữ liệu không đáng tin; chưa có stress test chứng minh chống prompt injection.

Mẫu chỉ 5 cặp/10 nhãn; chính sách tiếng Việt, thông tin ngầm từ câu hỏi và
abstention tạo judgment khó. Không dùng κ=1 để thay human review, không suy
40% bất nhất thành xác suất bias trên production. Cần thêm cặp tương đương về
nội dung/độ dài, mẫu holdout và review các bẫy phiên bản/phủ định.

Để kiểm tra artifact đã lưu, chạy `python scripts/check_lab.py` (không gọi API).
Chạy lại live có chi phí và có thể cho kết quả khác; cập nhật báo cáo theo JSON
mới nếu thực sự chạy lại. Các lỗi còn lại của toàn nhóm được ghi trong
`doc/SUBMISSION_REVIEW.md`, không phải lỗi schema hay hashes của Phase B.

## Hash của các nguồn đầu vào

- `answers_50q.json`: `8cab4c87cfb06d2fad7f8d3b9c835a460c27ea04dca844b94c6e91b821369ffd`.
- `test_set_50q.json`: `3ad288426e3066e561737b35b66b671e6c411697dffd0d1161cc7b801e5954cc`.
- `human_labels_10q.json`: `37231c1f4a635801e27a98333898d2d4c9c3c71167e8b9e7259b90cec5956782`.

Nguồn/AI hỗ trợ: README, ASSIGNMENT, RUBRIC, REPORT_SCHEMAS và scaffold của repo;
Codex hỗ trợ code, kiểm thử song song và phân tích artifact thật. Không dùng
nhãn human/notes trong prompt; không tạo số đo từ mock để nộp.
