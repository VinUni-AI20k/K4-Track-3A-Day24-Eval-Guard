# Đánh giá LLM Judge Phase B

Nhóm: ThienBinh

Người phụ trách: {{Họ tên và MSSV}}

Nguồn: `artifacts/judge_results.json`; run timestamp: 2026-10-12T14:53:31.250071+00:00 (21:53 UTC+07).
Models generation/judge: generation (candidate A, từ answers_50q.json) = `gemini-3.5-flash-lite`,
`gemini-3.6-flash`, `gemini-3.7-flash`, `gemini-3.8-flash`; judge = `gemini-3.5-flash-lite`
(cả pairwise Task 5–6 và binary calibration).

## Năm cặp A/B và hai lượt

Nguồn cố định: A từ artifacts/answers_50q.json:answer; B từ
fixtures/human_labels_10q.json:model_answer; reference từ fixtures/test_set_50q.json:ground_truth.
Ids: 1, 5, 12, 21, 41. Không đổi nguồn sau khi xem kết quả judge.

Pass 1 chấm (A, B); pass 2 hoán đổi thành (B, A) rồi quy winner và scores về nhãn A/B gốc. Lưu ý:
reasoning của pass 2 viết theo vị trí đã hoán đổi, nên chữ "câu A" trong reasoning pass 2 là
candidate B gốc.

| id | Candidate A (pipeline) | Candidate B (human_labels) | winner_pass1 | winner_pass2 (quy về gốc) | final_winner | position_consistent | scores pass1 (A/B) | scores pass2 (A/B) |
|---|---|---|---|---|---|---|---|---|
| 1 | "…nghỉ **3 ngày làm việc** khi kết hôn (không trừ vào phép năm)." | "…nghỉ 3 ngày làm việc có lương khi kết hôn." | tie | A | tie | false | 1.0 / 1.0 | 1.0 / 0.8 |
| 5 | "…cần **Tổng Giám đốc (CEO)** phê duyệt." | "Cần Giám đốc phòng ban phê duyệt." | A | A | A | true | 1.0 / 0.0 | 1.0 / 0.0 |
| 12 | "…từ 6 tháng trở lên là **1 tháng lương**." | "…thưởng Tết tối thiểu 1 tháng lương." | A | A | A | true | 1.0 / 0.7 | 1.0 / 0.8 |
| 21 | "18 ngày phép (15 + 3)… **Không tìm thấy** thông tin về lương" | "18 ngày phép (15 + 3 thâm niên). Lương Senior từ 20 đến 35 triệu." | B | B | B | true | 0.5 / 1.0 | 0.5 / 1.0 |
| 41 | "v2023: 12 ngày; v2024: 15 ngày; thâm niên +1 ngày/5 năm" | "Nhân viên được nghỉ 12 ngày phép năm." | A | A | A | true | 0.8 / 0.2 | 0.9 / 0.2 |

Reasoning tóm tắt:

- **id 1:** pass 1 thấy hai câu tương đương (tie). Pass 2 (A ở vị trí thứ hai) chấm A cao hơn vì có
  thêm "không trừ vào phép năm", đúng reference. Final = tie theo quy tắc swap-and-average.
- **id 5:** cả hai lượt đều xác định trên 50 triệu cần CEO duyệt; B sai.
- **id 12:** cả hai lượt chọn A vì nhắc lại đủ điều kiện đối tượng "chính thức, từ 6 tháng trở lên";
  B đúng số nhưng thiếu điều kiện.
- **id 21:** cả hai lượt chọn B vì A bỏ sót khoảng lương ("Không tìm thấy") trong khi reference có
  20–35 triệu.
- **id 41:** cả hai lượt chọn A vì có 15 ngày theo v2024 hiện hành. B chỉ nêu 12 ngày (v2023, hết
  hiệu lực). A vẫn có lỗi: gắn quy tắc thâm niên của v2023.

Position bias count/rate: 1/5 cặp không nhất quán giữa hai lượt (rate 0.20, id 1).
Verbosity win rate: 0.75 (3/4); decisive cases: 4 (id 5, 12, 21, 41; id 1 là tie nên không tính).

Diễn giải:

- **Case không nhất quán (id 1):** hai answer gần như tương đương về nội dung. Pass 1 cho tie, pass
  2 nghiêng về A vì A có thêm một chi tiết đúng reference. Đây là vùng sát ranh giới, nơi thứ tự
  trình bày đủ để đổi kết quả. Quy tắc swap-and-average đưa về tie, đúng với mục đích giảm position
  bias. Với 5 cặp, 1 case chưa đủ để kết luận judge có thiên vị vị trí đầu hay vị trí sau.
- **Verbosity 3/4:** answer dài hơn thắng ở id 5, 12, 41, và answer ngắn hơn thắng ở id 21. Đọc nội
  dung thì cả 3 lần answer dài thắng đều do đúng hơn: id 5 B sai người duyệt, id 12 B thiếu điều
  kiện, id 41 B dùng chính sách hết hiệu lực. Ở id 21, answer dài hơn (A) thua vì thiếu ý. Vậy 0.75
  là dấu hiệu thống kê trùng với chất lượng nội dung, không phải bằng chứng judge thưởng độ dài. Muốn
  tách được hai yếu tố cần các cặp đúng như nhau nhưng khác độ dài.

## Calibration đúng model_answer

Helper đánh giá đúng question/model_answer đang có trong fixtures/human_labels_10q.json;
không lấy answer mới của pipeline. Prompt chỉ nhận question, answer, reference.
Không gửi human_label, human_note hoặc phân bố nhãn human vào prompt.

| question_id | model_answer gốc | Judge | Reasoning của judge (tóm tắt) | human_label | agree |
|---|---|---|---|---|---|
| 1 | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | 1 | Đúng và đủ ý chính theo reference | 1 | ✓ |
| 5 | Cần Giám đốc phòng ban phê duyệt. | 0 | Trên 50 triệu phải do CEO duyệt; answer sai người duyệt | 0 | ✓ |
| 12 | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | 1 | Đúng mức thưởng tối thiểu 1 tháng lương | 1 | ✓ |
| 21 | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | 1 | Đúng số ngày phép và khoảng lương theo v2024 | 1 | ✓ |
| 23 | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | 1 | Đúng số tiền hoàn trả và lý do | 1 | ✓ |
| 29 | Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu. | 0 | Thiếu Kế toán trưởng phê duyệt; tính sai phí phạt quá hạn | 0 | ✓ |
| 33 | Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng. | 1 | Đúng 19 ngày phép và 1.500.000 VNĐ phụ cấp | 1 | ✓ |
| 41 | Nhân viên được nghỉ 12 ngày phép năm. | 0 | Dùng chính sách cũ v2023 thay vì v2024 (15 ngày) | 0 | ✓ |
| 46 | Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần. | 1 | Giữ đúng phủ định và quy định nghỉ không lương | 1 | ✓ |
| 50 | Được, miễn là đảm bảo kết nối an toàn. | 0 | Reference cấm VPN cá nhân; answer đảo ngược điều kiện | 0 | ✓ |

Cohen’s κ: 1.0.
Observed/chance agreement và diễn giải: observed agreement p_o = 10/10 = 1.0. Judge và human đều có
6 nhãn 1 và 4 nhãn 0, nên chance agreement p_e = 0.6 × 0.6 + 0.4 × 0.4 = 0.52, và
κ = (p_o − p_e) / (1 − p_e) = (1.0 − 0.52) / 0.48 = 1.0. Theo thang Landis-Koch đây là "almost
perfect", vượt ngưỡng > 0.6 mà đề yêu cầu.

## Giới hạn và cách dùng judge

- **Mẫu nhỏ:** κ = 1.0 trên 10 nhãn không có nghĩa judge luôn đúng. Chỉ cần lệch 1 nhãn là κ giảm
  còn khoảng 0.8. Các câu trong bộ này có đáp án rõ ràng (đúng/sai số liệu, đúng/sai phiên bản);
  judge chưa được thử trên câu mơ hồ hay answer đúng một phần.
- **Một model, một prompt:** judge là `gemini-3.5-flash-lite` với temperature 0 và JSON mode. Model
  này cũng là một trong 4 model sinh candidate A (25/50 answers), nên có rủi ro self-preference khi
  judge chấm answer do chính nó sinh. Trong 5 cặp A/B, A thắng 3, B thắng 1, tie 1; với số mẫu này
  chưa tách được self-preference khỏi chất lượng thật.
- **Không có case lệch human** trong lần chạy này, nên chưa có ví dụ thất bại để phân tích. Cần thêm
  nhãn human cho các câu khó (multi-hop có tính toán, version conflict) trước khi tin judge ở quy mô
  lớn.
- **Cách kiểm chứng tiếp:** (1) chạy lại calibration với một judge khác họ model để đo độ ổn định của
  κ; (2) thêm các cặp đúng như nhau nhưng khác độ dài để đo verbosity bias thật; (3) theo dõi tỉ lệ
  position_consistent trên nhiều cặp hơn 5.
- **Cách dùng:** judge phù hợp để sàng lọc và xếp hạng nhanh. Không dùng judge làm đáp án tuyệt đối:
  các case tie hoặc không nhất quán, và mọi quyết định quan trọng (gate release) vẫn cần human
  review mẫu.
