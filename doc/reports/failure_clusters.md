# Phân tích lỗi Phase A

Nhóm: Vision

Người phụ trách: Võ Huy Hoàng-2A202602548

Nguồn: `artifacts/ragas_50q.json`; run timestamp: `2026-10-12T11:23:59.175669+00:00`.
Chạy Phase A trên 50 answers đã lưu; mỗi answer có 3 contexts. Cả 50 answers có `generation_mode=llm`, không có `extractive_fallback`. Có 18 câu trả lời nguyên văn “Không tìm thấy.” và 1 câu (ID 44) trả lời biến thể không dấu “Khong tim thay.”. Tính cả hai kiểu từ chối, tổng là **19/50**: factual 5/20, multi_hop 11/20, adversarial 3/10.
Models theo metadata: generation `gpt-5-nano-2025-08-07`; evaluator `gpt-5-nano` và `text-embedding-3-small`. Đây là ID do report ghi nhận, không phải bằng chứng alias provider đã giải quyết thành snapshot cụ thể.

## Điểm theo distribution

Các điểm lấy từ `per_distribution`, làm tròn 4 chữ số thập phân.

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
|---|---:|---:|---:|
| faithfulness | 0.6583 | 0.3489 | 0.6833 |
| answer_relevancy | 0.7194 | 0.5540 | 0.6409 |
| context_precision | 0.8583 | 0.6708 | 0.8583 |
| context_recall | 0.6750 | 0.5958 | 0.5917 |
| avg_score | 0.7278 | 0.5424 | 0.6936 |

## Bottom 10 và nguyên nhân

Bảng giữ nguyên `rank`, `question_id`, `distribution`, `question`, `worst_metric`, `diagnosis` và `suggested_fix` của `bottom_10` trong JSON; chỉ `avg_score` được làm tròn khi hiển thị.

| Rank | ID | Distribution | Question | Avg score | Worst metric | Diagnosis (Task 3) | Suggested fix (Task 3) |
|---:|---:|---|---|---:|---|---|---|
| 1 | 5 | factual | Muốn mua thiết bị trị giá 55 triệu cần ai phê duyệt? | 0.1019 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 2 | 33 | multi_hop | Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp hàng tháng và số ngày phép năm theo v2024 là bao nhiêu? | 0.1102 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 3 | 41 | adversarial | Nhân viên được nghỉ bao nhiêu ngày phép năm? | 0.3125 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 4 | 26 | multi_hop | Nhân viên vừa kết hôn và cùng tuần đó có con kết hôn. Tổng số ngày nghỉ đặc biệt có lương là bao nhiêu? | 0.3304 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 5 | 9 | factual | Nam nhân viên được nghỉ bao nhiêu ngày khi vợ sinh con? | 0.3537 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 6 | 8 | factual | Nhân viên được nghỉ bao nhiêu ngày khi cha hoặc mẹ mất? | 0.3669 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 7 | 25 | multi_hop | Lương thử việc của nhân viên Junior mức cao nhất là bao nhiêu? | 0.3700 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 8 | 21 | multi_hop | Một nhân viên Senior có 9 năm thâm niên được nghỉ bao nhiêu ngày phép năm và lương trong khoảng nào? | 0.3717 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 9 | 19 | factual | Thời gian thử việc tiêu chuẩn và tối đa (dành cho Manager trở lên) là bao nhiêu ngày? | 0.3723 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 10 | 30 | multi_hop | So sánh quyền lợi bảo hiểm giữa nhân viên thử việc và nhân viên chính thức. | 0.4068 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |

`diagnosis` và `suggested_fix` ở trên là nhãn tự động của Task 3, không phải nguyên nhân đã được xác minh. Trong 10 câu này, 9 câu trả lời “Không tìm thấy.”: đó là từ chối trả lời, không phải tự bịa một dữ kiện. “Lower temperature” cũng không áp dụng trực tiếp cho `gpt-5-nano`, vốn không nhận `temperature` tùy chỉnh. Phân tích sau dựa trên answer, cả ba contexts và ground_truth của từng câu.

| ID | Đối chiếu dữ liệu và giới hạn kết luận | Việc sửa cần thử |
|---:|---|---|
| 5 | Answer “Không tìm thấy.”; context 1 chỉ chứa hàng **dưới 5 triệu** của `mua_sam.md`, context 2 nói về thiết bị CNTT, context 3 là **tạm ứng**. Hàng **trên 50 triệu → CEO** có trong tài liệu gốc nhưng vắng khỏi ba contexts. | Giữ trọn bảng thẩm quyền hoặc gắn từng hàng với tiêu đề/khoảng tiền khi chunking; truy vấn/rerank theo “55 triệu”, “trên 50 triệu”, “phê duyệt mua sắm” rồi kiểm tra hàng CEO vào top 3. |
| 33 | Answer “Không tìm thấy.”; context 1 có **15 ngày v2024**, context 2 là **12 ngày v2023** đã cũ, context 3 là bảng lương. Không context nào có **phụ cấp ăn trưa 1 triệu**, **điện thoại Manager 500 nghìn** hoặc quy tắc **+1 ngày/3 năm**; reference cần cả ba để ra 1,5 triệu và 19 ngày. | Tách nhánh phụ cấp/phép năm; truy xuất `phu_cap.md` và phần thâm niên của `nghi_phep_nam_v2024.md`, lọc phiên bản hiệu lực trước khi tổng hợp. |
| 41 | Answer “Không tìm thấy.” dù contexts có **v2023: 12 ngày** và **v2024: 15 ngày**, cùng ví dụ 9 năm được 18 ngày. Quy tắc tổng quát **+1 ngày/3 năm** không hiện diện trong ba contexts, nên mới có đủ chứng cứ trực tiếp cho 15 ngày cơ bản. | Ưu tiên văn bản v2024 theo ngày hiệu lực/quan hệ thay thế v2023; lấy thêm đoạn thâm niên v2024 và gắn nguồn cho từng mệnh đề. |
| 26 | Answer “Không tìm thấy.” dù context 1 có **bản thân kết hôn: 3 ngày**, context 2 có **con kết hôn: 1 ngày**; reference cộng thành **4 ngày**. Nhưng tài liệu gốc `nghi_phep_dac_biet.md` còn ghi “Phép đặc biệt không cộng dồn”, tạo điểm cần làm rõ khi hai sự kiện cùng tuần. | Xác nhận cách hiểu “không cộng dồn” với chủ bộ dữ liệu trước khi quy lỗi cho model. Nếu reference 4 ngày là chuẩn, yêu cầu generator cộng hai quyền lợi có chứng cứ và nêu điều kiện. |
| 9 | Answer “Không tìm thấy.”; context 1 nêu **nam giới sinh con: 5 ngày làm việc liên tục**, context 3 nêu nghỉ đặc biệt không trừ phép năm. Thông tin chính đã hiện diện; có dấu hiệu từ chối quá mức ở bước tạo answer, chưa rõ do prompt hay model. | Khi context có mệnh đề khớp trực tiếp, yêu cầu trả lời kèm nguồn; kiểm tra riêng ID 9 sau khi chỉnh prompt, không đưa reference vào prompt. |
| 8 | Answer **“3 ngày làm việc”** khớp số ngày trong context 3 và reference, nhưng thiếu **có lương** và **không trừ phép năm**; context 2 còn nêu điều kiện giấy tờ. `context_recall=0` dù context 3 có “Tang lễ (cha mẹ): 3 ngày”, nên điểm chấm cần kiểm tra thủ công. | Bổ sung context mở đầu chính sách về có lương/không trừ phép năm; kiểm tra lại case này và hướng generator trả lời đủ điều kiện. |
| 25 | Answer “Không tìm thấy.”; context 3 có **Junior tối đa 20 triệu**, contexts 1–2 có **thử việc = 85%**. Hai vế đủ để tính **17 triệu** như reference; `context_precision=0` cũng không phản ánh rõ chứng cứ đang có. | Prompt tổng hợp nhiều nguồn: `20.000.000 × 0,85 = 17.000.000 VNĐ/tháng`, gắn mỗi số với context; xác minh score thủ công trước khi coi là lỗi retrieval. |
| 21 | Answer “Không tìm thấy.”; context 1 có ví dụ **9 năm → 18 ngày**, contexts 2–3 là quy định v2023. Ba contexts **không có dải lương Senior 20–35 triệu**; reference cần cả phép năm lẫn lương. | Tách nhánh phép năm/lương, lấy đúng hàng Senior của `bang_luong_2024.md` và phần v2024, giảm ưu tiên chunk v2023 khi hỏi chính sách hiện hành. |
| 19 | Answer “Không tìm thấy.” dù context 1 có **Manager tối đa 90 ngày** và context 2 có **tiêu chuẩn 60 ngày** từ `thu_viec.md`; reference chỉ cần ghép hai vế. `context_recall=1` phù hợp với việc retrieval đã có chứng cứ. | Prompt yêu cầu trả đủ hai mốc khi mỗi mốc có nguồn; kiểm tra riêng ID 19 có cả 60 và 90 ngày. |
| 30 | Answer “Không tìm thấy.”; context 2 có **thử việc: BHXH bắt buộc, chưa hưởng PVI**, context 3 có **chính thức: PVI**. Contexts không có **hạn mức 200 triệu/năm** hay nguồn rõ cho BHXH của nhân viên chính thức như reference. | Lấy thêm đoạn `bao_hiem_suc_khoe.md` chứa hạn mức/phạm vi, xác minh nguồn BHXH chính thức; phân biệt đúng hai nhóm và giữ phủ định “không PVI” cho thử việc. |

## Matrix và nhóm yếu nhất

Matrix đếm `worst_metric` của **mọi câu**, kể cả câu có điểm tốt; không phải số câu thất bại. Tổng cột bằng kích thước ba nhóm 20/20/10.

| Worst metric | factual | multi_hop | adversarial | Tổng |
|---|---:|---:|---:|---:|
| faithfulness | 8 | 12 | 3 | 23 |
| answer_relevancy | 6 | 2 | 1 | 9 |
| context_precision | 1 | 2 | 0 | 3 |
| context_recall | 5 | 4 | 6 | 15 |
| **Tổng** | **20** | **20** | **10** | **50** |

Nhóm yếu theo **mean `avg_score` thấp nhất**: `multi_hop` = **0.5424** (`factual` = 0.7278; `adversarial` = 0.6936). Metric xuất hiện nhiều nhất với vai trò `worst_metric`: `faithfulness`, **23/50** câu. Trong `multi_hop`, 11/20 answers là “Không tìm thấy.” và 12/20 câu có `faithfulness` thấp nhất trong bốn metric; đây là dấu hiệu cần điều tra, chưa chứng minh quan hệ nhân quả. ID 33 và 21 thiếu ít nhất một nhánh chứng cứ; ID 25 và 26 có chứng cứ quan trọng nhưng answer vẫn từ chối.

Ưu tiên cải tiến: (1) bảo toàn hàng bảng và metadata phiên bản khi chunking, truy xuất theo từng nhánh cho câu nhiều ý; (2) trả lời các phần có đủ chứng cứ và nêu rõ phần còn thiếu thay vì “Không tìm thấy.” chung; (3) rerank có xét phiên bản hiện hành. Sau mỗi thay đổi, tạo lượt answers/evaluation mới trên cùng 50 câu, so sánh mean theo nhóm, tỷ lệ từ chối và các ID nêu trên; giữ artifact gốc để đối chiếu. Không chỉnh số trong JSON hoặc sửa reference để tăng điểm.

## Bẫy adversarial và giới hạn

`adversarial` có mean **0.6936**, thấp hơn `factual` **0.7278** khoảng **0.0342**. Ở ID 41, contexts chứa cả v2023 (**12 ngày**) và v2024 (**15 ngày**); answer “Không tìm thấy.” không chọn sai bản cũ nhưng cũng không nêu được chính sách hiện hành. ID 48 là bẫy phủ định: context từ `thu_viec.md` ghi rõ nhân viên thử việc **chưa được hưởng PVI**, trong khi answer vẫn là “Không tìm thấy.” dù reference trả lời **KHÔNG**. Điểm thấp hơn không tự chứng minh pipeline đã nhận diện bẫy phiên bản hay phủ định.

Bộ đánh giá chỉ có 50 câu, trong đó 10 câu adversarial, một lượt sinh answer và một lượt chấm bằng `gpt-5-nano`/`text-embedding-3-small`; chưa có người đối chiếu toàn bộ 50 câu hoặc đo độ ổn định qua nhiều lượt. Điểm tự động có thể bất nhất với chứng cứ hiển thị: ID 8 được `context_recall=0` dù context 3 có số ngày tang lễ; ID 25 được `context_precision=0` dù contexts có 20 triệu và 85%. Cần đọc chứng cứ trước khi dùng score để kết luận lỗi ở retrieval hay generation.
