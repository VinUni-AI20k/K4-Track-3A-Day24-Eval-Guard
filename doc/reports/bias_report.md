# Đánh giá LLM Judge Phase B

Nhóm: LGBTree

Người phụ trách: Hoàng Anh Minh - MSSV: 2A202602566

Nguồn: `artifacts/judge_results.json`; run timestamp: 2026-10-12T09:48:07.947355+00:00.
Models generation/judge: generation: [] (Extractive fallback từ Day 18 RAG); judge: gemini-3.5-flash.

## Năm cặp A/B và hai lượt

Nguồn cố định: A từ `artifacts/answers_50q.json:answer`; B từ `fixtures/human_labels_10q.json:model_answer`; reference từ `fixtures/test_set_50q.json:ground_truth`.
Ids: 1, 5, 12, 21, 41. Không đổi nguồn sau khi xem kết quả judge.

| Question ID | Candidate A | Candidate B | Winner Pass 1 | Winner Pass 2 (đã map về A/B) | Final Winner | Position Consistent | Scores Pass 1 | Scores Pass 2 | Lý do chính |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Trích từ nghi_phep_dac_biet.md (3 ngày phép) | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | B | B | B | True | A: 0.80, B: 0.95 | A: 0.80, B: 0.95 | Candidate B trả lời trực tiếp, tự nhiên và súc tích; Candidate A thừa metadata trích dẫn markdown. |
| 5 | Trích từ mua_sam.md (>50 triệu cần CEO duyệt) | Cần Giám đốc phòng ban phê duyệt. | A | A | A | True | A: 0.95, B: 0.30 | A: 0.95, B: 0.30 | Candidate A trích dẫn chính xác quy định đơn hàng >50 triệu cần Tổng Giám đốc (CEO) duyệt; Candidate B thiếu thẩm quyền CEO. |
| 12 | Trích từ thuong_tet.md (thưởng tối thiểu 1 tháng lương) | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | B | B | B | True | A: 0.85, B: 0.95 | A: 0.85, B: 0.95 | Candidate B nêu đúng và ngắn gọn mức thưởng tối thiểu 1 tháng lương; Candidate A chứa nhiều thông tin trích dẫn không cần thiết. |
| 21 | Trích từ nghi_phep_nam_v2024.md (18 ngày phép) | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | B | B | B | True | A: 0.60, B: 0.95 | A: 0.60, B: 0.95 | Candidate B trả lời trọn vẹn cả 2 vế câu hỏi (18 ngày phép và lương Senior 20-35 triệu); Candidate A chỉ trích dẫn phép năm. |
| 41 | Trích từ nghi_phep_nam_v2024.md (15 ngày phép) | Nhân viên được nghỉ 12 ngày phép năm. | A | A | A | True | A: 0.95, B: 0.20 | A: 0.95, B: 0.20 | Candidate A sử dụng chính sách v2024 hiện hành (15 ngày cơ bản); Candidate B dùng chính sách cũ 2023 đã hết hiệu lực (12 ngày). |

Position bias count/rate: 0 cases / 0.00 (0%).
Verbosity win rate: 0.40 (40%); decisive cases: 5 / 5 cases.

### Phân tích hiện tượng bias và kết quả so sánh

1. **Tính nhất quán vị trí (Position Consistency)**:
   - Toàn bộ 5/5 cặp câu hỏi đều đạt `position_consistent = True`. Kết quả giữa Pass 1 `(A, B)` và Pass 2 `(B, A)` sau khi ánh xạ ngược về không gian gốc đều trùng khớp tuyệt đối (`winner_pass1 == winner_pass2`).
   - Điều này chứng minh phương pháp **Swap-and-Average** hoạt động hiệu quả trong việc khử bỏ ưu tiên vị trí đầu (first-position bias) của LLM judge, đảm bảo kết quả phản ánh thực chất chất lượng câu trả lời thay vì thứ tự xuất hiện.

2. **Thiên lệch độ dài (Verbosity Bias)**:
   - Thống kê ghi nhận 2/5 trường hợp câu trả lời dài hơn giành chiến thắng (`a_wins_a_longer = 2`), tỷ lệ verbosity win rate là 40% (ngưỡng an toàn < 60%).
   - Cả 2 trường hợp câu dài hơn thắng đều rơi vào Candidate A (các câu hỏi 5 và 41):
     - Tại câu 5: Candidate A dài hơn do trích dẫn đầy đủ điều kiện quy định thẩm quyền của CEO cho đơn hàng trên 50 triệu, trong khi Candidate B ngắn hơn nhưng sai phạm quy trình nghiêm trọng (chỉ nêu Giám đốc phòng ban).
     - Tại câu 41: Candidate A nêu rõ văn bản quy định phiên bản 2024 với 15 ngày phép, trong khi Candidate B ngắn gọn nhưng trích dẫn phiên bản 2023 đã hết hiệu lực (12 ngày).
   - Ở chiều ngược lại, tại câu 1 và câu 12, Candidate B ngắn gọn hơn rõ rệt nhưng vẫn chiến thắng vì trả lời súc tích, tự nhiên, không bị rườm rà metadata như câu trích đoạn nguyên văn của Candidate A.
   - **Kết luận**: Hiện tượng câu dài hơn thắng ở 2 case trên là dấu hiệu thống kê hợp lý xuất phát từ tính đầy đủ và tính chính xác của dữ kiện chính sách, không phải do LLM bị thiên lệch độ dài một cách vô căn cứ.

## Calibration đúng model_answer

Helper đánh giá đúng question/model_answer đang có trong `fixtures/human_labels_10q.json`; không lấy answer mới của pipeline. Prompt chỉ nhận question, answer, reference. Không gửi human_label, human_note hoặc phân bố nhãn human vào prompt.

| Question ID | Model Answer gốc | Ground Truth tham chiếu | Nhãn Judge (0/1) | Nhãn Human (0/1) | Agree? | Lý do đánh giá của Judge |
|---|---|---|---|---|---|---|
| 1 | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn, không trừ vào phép năm. | 1 | 1 | True | Chính xác theo chính sách nghỉ kết hôn 3 ngày làm việc có lương. |
| 5 | Cần Giám đốc phòng ban phê duyệt. | Đơn hàng trên 50.000.000 VNĐ cần Tổng Giám đốc (CEO) phê duyệt. | 0 | 0 | True | Sai thẩm quyền phê duyệt: trên 50 triệu phải do CEO phê duyệt. |
| 12 | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | Nhân viên chính thức có thời gian làm việc từ 6 tháng trở lên được thưởng Tết tối thiểu 1 tháng lương. | 1 | 1 | True | Đúng mức thưởng Tết tối thiểu 1 tháng lương cho nhân viên từ 6 tháng trở lên. |
| 21 | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | Theo chính sách v2024: 15 ngày cơ bản + 3 ngày thâm niên = 18 ngày phép. Lương Senior từ 20-35 triệu VNĐ/tháng. | 1 | 1 | True | Tính đúng 18 ngày phép và nêu chuẩn khung lương Senior 20-35 triệu. |
| 23 | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | Nghỉ việc dưới 12 tháng hoàn trả 100% chi phí tài trợ đào tạo (25 triệu VNĐ). | 1 | 1 | True | Đúng tỷ lệ hoàn trả 100% (25 triệu) do làm việc dưới 12 tháng sau khóa học. |
| 29 | Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu. | Tạm ứng 8 triệu cần Trưởng phòng và Kế toán trưởng duyệt; phạt pro-rata quá hạn 15 ngày = 80.000 VNĐ. | 0 | 0 | True | Thiếu phê duyệt của Kế toán trưởng và chưa tính đúng mức phạt pro-rata quá hạn. |
| 33 | Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng. | Phép: 19 ngày (15 cơ bản + 4 thâm niên); phụ cấp trách nhiệm Manager: 1.500.000 VNĐ/tháng. | 1 | 1 | True | Đúng số ngày phép (19 ngày) và phụ cấp chức vụ Manager 1.500.000 VNĐ. |
| 41 | Nhân viên được nghỉ 12 ngày phép năm. | Theo v2024 hiện hành: 15 ngày cơ bản. Chính sách v2023 cũ (đã thay thế) là 12 ngày. | 0 | 0 | True | Dùng số ngày của phiên bản 2023 cũ đã bị thay thế bởi phiên bản 2024. |
| 46 | Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần. | Thử việc không được nghỉ phép năm hưởng lương; nếu nghỉ việc riêng phải xin nghỉ không lương. | 1 | 1 | True | Đúng quy định nhân viên thử việc không có phép năm và phải xin nghỉ không lương. |
| 50 | Được, miễn là đảm bảo kết nối an toàn. | Nghiêm cấm dùng VPN cá nhân (NordVPN); bắt buộc dùng VPN WireGuard nội bộ công ty. | 0 | 0 | True | Sai quy định an toàn thông tin: VPN cá nhân bị cấm, bắt buộc dùng VPN công ty. |

Cohen’s κ: 1.00.

Observed/chance agreement và diễn giải:
- **Tỷ lệ đồng thuận quan sát ($p_o$)**: 10/10 trường hợp trùng khớp hoàn toàn giữa LLM Judge và Human Label, do đó $p_o = 1.00$.
- **Tỷ lệ đồng thuận ngẫu nhiên ($p_e$)**:
  - Phân bố nhãn của Judge: 6 nhãn 1 (chấp nhận), 4 nhãn 0 (từ chối).
  - Phân bố nhãn của Human: 6 nhãn 1 (chấp nhận), 4 nhãn 0 (từ chối).
  - Công thức tính: $p_e = \frac{6 \times 6 + 4 \times 4}{10 \times 10} = \frac{36 + 16}{100} = 0.52$.
- **Hệ số Cohen's $\kappa$**:
  $$\kappa = \frac{p_o - p_e}{1 - p_e} = \frac{1.00 - 0.52}{1.00 - 0.52} = 1.00$$
- **Nhận xét**: Theo thang đo Landis-Koch, $\kappa = 1.00$ thuộc mức **Almost Perfect Agreement** (Đồng thuận hoàn hảo). LLM Judge phân biệt rất tốt giữa câu trả lời đúng, đầy đủ với các câu trả lời sai thẩm quyền, thiếu điều kiện phạt hoặc sử dụng tài liệu hết hạn.

## Giới hạn và cách dùng judge

1. **Hạn chế về quy mô mẫu và mô hình**:
   - Thử nghiệm hiệu chuẩn được thực hiện trên tập mẫu nhỏ (5 cặp pairwise và 10 mẫu nhãn nhị phân), do đó hệ số $\kappa = 1.00$ là bằng chứng tốt trên tập test kiểm chuẩn nhưng chưa bao quát được toàn bộ phân bố câu hỏi phong phú trong thực tế production.
   - LLM Judge sử dụng model `gemini-3.5-flash` với prompt đánh giá 3 tiêu chí cấu trúc JSON. Nếu prompt thay đổi hoặc gặp các ngữ cảnh có tranh chấp tinh vi giữa các phòng ban (ambiguous policies), judge vẫn có nguy cơ đưa ra phán đoán sai lệch.

2. **Cách kiểm chứng và đối chiếu**:
   - Khi triển khai production, không bao giờ xem LLM Judge là sự thật tuyệt đối (Ground Truth). Judge chỉ đóng vai trò là tầng **tự động hóa sàng lọc (automated screening gate)** trong CI/CD.
   - Các trường hợp judge cho điểm thấp hoặc không nhất quán sau 2 lượt swap-and-average (`final_winner == "tie"`, điểm số chênh lệch < 0.1) cần được tự động định tuyến về hàng đợi kiểm duyệt của con người (Human-in-the-Loop review).
   - Định kỳ lấy mẫu ngẫu nhiên từ 5% đến 10% kết quả chấm của LLM Judge để chuyên gia nhân sự/chính sách gán nhãn mù (blind labeling) nhằm phát hiện sớm hiện tượng suy giảm chất lượng (judge drift).
