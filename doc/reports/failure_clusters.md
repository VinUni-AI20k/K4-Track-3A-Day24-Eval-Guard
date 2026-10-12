# Phân tích lỗi Phase A

Nhóm: NhomBotVN

Người phụ trách: Phạm Đình Hải (MSSV: 2A202602482) - Nhánh làm việc: `hai-phase-a`

Nguồn: `artifacts/ragas_50q.json`; run timestamp: 2026-10-12T05:41:06.175935+00:00.
Generation mode/fallback và điều kiện chạy: Chạy live hoàn toàn với `generation_mode: llm`, pipeline gồm hybrid search (BM25 + Dense all-MiniLM-L6-v2) kết hợp lexical reranking, không sử dụng extractive fallback; toàn bộ 50 câu hỏi được sinh qua OpenAI API.
Models generation/evaluator: Generation: gpt-4o-mini-2024-07-18; Evaluator: gpt-4o-mini, text-embedding-ada-002.

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
|---|---|---|---|
| faithfulness | 0.8750 | 0.3158 | 0.8000 |
| answer_relevancy | 0.7500 | 0.5434 | 0.5868 |
| context_precision | 0.9833 | 0.8625 | 0.8917 |
| context_recall | 0.9333 | 0.6792 | 0.6833 |
| avg_score | 0.8854 | 0.6002 | 0.7405 |

## Bottom 10 và nguyên nhân

| Rank | Question ID | Distribution | Question | Avg Score | Worst Metric | Diagnosis | Suggested Fix |
|---|---|---|---|---|---|---|---|
| 1 | 40 | multi_hop | Nhân viên cấp Manager có thời hạn thử việc 90 ngày, đang trong tháng thứ 3, phát hiện vi phạm bảo mật. Họ nên và không nên làm gì theo chính sách? | 0.0000 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 2 | 25 | multi_hop | Lương thử việc của nhân viên Junior mức cao nhất là bao nhiêu? | 0.2500 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 3 | 39 | multi_hop | So sánh yêu cầu mật khẩu giữa policy v1.0 và v2.0 về độ dài tối thiểu, thời hạn đổi và MFA. | 0.2500 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 4 | 50 | adversarial | Nhân viên Manager có thể dùng VPN cá nhân (như NordVPN) khi WFH để tăng bảo mật thêm không? | 0.2917 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 5 | 48 | adversarial | Nhân viên thử việc có được hưởng bảo hiểm sức khỏe PVI không? | 0.3125 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 6 | 22 | multi_hop | Nếu cần mua một chiếc laptop 30 triệu cho nhân viên mới, ai phê duyệt và cần gì từ phòng CNTT? | 0.3333 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 7 | 6 | factual | Thông tin lương thuộc cấp độ phân loại dữ liệu nào? | 0.3750 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 8 | 33 | multi_hop | Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp hàng tháng và số ngày phép năm theo v2024 là bao nhiêu? | 0.3750 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 9 | 29 | multi_hop | Nhân viên tạm ứng 8 triệu, chưa thanh toán sau 30 ngày (quá hạn 15 ngày). Ai phê duyệt khoản này và phí phạt là bao nhiêu? | 0.4167 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 10 | 34 | multi_hop | Nhân viên tạm ứng 4 triệu và một nhân viên khác tạm ứng 7 triệu: quy trình phê duyệt khác nhau thế nào? | 0.4167 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |

### Đối chiếu chi tiết các ca lỗi điển hình

1. **Lỗi Multi-hop (Câu 40 & Câu 39):**
   - **Câu 40 (Rank 1 - avg_score = 0.0):** Câu hỏi đòi hỏi tổng hợp từ hai tài liệu độc lập: chính sách thử việc (`thu_viec.md`) và quy trình xử lý sự cố an toàn thông tin (`bao_mat_su_co.md`). Trong retrieval chỉ lấy được một phần ngữ cảnh về thử việc nhưng thiếu tài liệu quy định về báo cáo sự cố vi phạm. Khi đó LLM sinh câu trả lời dựa trên suy đoán ("Không tìm thấy" hoặc tự suy luận sai lệch ngữ cảnh trích xuất), dẫn đến `faithfulness = 0.0` và `answer_relevancy = 0.0`.
   - **Câu 39 (Rank 3 - avg_score = 0.25):** Yêu cầu so sánh hai phiên bản chính sách mật khẩu (`mat_khau_v1.md` và `mat_khau_v2.md`). Hệ thống retrieval bị thiên lệch lấy chunk từ v2.0 hoặc v1.0 mà không trích xuất đủ cả hai bản song song để LLM làm bảng so sánh, khiến câu trả lời thiếu thông tin đối chiếu của phiên bản còn lại (`context_recall` và `faithfulness` bị suy giảm nghiêm trọng).

2. **Lỗi Adversarial Negation & False Premise (Câu 50 & Câu 48):**
   - **Câu 50 (Rank 4 - avg_score = 0.2917):** Câu hỏi gài tiền đề sai: *"Nhân viên Manager có thể dùng VPN cá nhân (như NordVPN) khi WFH để tăng bảo mật thêm không?"*. Chính sách công ty quy định rõ cấm dùng VPN thương mại cá nhân truy cập mạng nội bộ. LLM do thiên hướng chiều ý người dùng (sycophancy) đôi khi diễn giải lỏng lẻo thay vì khẳng định dứt khoát lệnh cấm, làm giảm độ trung thực so với ground truth.
   - **Câu 48 (Rank 5 - avg_score = 0.3125):** Câu hỏi gài bẫy quyền lợi thử việc đối với gói bảo hiểm sức khỏe PVI. Tài liệu nêu PVI chỉ cấp cho nhân viên chính thức. Khi ngữ cảnh trích xuất từ tài liệu thử việc không nêu cụ thể ngoại lệ bảo hiểm, LLM không có đủ căn cứ trực tiếp (`context_precision` thấp) dẫn đến trả lời chưa dứt khoát.

## Matrix và nhóm yếu nhất

| Metric | factual | multi_hop | adversarial |
|---|---|---|---|
| faithfulness | 3 | 17 | 2 |
| answer_relevancy | 15 | 1 | 1 |
| context_precision | 1 | 0 | 0 |
| context_recall | 1 | 2 | 7 |

Nhóm yếu theo mean thấp nhất: multi_hop; mean: 0.6002.
Worst metric xuất hiện nhiều nhất: faithfulness; số câu: 22.

### Phân tích nguyên nhân và giải pháp cải thiện

1. **Vì sao nhóm multi_hop yếu nhất (mean = 0.6002)?**
   - Điểm số `multi_hop` bị kéo tụt chủ yếu bởi `faithfulness` (chỉ đạt 0.3158) và `context_recall` (0.6792). Do đặc tính của bài toán multi-hop cần thông tin rải rác ở ít nhất 2 file tài liệu khác nhau (ví dụ: lương cấp bậc + phụ cấp, hoặc thử việc + bảo hiểm), cơ chế hybrid search đơn tầng chỉ tối ưu truy vấn bề mặt của câu hỏi tổng thể mà không tách nhỏ các ý con. Khi đó top 3 chunks sau rerank thường chỉ phủ được 1 hop, khiến LLM thiếu dữ kiện để kết luận hop còn lại và rơi vào trạng thái hallucination.
2. **Đề xuất khắc phục cụ thể:**
   - **Query Decomposition (Sub-query Generation):** Phân rã câu hỏi multi-hop thành 2 truy vấn đơn lẻ trước khi gửi vào bộ tìm kiếm, sau đó gộp kết quả chunks từ cả 2 nhánh.
   - **Tăng Rerank Top-K Context:** Nâng `RERANK_TOP_K` từ 3 lên 5 để bao quát được cả hai nguồn tài liệu khác nhau vào context window.
   - **Thắt chặt Prompt RAG:** Yêu cầu LLM chỉ trả lời dựa trên facts được cung cấp, nếu một trong các nhánh thông tin không có trong tài liệu thì phải từ chối rõ ràng từng phần thay vì phỏng đoán.
   - **Cách chạy lại để kiểm chứng:** Sau khi cập nhật prompt và query decomposition trong pipeline, sinh lại `artifacts/answers_50q.json` và chạy lại `python scripts/run_experiments.py --phase a --live`, đo lại mean của `multi_hop` xem có vượt ngưỡng 0.75 hay không.

## Bẫy adversarial và giới hạn

1. **So sánh với Factual và Multi-hop:**
   - Điểm trung bình của nhóm `adversarial` đạt **0.7405**, thấp hơn rõ rệt so với nhóm `factual` (**0.8854**). Điều này cho thấy tập câu hỏi đối kháng đặt ra thách thức đáng kể cho pipeline RAG, đặc biệt ở `context_recall` (0.6833) và `answer_relevancy` (0.5868).
   - Trong khi các câu hỏi factual đi thẳng vào một tài liệu duy nhất và đạt độ chuẩn xác cao (98.3% context precision), các câu hỏi adversarial cố tình chèn thông tin sai lệch hoặc yêu cầu phủ định một quyền lợi không tồn tại.
2. **Phân tích bẫy xung đột phiên bản (Version Conflict) và bẫy phủ định (Negation):**
   - **Bẫy phiên bản chính sách:** Các câu hỏi liên quan đến ngày phép năm v2023 vs v2024 hoặc chính sách mật khẩu v1.0 vs v2.0 khiến retrieval dễ lấy nhầm phiên bản cũ đã hết hiệu lực do từ khóa truy vấn trùng khớp nhiều token trong bản cũ. Nếu không có bộ lọc metadata theo ngày hiệu lực, câu trả lời sẽ đưa thông tin lỗi thời.
   - **Bẫy phủ định:** Các câu hỏi gài bẫy hỏi "có được làm X không" khi tài liệu cấm làm X (ví dụ dùng VPN cá nhân, hoặc quản lý kiêm mentor/buddy). Điểm adversarial thấp hơn phản ánh mô hình gặp khó khăn trong việc trích xuất và khẳng định tính phủ định, tuy nhiên điểm thấp không tự chứng minh pipeline đã hoàn toàn nhận ra bẫy mà là bằng chứng cho thấy cần bổ sung Guardrail chặn và xác minh tiền đề ở Phase C.
3. **Giới hạn thực nghiệm:**
   - Tập dữ liệu gồm 50 câu hỏi (20 factual, 20 multi_hop, 10 adversarial).
   - Model sinh là `gpt-4o-mini-2024-07-18`, mô hình evaluator RAGAS là `gpt-4o-mini` kết hợp `text-embedding-ada-002`. Reranker dùng thuật toán lexical rerank cục bộ thay cho cross-encoder sâu. Do đó, các ca đa tài liệu phức tạp bị hạn chế ở tầng rerank retrieval.
