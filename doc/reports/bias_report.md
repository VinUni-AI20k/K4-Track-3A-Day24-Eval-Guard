# Đánh giá LLM Judge Phase B

Nhóm: NhomBotVN

Người phụ trách: Nguyễn Minh Ngọc (MSSV: 2A202602530)

Nguồn: `artifacts/judge_results.json`; thời điểm chạy: 12/10/2026 17:32:56
(Asia/Ho_Chi_Minh, chuyển đổi từ `2026-10-12T10:32:56.687590+00:00`).

- Model sinh câu trả lời: `gpt-4o-mini-2024-07-18`.
- Model judge: `gpt-4o-mini`.
- Loại chạy: `live`.

## Năm cặp A/B và hai lượt

Nguồn được giữ cố định cho cả năm cặp: A lấy từ
`artifacts/answers_50q.json:answer`, B lấy từ
`fixtures/human_labels_10q.json:model_answer`, và reference lấy từ
`fixtures/test_set_50q.json:ground_truth`. Các ID được đánh giá là 1, 5, 12,
21 và 41.

`winner_pass2` và `scores_pass2` trong bảng đã được quy đổi về A/B gốc. Riêng
nội dung `reasoning_pass2` vẫn dùng ký hiệu A/B theo thứ tự trình bày ở lượt hai,
tức là thứ tự đã hoán đổi.

|  ID | Candidate A                                                                                                                                                      | Candidate B                                                                        | Pass 1          | Pass 2 (quy về A/B gốc) | Kết quả cuối | Nhất quán |
| --: | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | --------------- | ----------------------- | ------------ | --------- |
|   1 | Nhân viên được nghỉ 3 ngày làm việc khi kết hôn.                                                                                                                 | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn.                          | B; A=0,7, B=1,0 | B; A=0,5, B=1,0         | B            | Có        |
|   5 | Không tìm thấy.                                                                                                                                                  | Cần Giám đốc phòng ban phê duyệt.                                                  | B; A=0,0, B=1,0 | A; A=0,5, B=0,0         | tie          | Không     |
|  12 | Thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên là **1 tháng lương**.                                                                        | Nhân viên được thưởng Tết tối thiểu 1 tháng lương.                                 | A; A=1,0, B=0,8 | A; A=1,0, B=0,7         | A            | Có        |
|  21 | Một nhân viên Senior có 9 năm thâm niên sẽ được nghỉ tổng cộng **18 ngày phép năm**. Trong đó, 15 ngày phép có lương và 3 ngày phép được cộng thêm do thâm niên. | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | A; A=1,0, B=0,8 | tie; A=1,0, B=0,9       | tie          | Không     |
|  41 | Nhân viên chính thức được hưởng **15 ngày phép năm** có lương.                                                                                                   | Nhân viên được nghỉ 12 ngày phép năm.                                              | A; A=1,0, B=0,0 | A; A=1,0, B=0,2         | A            | Có        |

### Reasoning của hai lượt

|  ID | Reasoning pass 1                                                                                                       | Reasoning pass 2 (ký hiệu theo thứ tự đã hoán đổi)                                                               |
| --: | ---------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
|   1 | B chính xác hơn vì vừa nêu số ngày nghỉ vừa nêu rõ đó là thời gian có lương, phù hợp reference.                        | A chính xác hơn vì nêu rõ ba ngày nghỉ có lương, trong khi B chỉ nêu số ngày.                                    |
|   5 | B đưa ra người phê duyệt cụ thể, còn A không cung cấp thông tin liên quan.                                             | A sai về người phê duyệt; B không hữu ích nhưng không đưa ra thông tin sai so với reference.                     |
|  12 | A chính xác và đầy đủ hơn vì nêu điều kiện nhân viên đã làm việc từ sáu tháng trở lên.                                 | Hai đáp án đều đúng, nhưng B được judge đánh giá rõ ràng hơn vì nhắc lại điều kiện và nhấn mạnh “1 tháng lương”. |
|  21 | Judge cho rằng cả hai đáp án đều đúng về ngày phép và lương, đồng thời đánh giá A chi tiết hơn về nguồn gốc ngày phép. | Judge cho rằng cả hai đáp án đều đúng và đầy đủ về ngày phép, lương; B chi tiết hơn về cách tính phép thâm niên. |
|  41 | A đúng theo chính sách v2024, còn B dùng chính sách cũ nên sai.                                                        | B đúng với 15 ngày phép theo v2024, còn A dùng số ngày không đúng với chính sách hiện hành.                      |

### Phân tích bias

- Position bias: **2/5 = 0,4 (40%)**. Hai trường hợp không nhất quán là ID 5
  và ID 21; cơ chế swap-and-average đã chuyển cả hai thành `tie` thay vì chấp
  nhận một kết quả phụ thuộc thứ tự.
- Verbosity win rate: **3/3 = 1,0 (100%)** trên ba trường hợp có winner dứt
  khoát. Cụ thể, A thắng và dài hơn ở 2 trường hợp (ID 12, 41); B thắng và dài
  hơn ở 1 trường hợp (ID 1).

ID 5 cho thấy lượt đầu chọn B dù B đưa ra người phê duyệt sai; sau khi đảo vị
trí, judge lại ưu tiên câu “Không tìm thấy” vì ít nhất câu này không khẳng định
thông tin sai. ID 21 đáng chú ý hơn: A không nêu khoảng lương nhưng reasoning
lượt đầu vẫn nói cả hai đáp án đều đúng về lương. Đây là lỗi đọc nội dung của
judge, không chỉ là position bias.

Tỷ lệ verbosity 100% là một dấu hiệu cần theo dõi, nhưng chưa đủ để kết luận độ
dài là nguyên nhân khiến câu trả lời thắng. Ở ID 1, phần dài hơn bổ sung chi tiết
“có lương”; ở ID 12 và 41, phần dài hơn cũng chứa điều kiện hoặc thông tin chính
xác hơn. Chỉ có ba winner dứt khoát nên mẫu quá nhỏ để tách ảnh hưởng của độ dài
khỏi ảnh hưởng của chất lượng nội dung.

## Calibration đúng `model_answer`

Helper đã đánh giá đúng `question` và `model_answer` gốc trong
`fixtures/human_labels_10q.json`, sử dụng reference tương ứng. Prompt judge
không nhận `human_label`, `human_note` hay phân bố nhãn người. Nhãn người chỉ
được dùng sau khi judge hoàn tất để tính mức độ đồng thuận.

|  ID | `model_answer` gốc                                                                 | Judge | Lý do của judge                                                                           | Human | Khớp |
| --: | ---------------------------------------------------------------------------------- | ----: | ----------------------------------------------------------------------------------------- | ----: | ---- |
|   1 | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn.                          |     1 | Đúng số ngày nghỉ và phù hợp reference.                                                   |     1 | Có   |
|   5 | Cần Giám đốc phòng ban phê duyệt.                                                  |     0 | Sai vì khoản trên 50 triệu cần Tổng Giám đốc (CEO) phê duyệt.                             |     0 | Có   |
|  12 | Nhân viên được thưởng Tết tối thiểu 1 tháng lương.                                 |     1 | Đúng mức thưởng theo reference cho nhân viên đủ điều kiện.                                |     1 | Có   |
|  21 | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. |     1 | Đúng cả số ngày phép và khoảng lương Senior.                                              |     1 | Có   |
|  23 | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết.                                        |     1 | Đúng số tiền hoàn trả và lý do chưa đủ thời hạn cam kết.                                  |     1 | Có   |
|  29 | Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu.                                |     0 | Thiếu phê duyệt của Kế toán trưởng và tính sai khoản phạt 15 ngày, đúng ra là 80.000 VNĐ. |     0 | Có   |
|  33 | Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng.                                       |     1 | Đúng số ngày phép và tổng phụ cấp hàng tháng.                                             |     1 | Có   |
|  41 | Nhân viên được nghỉ 12 ngày phép năm.                                              |     0 | Dùng chính sách v2023; chính sách v2024 quy định 15 ngày.                                 |     0 | Có   |
|  46 | Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần.  |     1 | Phù hợp reference về chế độ nghỉ của nhân viên thử việc.                                  |     1 | Có   |
|  50 | Được, miễn là đảm bảo kết nối an toàn.                                             |     0 | Sai vì chính sách cấm dùng VPN cá nhân khi WFH.                                           |     0 | Có   |

Kết quả có 10/10 nhãn khớp, do đó observed agreement là:

\[
p_o = \frac{10}{10} = 1{,}0
\]

Cả judge và human có 6 nhãn `1` và 4 nhãn `0`, nên chance agreement là:

\[
p_e = \left(\frac{6}{10}\right)^2 + \left(\frac{4}{10}\right)^2
= 0{,}36 + 0{,}16 = 0{,}52
\]

Vì vậy:

\[
\kappa = \frac{p_o-p_e}{1-p_e}
= \frac{1{,}0-0{,}52}{1-0{,}52}
= 1{,}0
\]

Cohen’s κ = **1,0**, thể hiện mức đồng thuận hoàn hảo trên đúng 10 mẫu
calibration này và vượt ngưỡng bonus `κ > 0,6`. Không có case lệch nhãn với
human trong lần chạy hiện tại.

## Giới hạn và cách dùng judge

Kết quả sử dụng `gpt-4o-mini` với prompt yêu cầu so sánh accuracy,
completeness và conciseness dựa trên reference, đồng thời yêu cầu JSON có
winner, reasoning và scores. Tuy nhiên, năm cặp pairwise và mười mẫu calibration
là tập rất nhỏ; κ = 1,0 chỉ mô tả sự đồng thuận trên tập này, không chứng minh
judge luôn đúng hoặc không có bias trên dữ liệu mới.

Hai kết quả đổi theo vị trí và lỗi reasoning ở ID 21 cho thấy cần giữ
swap-and-average, kiểm tra thủ công các `tie`, và đối chiếu trực tiếp candidate
với reference. Tỷ lệ verbosity cũng cần được theo dõi trên tập lớn hơn, với các
cặp được kiểm soát sao cho nội dung tương đương nhưng độ dài khác nhau.

Trong sử dụng thực tế, judge nên là một tín hiệu đánh giá có giám sát, không phải
đáp án tuyệt đối. Nên version hóa model/prompt, lưu cả hai lượt và scores, chạy
calibration định kỳ trên nhãn người, cảnh báo khi κ giảm hoặc position bias tăng,
và yêu cầu human review đối với các trường hợp không nhất quán hoặc có reasoning
không bám sát nội dung.
