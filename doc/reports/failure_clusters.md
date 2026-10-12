# Phân tích lỗi Phase A

Nhóm: LGBTree

Người phụ trách: Ngô Tiến Dũng (MSSV: 2A202602374)

Nguồn: `artifacts/ragas_50q.json`; run timestamp: 2026-10-12T09:52:39.902165+00:00.
Generation mode/fallback và điều kiện chạy: extractive_fallback (tài liệu RAG Day 18 trích xuất trực tiếp).
Models generation/evaluator: Evaluator models: gpt-4o-mini, text-embedding-3-small từ m4_eval. Generation model: None (extractive fallback).

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
|---|---|---|---|
| faithfulness | 0.9900 | 0.9875 | 1.0000 |
| answer_relevancy | 0.3953 | 0.3438 | 0.4040 |
| context_precision | 0.9167 | 0.9833 | 0.9583 |
| context_recall | 0.8250 | 0.8042 | 0.6833 |
| avg_score | 0.7817 | 0.7797 | 0.7614 |

## Bottom 10 và nguyên nhân

| Rank | ID | Distribution | Question | Avg Score | Worst Metric | Diagnosis | Suggested Fix |
|---|---|---|---|---|---|---|---|
| 1 | 5 | factual | Muốn mua thiết bị trị giá 55 triệu cần ai phê duyệt? | 0.3340 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |
| 2 | 6 | factual | Thông tin lương thuộc cấp độ phân loại dữ liệu nào? | 0.6370 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 3 | 33 | multi_hop | Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp hàng tháng và số ngày phép năm theo v2024 là bao nhiêu? | 0.6723 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 4 | 44 | adversarial | Bao lâu phải đổi mật khẩu một lần? | 0.6776 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 5 | 21 | multi_hop | Một nhân viên Senior có 9 năm thâm niên được nghỉ bao nhiêu ngày phép năm và lương trong khoảng nào? | 0.6938 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 6 | 7 | factual | Nghỉ phép không lương 20 ngày cần ai phê duyệt? | 0.6943 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 7 | 30 | multi_hop | So sánh quyền lợi bảo hiểm giữa nhân viên thử việc và nhân viên chính thức. | 0.6970 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 8 | 34 | multi_hop | Nhân viên tạm ứng 4 triệu và một nhân viên khác tạm ứng 7 triệu: quy trình phê duyệt khác nhau thế nào? | 0.6988 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 9 | 22 | multi_hop | Nếu cần mua một chiếc laptop 30 triệu cho nhân viên mới, ai phê duyệt và cần gì từ phòng CNTT? | 0.7036 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 10 | 45 | adversarial | Có cần kích hoạt xác thực đa yếu tố (MFA) không? | 0.7057 | answer_relevancy | Answer doesn't match question | Improve prompt template |

### Phân tích chi tiết các câu đại diện cho nhóm lỗi

1. **Lỗi Retrieval / Precision (Câu 5 - Rank 1, factual)**:
   - *Câu hỏi*: "Muốn mua thiết bị trị giá 55 triệu cần ai phê duyệt?"
   - *Nguyên nhân*: Pipeline lấy về chunk chứa hạn mức 20-50 triệu và quy trình mua sắm chung trước khi trích xuất đúng hạn mức trên 50 triệu (cần Tổng giám đốc phê duyệt), dẫn đến `context_precision` bị giảm sâu (0.0). Hệ thống cần cải thiện reranker hoặc thêm metadata filter phân loại hạn mức chi tiêu.
2. **Lỗi Retrieval / Recall (Câu 22 - Rank 9, multi_hop)**:
   - *Câu hỏi*: "Nếu cần mua một chiếc laptop 30 triệu cho nhân viên mới, ai phê duyệt và cần gì từ phòng CNTT?"
   - *Nguyên nhân*: Câu hỏi yêu cầu thông tin từ hai tài liệu khác nhau (quy trình mua sắm thiết bị và quy định cấp phát thiết bị CNTT). Pipeline chỉ lấy được 1 trong 2 chunk cần thiết, khiến `context_recall` bị hạ thấp (0.5). Cần bổ sung BM25 hybrid search hoặc mở rộng top-k retrieval cho multi-hop queries.
3. **Lỗi Generation / Answer Relevancy (Các câu Rank 2, 3, 4, 6, 7, 8, 10)**:
   - *Nguyên nhân*: Do chế độ chạy là `extractive_fallback`, pipeline trích xuất nguyên văn đoạn văn bản chứa câu trả lời thay vì dùng LLM sinh câu trả lời cô đọng và trực tiếp. Đoạn văn trích xuất chứa nhiều tiêu đề và câu từ phụ trợ (boilerplate markdown), khiến metric `answer_relevancy` của RAGAS đánh giá câu trả lời bị lan man, không khớp sát với câu hỏi.

## Matrix và nhóm yếu nhất

| Metric | factual (20) | multi_hop (20) | adversarial (10) | Tổng cộng |
|---|---|---|---|---|
| faithfulness | 0 | 0 | 0 | 0 |
| context_recall | 0 | 1 | 0 | 1 |
| context_precision | 1 | 0 | 0 | 1 |
| answer_relevancy | 19 | 19 | 10 | 48 |
| Tổng số câu | 20 | 20 | 10 | 50 |

Nhóm yếu theo mean thấp nhất: adversarial; mean: 0.7614.
Worst metric xuất hiện nhiều nhất: answer_relevancy; số câu: 48.

### Giải thích nhóm yếu nhất và đề xuất cải tiến
- Nhóm `adversarial` có điểm trung bình thấp nhất (0.7614) do `context_recall` thấp vượt trội (chỉ đạt 0.6833 so với >0.80 ở hai nhóm còn lại). Các câu adversarial chứa câu hỏi bẫy về phiên bản quy định cũ/mới (như chính sách bảo mật, đổi mật khẩu) hoặc điều kiện phủ định. Retrieval engine thường lấy nhầm các chunk chính sách phiên bản cũ hoặc bỏ sót các điều khoản ngoại lệ mới nhất.
- Đề xuất: Bổ sung bộ lọc metadata thời gian/phiên bản tài liệu (ví dụ chỉ ưu tiên v2024 mới nhất) và tinh chỉnh prompt generation với LLM thay vì trích xuất thô để nâng cao `answer_relevancy`.
- Cách kiểm chứng: Chạy lại `python scripts/run_experiments.py --phase a --live` sau khi cập nhật reranker/prompt và so sánh sự gia tăng của `avg_score` và `context_recall`.

## Bẫy adversarial và giới hạn

- **Bẫy xung đột phiên bản và phủ định**: Các câu adversarial (như câu 44: "Bao lâu phải đổi mật khẩu một lần?", câu 45: "Có cần kích hoạt xác thực đa yếu tố (MFA) không?") thách thức hệ thống khi tài liệu có cả quy định cũ (yêu cầu đổi mật khẩu định kỳ 90 ngày) và chính sách bảo mật v2024 hiện đại (khuyến nghị không đổi mật khẩu định kỳ trừ khi lộ lọt, nhưng bắt buộc MFA). Extractive fallback lấy cả hai thông tin mà không phân giải được tính hiệu lực thời gian.
- **Giới hạn thực nghiệm**: Tập câu hỏi gồm 50 câu (10 câu adversarial), đánh giá bằng bộ đánh giá `gpt-4o-mini` và `text-embedding-3-small`. Do dùng extractive fallback, độ trung thực (faithfulness) đạt gần tuyệt đối (0.99-1.00) nhưng answer relevancy bị thấp do câu trả lời chưa được LLM tổng hợp súc tích.
