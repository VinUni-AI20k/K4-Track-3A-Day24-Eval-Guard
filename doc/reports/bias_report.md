# Đánh giá LLM Judge Phase B

Nhóm: Latentia

Người phụ trách: Nguyễn Minh Thắng - 2A202602706

Nguồn: `artifacts/judge_results.json`; run timestamp: 2026-10-12T06:04:19.763969+00:00.
Models generation/judge: gpt-4o-mini-2024-07-18 và gpt-4o-mini.

## Năm cặp A/B và hai lượt

Nguồn cố định: A từ artifacts/answers_50q.json:answer; B từ
fixtures/human_labels_10q.json:model_answer; reference từ fixtures/test_set_50q.json:ground_truth.
Ids: 1, 5, 12, 21, 41. Không đổi nguồn sau khi xem kết quả judge.

| ID | Candidate A | Candidate B | Pass 1 | Pass 2 (quy về A/B) | Final Winner | Nhất quán vị trí | Điểm Pass 1 (A/B) | Điểm Pass 2 (A/B) |
|---|---|---|---|---|---|---|---|---|
| 1 | Không tìm thấy. | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | B | B | B | True | 0.0 / 1.0 | 0.0 / 1.0 |
| 5 | Cần phê duyệt của Giám đốc điều hành (CEO). | Cần Giám đốc phòng ban phê duyệt. | A | A | A | True | 1.0 / 0.0 | 1.0 / 0.0 |
| 12 | Thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên là **1 tháng lương**. | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | A | A | A | True | 1.0 / 0.8 | 1.0 / 0.8 |
| 21 | Không tìm thấy. | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | B | B | B | True | 0.0 / 1.0 | 0.0 / 1.0 |
| 41 | Không tìm thấy. | Nhân viên được nghỉ 12 ngày phép năm. | A | B | tie | False | 0.3 / 0.0 | 0.0 / 0.4 |

Position bias count/rate: 1/5 (20.0%).
Verbosity win rate: 1.0 (100.0%); decisive cases: 4/5.

### Phân tích chi tiết các trường hợp

1. **Về tính nhất quán vị trí (Position Consistency):**
   - 4/5 cặp (IDs 1, 5, 12, 21) đạt đồng thuận tuyệt đối ở cả 2 lượt đánh giá bất kể thứ tự trình bày.
   - Trường hợp ID 41 xuất hiện bất đồng vị trí (Pass 1 chọn A, Pass 2 chọn B khi hoán đổi vị trí). Nguyên nhân không đơn thuần do vị trí đứng trước mà do bản chất câu hỏi mang tính xung đột phiên bản chính sách: Candidate A thừa nhận không tìm thấy câu trả lời, trong khi Candidate B đưa ra con số 12 ngày của phiên bản cũ v2023 (đã bị bãi bỏ bởi v2024 quy định 15 ngày). Ở lượt 1, LLM judge phạt nặng lỗi thông tin sai lệch của B và ưu tiên A thà từ chối còn hơn bịa đặt. Ở lượt 2 khi B được đổi lên vị trí trước, LLM lại đánh giá cao việc có đưa ra con số cụ thể hơn là từ chối. Cơ chế **swap-and-average** đã phát huy tác dụng chính xác khi chuyển kết quả thành `tie`, tránh thiên vị một chiều.

2. **Về xu hướng thiên vị độ dài (Verbosity Bias):**
   - Trong 4 trường hợp có kết quả dứt khoát (decisive), 100% người chiến thắng có độ dài câu trả lời dài hơn đối thủ (A thắng ở IDs 5, 12 với độ dài lớn hơn B; B thắng ở IDs 1, 21 với độ dài lớn hơn A).
   - Tuy nhiên, đây chủ yếu là **hệ quả tự nhiên của nội dung** chứ không phải bias tiêu cực thuần túy: ở ID 1 và ID 21, câu trả lời ngắn là "Không tìm thấy." (16 ký tự) do RAG retrieval trượt, trong khi câu trả lời dài cung cấp đầy đủ thông tin chính sách có giá trị thực tế. Ở ID 5 và 12, câu trả lời dài hơn có cấu trúc giải thích và trích dẫn chuẩn chỉ theo quy định.

## Calibration đúng model_answer

Helper đánh giá đúng question/model_answer đang có trong fixtures/human_labels_10q.json;
không lấy answer mới của pipeline. Prompt chỉ nhận question, answer, reference.
Không gửi human_label, human_note hoặc phân bố nhãn human vào prompt.

| QID | Model Answer gốc | LLM Label | Human Label | Đồng thuận | Lý do đánh giá của LLM Judge |
|---|---|---|---|---|---|
| 1 | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | 1 | 1 | True | Câu trả lời chính xác theo tài liệu tham khảo, nêu rõ 3 ngày có lương và điều kiện không trừ phép năm. |
| 5 | Cần Giám đốc phòng ban phê duyệt. | 0 | 0 | True | Câu trả lời sai vì tài sản 55 triệu vượt ngưỡng phòng ban, thẩm quyền thuộc Tổng Giám đốc (CEO). |
| 12 | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | 1 | 1 | True | Chính xác theo reference, đáp ứng đủ điều kiện thâm niên từ 6 tháng trở lên cho nhân viên chính thức. |
| 21 | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | 1 | 1 | True | Chính xác đầy đủ cả số ngày phép kết hợp thâm niên lẫn khung lương chức danh Senior. |
| 23 | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | 1 | 1 | True | Đúng theo điều khoản hoàn trả 100% kinh phí đào tạo khi nghỉ việc trước hạn cam kết 1 năm. |
| 29 | Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu. | 0 | 0 | True | Sai vì thiếu phê duyệt của Kế toán trưởng và cách tính phí phạt quá hạn 15 ngày không đúng quy định. |
| 33 | Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng. | 1 | 1 | True | Cung cấp chính xác tổng số ngày phép năm theo thâm niên và các khoản phụ cấp của Manager. |
| 41 | Nhân viên được nghỉ 12 ngày phép năm. | 0 | 0 | True | Sai nghiêm trọng do dùng số liệu chính sách cũ v2023 thay vì 15 ngày theo chính sách hiện hành v2024. |
| 46 | Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần. | 1 | 1 | True | Đúng theo quy định nhân viên thử việc chưa được tích lũy phép năm và quy trình xin nghỉ không lương. |
| 50 | Được, miễn là đảm bảo kết nối an toàn. | 0 | 0 | True | Sai vì chính sách bảo mật mạng nghiêm cấm sử dụng VPN thương mại cá nhân để truy cập tài nguyên nội bộ. |

Cohen’s κ: 1.0.
Observed/chance agreement và diễn giải:
- Tỷ lệ đồng thuận quan sát được: $P_o = 10/10 = 1.0$ (100%).
- Tỷ lệ đồng thuận ngẫu nhiên kỳ vọng: $P_e = (6/10 \times 6/10) + (4/10 \times 4/10) = 0.36 + 0.16 = 0.52$.
- Hệ số Cohen's $\kappa = \frac{P_o - P_e}{1 - P_e} = \frac{1.0 - 0.52}{1 - 0.52} = 1.0$.
- Theo thang đo chuẩn Landis & Koch, $\kappa = 1.0$ thể hiện sự tương thích hoàn hảo (Almost Perfect / Perfect Agreement) giữa quyết định của LLM Judge và chuyên gia con người.

## Giới hạn và cách dùng judge

1. **Giới hạn kích thước mẫu:**
   - Bộ đánh giá calibration chỉ gồm 10 mẫu nhãn người và 5 cặp so sánh pairwise. Dù đạt $\kappa = 1.0$, mẫu thử nhỏ này chưa bao quát hết mọi khía cạnh góc cạnh (edge cases) và bẫy suy luận phức tạp trong toàn bộ corpus.
   - Khi triển khai production, cần mở rộng ngân hàng câu hỏi calibration lên tối thiểu 100–200 mẫu được gán nhãn đa chuyên gia.

2. **Cách sử dụng LLM Judge trong quy trình thực tế:**
   - **Không xem LLM Judge là chân lý tuyệt đối:** LLM Judge vẫn có thể mắc lỗi hallucination khi đọc reference quá dài hoặc bị lừa bởi phong cách hành văn tự tin. Cần luôn đối chiếu với ground-truth và chỉ định human-in-the-loop cho các trường hợp điểm số cận biên (borderline) hoặc bất đồng vị trí.
   - **Bắt buộc áp dụng Swap-and-Average:** Trong mọi tác vụ A/B testing tự động, cơ chế hoán đổi vị trí là bắt buộc để triệt tiêu position bias và phát hiện các trường hợp bấp bênh cần can thiệp thủ công.
   - **Prompting nghiêm ngặt:** Luôn sử dụng JSON schema mode có temperature=0, cô lập ngữ cảnh đánh giá, không nhúng nhãn lịch sử hoặc giả định xác suất vào prompt.
