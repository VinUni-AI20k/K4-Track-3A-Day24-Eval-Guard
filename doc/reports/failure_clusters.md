# Phân tích lỗi Phase A

Nhóm: ThienBinh

Người phụ trách: Trần Quốc Bảo Long - 2A202602696

Nguồn: `artifacts/ragas_50q.json`; run timestamp: 2026-10-12T14:30:49.653526+00:00 (21:30 UTC+07).
Generation mode/fallback và điều kiện chạy: 50/50 answers `generation_mode = "llm"`, không có
extractive fallback. Chạy live qua Gemini free tier (endpoint OpenAI-compatible); `src/llm.py`
xoay vòng model khi một model hết quota ngày (20 request/model/ngày), nên 50 answers do 4 model
khác nhau sinh ra (25 câu `gemini-3.5-flash-lite`, 17 `gemini-3.6-flash`, 5 `gemini-3.8-flash`,
3 `gemini-3.7-flash`). Retrieval: hybrid BM25 + dense (BGE-M3, Qdrant v1.9.7) + rerank, 130 chunks
đã enrich (2 PDF scan ảnh bị bỏ qua vì không có text layer).
Models generation/evaluator: generation = `gemini-3.5-flash-lite`, `gemini-3.6-flash`,
`gemini-3.7-flash`, `gemini-3.8-flash`; evaluator (m4, RAGAS) = `gemini-3.1-flash-lite`,
`gemini-3.5-flash`, `gemini-3.5-flash-lite`, `gemini-3.6-flash`, `gemini-3.7-flash`,
`gemini-flash-latest`, `gemini-flash-lite-latest`, embedding `gemini-embedding-001`.

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
|---|---|---|---|
| faithfulness | 1.000 | 0.800 | 0.675 |
| answer_relevancy | 0.952 | 0.819 | 0.609 |
| context_precision | 0.975 | 0.612 | 0.800 |
| context_recall | 0.925 | 0.729 | 0.717 |
| avg_score | 0.963 | 0.740 | 0.700 |

Trung bình toàn bộ 50 câu: faithfulness 0.855, answer_relevancy 0.830, context_precision 0.795,
context_recall 0.805.

## Bottom 10 và nguyên nhân

Bảng dưới lấy đúng 10 rows `bottom_10` của Task 3. Cột diagnosis/suggested_fix đầu tiên là output
của `bottom_10()`; cột "Chẩn đoán sau khi đọc answer/contexts" là kết luận của nhóm sau khi đối
chiếu answer, contexts và ground_truth.

| Rank | id | Distribution | avg_score | worst_metric | diagnosis / suggested_fix (Task 3) | Chẩn đoán sau khi đọc answer/contexts |
|---|---|---|---|---|---|---|
| 1 | 48 | adversarial | 0.417 | faithfulness | LLM hallucinating / Tighten system prompt, lower temperature | **Generation**: CTX0 nói rõ thử việc "chưa được hưởng gói PVI" nhưng model trả "Không tìm thấy." (negation trap) |
| 2 | 39 | multi_hop | 0.484 | context_precision | Too many irrelevant chunks / Add reranking or metadata filter | **Retrieval**: top-3 không có đoạn yêu cầu mật khẩu v1.0 (8 ký tự, 90 ngày) nên answer chỉ trả được phần v2.0 |
| 3 | 49 | adversarial | 0.491 | context_precision | Too many irrelevant chunks / Add reranking or metadata filter | **Retrieval thiếu thâm niên v2024**; answer nhận ra v2024 hiện hành (12 → 15 ngày) nhưng thiếu quy tắc +1 ngày/3 năm |
| 4 | 27 | multi_hop | 0.500 | answer_relevancy | Answer doesn't match question / Improve prompt template | **Retrieval + generation**: tính đúng 17 ngày nhưng không có chunk về ốm không giấy y tế nên bỏ dở bước trừ 4 ngày |
| 5 | 33 | multi_hop | 0.500 | answer_relevancy | Answer doesn't match question / Improve prompt template | **Retrieval + generation**: có đủ chunk phép năm nhưng thiếu chunk phụ cấp; model trả "Không tìm thấy." cho cả câu thay vì trả phần đã có |
| 6 | 47 | adversarial | 0.500 | faithfulness | LLM hallucinating / Tighten system prompt, lower temperature | **Generation**: CTX0/CTX1 ghi "tuyệt đối không tự xử lý, báo cáo trong 1 giờ" nhưng model trả "Không tìm thấy." |
| 7 | 35 | multi_hop | 0.593 | context_recall | Missing relevant chunks / Improve chunking or add BM25 | **Retrieval**: thiếu chunk phụ cấp điện thoại theo cấp bậc nên không kết luận được "Junior không có phụ cấp điện thoại", thiếu tổng 11.2 triệu |
| 8 | 37 | multi_hop | 0.615 | context_precision | Too many irrelevant chunks / Add reranking or metadata filter | **Retrieval (nguồn)**: answer đúng ý nhưng lấy cả hai ý từ `bao_mat_su_co.md`; thiếu chunk chính sách phân loại dữ liệu mà reference dẫn |
| 9 | 26 | multi_hop | 0.652 | context_precision | Too many irrelevant chunks / Add reranking or metadata filter | **Ranking**: answer đúng 3 + 1 = 4 ngày; CTX2 (phép năm v2024) là nhiễu nên precision bị kéo xuống |
| 10 | 46 | adversarial | 0.687 | faithfulness | LLM hallucinating / Tighten system prompt, lower temperature | **Generation**: CTX0 in đậm "KHÔNG được nghỉ phép năm" nhưng model trả "Không tìm thấy." |

Đối chiếu bằng chứng theo nhóm lỗi:

- **Generation từ chối dù context đủ (id 46, 47, 48; và 33):** contexts đều chứa câu trả lời, id 47
  có context_precision = context_recall = 1.0. Cả 4 câu đều do `gemini-3.5-flash-lite` sinh. Prompt
  hệ thống là "Trả lời CHỈ dựa trên context. Nếu không có → nói 'Không tìm thấy.'". Với câu hỏi
  có/không mà đáp án là phủ định, model chọn nhánh "Không tìm thấy". Faithfulness = 0 là do RAGAS
  không tìm được claim nào được context hỗ trợ trong câu "Không tìm thấy.", chứ không phải model bịa
  thông tin. Nhãn "LLM hallucinating" của Task 3 vì vậy không đúng bản chất.
- **Retrieval thiếu một vế của câu multi-hop (id 39, 49, 27, 33, 35, 37):** top-3 sau rerank thường
  lấy 2–3 chunk của cùng một tài liệu/phiên bản, thiếu vế còn lại (v1.0 mật khẩu, thâm niên v2024,
  ốm không giấy y tế, phụ cấp, phân loại dữ liệu). Generation thì trung thực (faithfulness 1.0 ở id
  27, 33, 35, 37, 39) nhưng trả lời không đủ.
- **Phiên bản (id 49, và câu 41 ở Phase B):** retriever lấy lẫn v2023 và v2024. Ở id 49, model nêu
  đúng v2024 là bản hiện hành, nhưng chunk thâm niên lấy được lại là của v2023.

## Matrix và nhóm yếu nhất

Mỗi câu được đếm đúng một lần theo `worst_metric` (metric thấp nhất của câu đó). Matrix mô tả metric
yếu nhất, không có nghĩa cả 50 câu đều là failure: phần lớn câu factual vẫn ≥ 0.9.

| worst_metric | factual | multi_hop | adversarial | Tổng |
|---|---|---|---|---|
| faithfulness | 0 | 6 | 3 | 9 |
| answer_relevancy | 15 | 3 | 2 | 20 |
| context_precision | 3 | 6 | 3 | 12 |
| context_recall | 2 | 5 | 2 | 9 |
| **Tổng** | 20 | 20 | 10 | 50 |

Nhóm yếu theo mean thấp nhất: adversarial; mean: 0.700 (multi_hop 0.740, factual 0.963).
Worst metric xuất hiện nhiều nhất: answer_relevancy; số câu: 20 (15 trong số đó thuộc factual).

Answer_relevancy đứng đầu chủ yếu vì factual có điểm cao đồng đều: 4 metric đều gần 1, nên metric
thấp nhất của câu thường là answer_relevancy (khoảng 0.9–0.95, do answer lặp lại "Dựa trên context"
hoặc thêm chi tiết phụ). Đây không phải lỗi nặng. Lỗi nặng tập trung ở adversarial và multi_hop:

- adversarial yếu vì 4/10 câu (46, 47, 48, 50) bị trả "Không tìm thấy." dù context có đáp án phủ
  định, kéo faithfulness (0.675) và answer_relevancy (0.609) xuống.
- multi_hop yếu ở context_precision (0.612) và context_recall (0.729) vì top-3 chunk không phủ đủ
  các vế của câu hỏi.

Đề xuất sửa và cách kiểm chứng:

1. **Prompt generation:** tách "không có thông tin" với "thông tin là phủ định". Ví dụ: "Nếu context
   nói KHÔNG/chưa được thì trả lời phủ định kèm trích dẫn; chỉ nói 'Không tìm thấy' khi không đoạn
   nào liên quan. Nếu chỉ tìm được một phần, trả lời phần đó và nêu phần còn thiếu." Kiểm chứng: chạy
   lại `setup_answers.py --live` rồi Phase A; kỳ vọng faithfulness adversarial > 0.85, và các câu
   46/47/48/50 không còn "Không tìm thấy".
2. **Tăng độ phủ retrieval cho multi_hop:** tăng `RERANK_TOP_K` từ 3 lên 5, hoặc tách câu hỏi
   multi-hop thành sub-query rồi gộp kết quả. Kiểm chứng: so context_recall và context_precision
   của multi_hop trước/sau (hiện 0.729/0.612) trên cùng 50 câu và cùng evaluator.
3. **Metadata filter phiên bản:** ưu tiên chunk có `version`/hiệu lực mới nhất, hạ điểm chunk tài
   liệu "đã hết hiệu lực" trừ khi câu hỏi nhắc rõ phiên bản cũ. Kiểm chứng trên các câu id 41, 49
   và các câu hỏi v1.0/v2.0 mật khẩu.

Khi chạy lại phải cố định cùng model generation, vì hiện tại 50 answers đến từ 4 model do xoay
vòng quota, nên so sánh trước/sau sẽ bị nhiễu bởi khác biệt giữa các model.

## Bẫy adversarial và giới hạn

So với factual (0.963) và multi_hop (0.740), adversarial thấp nhất (0.700). Bottom 10 có 4 câu
adversarial:

- **Negation trap (46, 47, 48):** đáp án đúng là phủ định ("KHÔNG"). Pipeline lấy được đúng chunk
  phủ định nhưng generation không dám phát biểu phủ định mà chọn "Không tìm thấy". Điểm thấp ở đây
  không chứng minh pipeline "nhận ra bẫy": nó né trả lời. Đây là lỗi an toàn theo kiểu từ chối,
  không phải lỗi bịa.
- **Version conflict (49):** answer xử lý đúng phần quan trọng nhất (v2023 = 12 ngày, v2024 hiện
  hành = 15 ngày), nhưng context_precision = 0 vì retrieval trả thêm chunk thâm niên v2023 thay vì
  v2024. Câu 41 (Phase B) có cùng kiểu lỗi: answer liệt kê cả 12 ngày (v2023) và 15 ngày (v2024),
  rồi gắn quy tắc thâm niên của v2023.

Giới hạn:

- Chỉ 50 câu (10 adversarial), nên mỗi câu adversarial chiếm 10% mean của nhóm. Chênh lệch giữa
  multi_hop và adversarial (0.04) nằm trong mức dao động của vài câu.
- Generation và evaluator đều là Gemini, và cả hai đều đổi model giữa chừng do quota free tier (4
  model generation, 7 model + 1 embedding cho evaluator). Điểm của các câu khác nhau có thể đến từ
  evaluator khác nhau.
- Hai PDF (BCTC.pdf, Nghị định 13/2023) là bản scan ảnh không có text layer nên không được index.
  Các câu hỏi cần hai tài liệu này sẽ luôn thiếu context.
- Không có extractive fallback trong bản nộp, nhưng mọi kết luận trên chỉ đúng với lần chạy ngày
  2026-10-12 này.
