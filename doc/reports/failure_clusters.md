# Phân tích lỗi Phase A

Nhóm: K4-Track-3A-EvalGuard

Người phụ trách: Nguyễn Đỗ Chiến Thắng - 2A202602442

Nguồn: `artifacts/ragas_50q.json`; run timestamp: 2026-10-12T05:42:19.204993+00:00.
Generation mode/fallback và điều kiện chạy: Chạy hoàn toàn trên chế độ LLM (generation_mode: "llm"), không sử dụng extractive fallback; mô hình sinh câu trả lời là deepseek-flash, mô hình thẩm định RAGAS là deepseek-chat qua OpenAI-compatible API.
Models generation/evaluator: generation: ['deepseek-flash'], evaluator: ['deepseek-chat'].

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
|---|---|---|---|
| faithfulness | 0.9500 | 0.7750 | 0.7000 |
| answer_relevancy | 0.9000 | 0.6925 | 0.5700 |
| context_precision | 0.6115 | 0.6145 | 0.5380 |
| context_recall | 0.8525 | 0.6525 | 0.7050 |
| avg_score | 0.8285 | 0.6836 | 0.6283 |

## Bottom 10 và nguyên nhân

| Rank | ID | Question | Distribution | Avg Score | Worst Metric | Diagnosis | Suggested Fix |
|---|---|---|---|---|---|---|---|
| 1 | 41 | Nhân viên được nghỉ bao nhiêu ngày phép năm? | adversarial | 0.0750 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 2 | 27 | Nhân viên có thâm niên 7 năm theo v2024 được nghỉ bao nhiêu ngày phép? Nếu bị trừ thêm 4 ngày ốm không có giấy y tế thì còn lại bao nhiêu? | multi_hop | 0.1250 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 3 | 49 | Theo chính sách nghỉ phép cũ (v2023), nhân viên được nghỉ bao nhiêu ngày? Còn chính sách nào đang có hiệu lực hiện tại? | adversarial | 0.1250 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 4 | 22 | Nếu cần mua một chiếc laptop 30 triệu cho nhân viên mới, ai phê duyệt và cần gì từ phòng CNTT? | multi_hop | 0.1750 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 5 | 25 | Lương thử việc của nhân viên Junior mức cao nhất là bao nhiêu? | multi_hop | 0.2500 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 6 | 33 | Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp hàng tháng và số ngày phép năm theo v2024 là bao nhiêu? | multi_hop | 0.2500 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 7 | 48 | Nhân viên thử việc có được hưởng bảo hiểm sức khỏe PVI không? | adversarial | 0.3000 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 8 | 5 | Muốn mua thiết bị trị giá 55 triệu cần ai phê duyệt? | factual | 0.3250 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 9 | 50 | Nhân viên Manager có thể dùng VPN cá nhân (như NordVPN) khi WFH để tăng bảo mật thêm không? | adversarial | 0.4575 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 10 | 40 | Nhân viên cấp Manager có thời hạn thử việc 90 ngày, đang trong tháng thứ 3, phát hiện vi phạm bảo mật. Họ nên và không nên làm gì theo chính sách? | multi_hop | 0.5000 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |

### Phân tích chi tiết các câu tiêu biểu:
- **Câu ID 41 (Adversarial, rank 1, avg=0.0750, worst=faithfulness):** Câu hỏi bẫy không chỉ rõ phiên bản quy chế (trong corpus có cả nghi_phep_nam_v1.md quy định 12 ngày và nghi_phep_nam_v2.md quy định 14 ngày). Hệ thống trích xuất cả 2 văn bản nhưng LLM chỉ chọn một con số mà không phân biệt rõ quy chế hiện hành, dẫn đến điểm faithfulness bị trừ nặng vì thiếu căn cứ xác đáng giữa 2 phiên bản xung đột.
- **Câu ID 49 (Adversarial, rank 3, avg=0.1250, worst=faithfulness):** Câu hỏi hỏi về phiên bản cũ (v2023) và yêu cầu đối chiếu với phiên bản hiện tại. Khi retrieval lấy cả văn bản cũ và mới, LLM bị nhầm lẫn giữa hiệu lực của 2 văn bản, sinh ra câu trả lời không tách bạch rõ ràng giữa quy định đã hết hiệu lực và quy định đang áp dụng.
- **Câu ID 27 (Multi-hop, rank 2, avg=0.1250, worst=faithfulness):** Đòi hỏi kết hợp giữa quy định phép năm theo thâm niên (nghi_phep_nam_v2.md) và quy định trừ phép khi nghỉ ốm không phép (nghi_om.md). Mặc dù trích xuất được tài liệu, LLM gặp khó khăn trong việc tính toán số học trừ ngày và suy luận nhiều bước, dẫn đến câu trả lời đưa ra số ngày không có trong context.
- **Câu ID 5 (Factual, rank 8, avg=0.3250, worst=answer_relevancy):** Mức chi phí 55 triệu thuộc ngưỡng phê duyệt đặc biệt của Ban Giám đốc trong mua_sam.md. Tuy nhiên, câu trả lời sinh ra lại tập trung liệt kê quy trình mua sắm thay vì trả lời trực diện vào đối tượng có thẩm quyền phê duyệt, khiến điểm answer_relevancy bị kéo xuống thấp.

## Matrix và nhóm yếu nhất

| Metric | factual | multi_hop | adversarial |
|---|---|---|---|
| faithfulness | 1 | 5 | 3 |
| answer_relevancy | 1 | 1 | 2 |
| context_precision | 15 | 7 | 5 |
| context_recall | 3 | 7 | 0 |

Nhóm yếu theo mean thấp nhất: adversarial; mean: 0.6283.
Worst metric xuất hiện nhiều nhất: context_precision; số câu: 27.

### Giải thích nguyên nhân & Đề xuất cải tiến:
- **Tại sao adversarial là nhóm yếu nhất:** Nhóm adversarial có điểm trung bình thấp nhất (0.6283 so với factual 0.8285) vì tập câu hỏi này chứa các câu hỏi có bẫy phiên bản (mat_khau_v1.md vs mat_khau_v2.md, nghi_phep_nam_v1.md vs nghi_phep_nam_v2.md) và bẫy phủ định. Khi hệ thống retrieval BM25 tìm kiếm theo từ khóa, các từ khóa trong bản cũ và bản mới đều giống nhau, khiến cả 2 bản đều lọt vào top context. LLM không có cơ chế lọc siêu dữ liệu theo trạng thái hiệu lực (metadata: status active vs deprecated) nên dễ bị ảo giác hoặc trả lời sai phiên bản.
- **Tại sao context_precision là điểm yếu phổ biến nhất (27 câu):** Do kích thước chunking cố định và việc lấy top 3 chunks gửi vào context khiến nhiều đoạn văn chứa thông tin ngoại vi không liên quan đến câu hỏi cụ thể lọt vào context.
- **Đề xuất sửa cụ thể:**
  1. Thêm bộ lọc metadata filter theo trường version hoặc effective_date trước khi rerank để loại bỏ tài liệu cũ đã hết hiệu lực.
  2. Bổ sung threshold điểm số cho Reranker: chỉ giữ lại các chunks có cross-encoder score lớn hơn 0.5 để cải thiện context_precision.
  3. Tinh chỉnh system prompt: yêu cầu LLM luôn chỉ rõ phiên bản chính sách đang áp dụng và từ chối khẳng định nếu context có mâu thuẫn giữa các phiên bản.

## Bẫy adversarial và giới hạn

- **Bẫy xung đột phiên bản (Version Conflict) & Phủ định (Negation):** Trong bottom 10 có tới 4/10 câu thuộc nhóm adversarial (ID 41, 49, 48, 50). Điểm trung bình của nhóm adversarial (0.6283) thấp hơn rõ rệt so với factual (0.8285). Điều này phản ánh trung thực rằng pipeline RAG chưa có khả năng tự giải quyết xung đột thời gian (temporal reasoning) khi hai văn bản mâu thuẫn cùng được trả về trong context.
- **Giới hạn thực nghiệm:**
  - Kích thước tập mẫu 50 câu (20/20/10) là bộ mẫu tiêu chuẩn của lab, chưa bao quát toàn bộ các tình huống tấn công phức tạp trong thực tế.
  - Sử dụng mô hình DeepSeek (deepseek-flash và deepseek-chat) với nhiệt độ temperature = 0.0. Toàn bộ 50 câu đều chạy qua LLM thành công, không phải dùng chế độ extractive fallback.
