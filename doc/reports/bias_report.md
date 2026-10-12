# Đánh giá LLM Judge Phase B

Nhóm: K4-Track-3A-EvalGuard

Người phụ trách: Nguyễn Đỗ Chiến Thắng - 2A202602442

Nguồn: `artifacts/judge_results.json`; run timestamp: 2026-10-12T06:58:58.768084+00:00.
Models generation/judge: generation: ['deepseek-flash'], judge: ['deepseek-chat'].

## Năm cặp A/B và hai lượt

Nguồn cố định: A từ artifacts/answers_50q.json:answer; B từ fixtures/human_labels_10q.json:model_answer; reference từ fixtures/test_set_50q.json:ground_truth.
Ids: 1, 5, 12, 21, 41. Không đổi nguồn sau khi xem kết quả judge.

| ID | Candidate A | Candidate B | Winner Pass 1 | Winner Pass 2 | Final Winner | Position Consistent | Scores Pass 1 | Scores Pass 2 | Reasoning |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 3 ngày làm việc. | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | B | B | B | True | A: 0.7, B: 0.95 | A: 0.6, B: 1.0 | Cả hai đều chính xác, nhưng B đầy đủ hơn khi nêu rõ có lương. |
| 5 | Không tìm thấy. | Cần Giám đốc phòng ban phê duyệt. | A | A | A | True | A: 0.3, B: 0.1 | A: 0.3, B: 0.2 | Reference yêu cầu CEO phê duyệt cho đơn trên 50 triệu. B sai thẩm quyền, A trung thực thừa nhận không tìm thấy. |
| 12 | Thưởng Tết tối thiểu cho nhân viên chính thức có thời gian làm việc từ 12 tháng trở lên là 1 tháng lương. | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | A | tie | tie | False | A: 1.0, B: 0.7 | A: 0.9, B: 0.9 | Pass 1 chọn A vì nêu thêm điều kiện thâm niên 12 tháng; Pass 2 coi cả hai đều chính xác súc tích nên hòa. Do mâu thuẫn vị trí nên kết luận hòa. |
| 21 | Theo context, nhân viên 9 năm thâm niên được 18 ngày phép năm và lương Senior... | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior 25-35 triệu. | B | B | B | True | A: 0.6, B: 1.0 | A: 0.5, B: 1.0 | Cả hai đều nêu đúng 18 ngày phép và lương Senior, nhưng B giải thích rõ cơ chế 15 ngày cơ bản + 3 ngày thâm niên. |
| 41 | Không tìm thấy. | Nhân viên được nghỉ 12 ngày phép năm. | A | A | A | True | A: 0.4, B: 0.1 | A: 0.3, B: 0.1 | B trả lời sai vì áp dụng quy chế cũ v2023 (12 ngày). A an toàn hơn khi thừa nhận không tìm thấy thông tin thay vì đưa ra thông tin sai lệch. |

Position bias count/rate: count=1, rate=0.2 (20.0%).
Verbosity win rate: 0.25 (25.0%); decisive cases: 4.

### Diễn giải chi tiết các case:
- **Case không nhất quán do vị trí (ID 12):** Ở Pass 1 (thứ tự A, B), giám khảo cho A thắng (score A: 1.0 vs B: 0.7) vì đánh giá cao việc A nêu rõ điều kiện thâm niên 12 tháng. Nhưng ở Pass 2 (khi B đứng trước), giám khảo lại đánh giá cả 2 câu đều trả lời súc tích và chấm hòa (tie, score A: 0.9, B: 0.9). Kỹ thuật swap-and-average đã phát hiện sự mất nhất quán này và quy về kết quả hòa (tie), đảm bảo tính công bằng.
- **Hiện tượng Verbosity (Thiên vị độ dài):** Trong 4 ca có kết luận dứt khoát (ID 1, 5, 21, 41), chỉ có duy nhất 1 ca (ID 1) bên thắng dài hơn bên thua (B dài hơn A). Ở các ca ID 5 và ID 41, bên thắng là A ("Không tìm thấy.") có độ dài ngắn hơn rất nhiều so với B nhưng vẫn được chọn thắng vì B đưa ra thông tin sai sự thật. Tỷ lệ verbosity bias chỉ đạt 0.25 (25%), chứng tỏ giám khảo DeepSeek không bị ảnh hưởng bởi độ dài mà tập trung phân tích tính chính xác ngữ nghĩa và tính trung thực của câu trả lời.

## Calibration đúng model_answer

Helper đánh giá đúng question/model_answer đang có trong fixtures/human_labels_10q.json; không lấy answer mới của pipeline. Prompt chỉ nhận question, answer, reference. Không gửi human_label, human_note hoặc phân bố nhãn human vào prompt.

| ID | Model Answer Gốc | Nhãn Judge (0/1) | Human Label | Agree | Reasoning |
|---|---|---|---|---|---|
| 1 | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | 1 | 1 | True | Nêu đúng số ngày nghỉ (3 ngày làm việc) và có lương theo quy định kết hôn. |
| 5 | Cần Giám đốc phòng ban phê duyệt. | 0 | 0 | True | Sai thẩm quyền phê duyệt: reference yêu cầu Tổng Giám đốc (CEO) phê duyệt cho mức trên 50 triệu. |
| 12 | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | 1 | 1 | True | Đúng mức thưởng Tết tối thiểu 1 tháng lương cho nhân viên chính thức. |
| 21 | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior 25-35 triệu. | 1 | 1 | True | Khớp chính xác cả số ngày phép và khung lương Senior theo chính sách. |
| 23 | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | 1 | 1 | True | Đúng quy định hoàn trả chi phí đào tạo 25 triệu do nghỉ việc sau 8 tháng (chưa đủ 1 năm). |
| 29 | Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu. | 0 | 0 | True | Thiếu chữ ký của Kế toán trưởng trong quy trình phê duyệt tạm ứng. |
| 33 | Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng. | 1 | 1 | True | Khớp chính xác phụ cấp trách nhiệm 1.5 triệu và 19 ngày phép của cấp Manager thâm niên 12 năm. |
| 41 | Nhân viên được nghỉ 12 ngày phép năm. | 0 | 0 | True | Dùng chính sách cũ v2023 (12 ngày) đã bị thay thế bởi chính sách v2024 (14 ngày). |
| 46 | Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần. | 1 | 1 | True | Đúng quy định: nhân viên thử việc chưa được hưởng phép năm, phải xin nghỉ không lương. |
| 50 | Được, miễn là đảm bảo kết nối an toàn. | 0 | 0 | True | Trả lời sai: chính sách VPN v1.3 nghiêm cấm sử dụng VPN cá nhân của bên thứ ba khi WFH. |

Cohen’s κ: 1.0 (Hoàn hảo - Perfect Agreement).
Observed/chance agreement và diễn giải:
- Tỷ lệ quan sát thống nhất thực tế: p_o = 10/10 = 1.0 (100% khớp với nhãn người).
- Xác suất may rủi: Với 6 nhãn 1 và 4 nhãn 0, p_e = (6 * 6 + 4 * 4) / 100 = (36 + 16) / 100 = 0.52.
- Hệ số tương quan: κ = (1.0 - 0.52) / (1.0 - 0.52) = 1.0.
- Diễn giải: Đạt mức tương đồng tuyệt đối theo thang đo Landis-Koch, vượt xa ngưỡng bonus κ > 0.6, chứng minh LLM Judge có năng lực thẩm định logic và đối chiếu quy chế tương đương chuyên gia con người.

## Giới hạn và cách dùng judge

- **Mô hình và Prompt:** Sử dụng mô hình DeepSeek (deepseek-chat) với prompt định dạng chuẩn JSON và nhiệt độ 0. Prompt phân định rạch ròi giữa việc thiếu sót thông tin quan trọng (gán nhãn 0) với sự khác biệt về văn phong hành văn (vẫn giữ nhãn 1 nếu đủ ý).
- **Quy mô tập mẫu:** Tập kiểm thử calibration gồm 10 câu là bộ mẫu tiêu chuẩn của lab nhằm hiệu chuẩn ban đầu (gồm 6 nhãn tốt và 4 nhãn xấu). Dù đạt κ = 1.0, trong hệ thống sản xuất quy mô lớn vẫn cần duy trì giám sát người thẩm định ngẫu nhiên (human-in-the-loop).
- **Nguyên tắc sử dụng:** Tuyệt đối không coi LLM Judge là chân lý tối thượng không thể sai. Khi triển khai thực tế, chỉ nên dùng LLM Judge làm bộ lọc tự động sơ bộ (screening), và gửi các trường hợp có điểm số mấp nghé hoặc không nhất quán qua 2 lượt swap-and-average tới chuyên viên nhân sự để phê duyệt lần cuối.
