# Phân tích lỗi Phase A

Nhóm: Latentia

Người phụ trách: Nguyễn Minh Tuấn - MSSV: 2A202602420

Nguồn: `artifacts/ragas_50q.json`; run timestamp: 2026-10-12T05:07:01.841963+00:00.
Generation mode/fallback và điều kiện chạy: Live generation mode=llm (OpenAI gpt-4o-mini-2024-07-18); BM25 Okapi + FlashRank reranker top_k=3; Qdrant container running trên port 6333; chạy thực nghiệm bằng python scripts/run_experiments.py --phase a --live.
Models generation/evaluator: Generation: gpt-4o-mini-2024-07-18; Evaluator: BAAI/bge-m3, gpt-4o-mini từ adapter m4_eval.

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
|---|---|---|---|
| faithfulness | 0.6750 | 0.2161 | 0.7000 |
| answer_relevancy | 0.5373 | 0.3306 | 0.5058 |
| context_precision | 0.6292 | 0.7417 | 0.7833 |
| context_recall | 0.5500 | 0.4208 | 0.5833 |
| avg_score | 0.5979 | 0.4273 | 0.6431 |

## Bottom 10 và nguyên nhân

| Rank | ID | Question | Distribution | Avg Score | Worst Metric | Diagnosis | Suggested Fix |
|---|---|---|---|---|---|---|---|
| 1 | 1 | Nhân viên được nghỉ bao nhiêu ngày khi kết hôn? | factual | 0.0000 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 2 | 8 | Nhân viên được nghỉ bao nhiêu ngày khi cha hoặc mẹ mất? | factual | 0.0000 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 3 | 9 | Nam nhân viên được nghỉ bao nhiêu ngày khi vợ sinh con? | factual | 0.0000 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 4 | 18 | Cơ cấu điểm đánh giá hiệu suất gồm những thành phần nào và tỷ lệ ra sao? | factual | 0.0000 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 5 | 20 | Phụ cấp đi lại tối đa mỗi tháng là bao nhiêu và điều kiện để được hưởng là gì? | factual | 0.0000 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 6 | 40 | Nhân viên cấp Manager có thời hạn thử việc 90 ngày, đang trong tháng thứ 3, phát hiện vi phạm bảo mật. Họ nên và không nên làm gì theo chính sách? | multi_hop | 0.0000 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 7 | 41 | Nhân viên được nghỉ bao nhiêu ngày phép năm? | adversarial | 0.0000 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 8 | 15 | Tạm ứng dưới 5 triệu cần ai phê duyệt? Từ 5 triệu trở lên thì sao? | factual | 0.0833 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 9 | 32 | Nhân viên mới cấp Manager có thời hạn thử việc 90 ngày, đang trong tháng thứ 3, có BẮT BUỘC tham dự buổi đào tạo nội bộ của phòng ban không? Tại sao? | multi_hop | 0.0833 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 10 | 38 | Nhân viên đi công tác nước ngoài 4 ngày tại thành phố lớn, ở khách sạn 200 USD/đêm (3 đêm). Công ty thanh toán bao nhiêu tiền khách sạn? | multi_hop | 0.0833 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |

### Đối chiếu nguyên nhân theo bằng chứng thực tế:
- **Câu ID 1 (Factual):** Context retrieved lấy phải các đoạn về thử việc và đăng ký kết hôn không đầy đủ mệnh đề nghỉ 3 ngày. Do prompt quy định "Nếu không có thông tin thì trả lời 'Không tìm thấy'", LLM đã trả về "Không tìm thấy." → Đây là lỗi xuất phát từ Retrieval Recall (bỏ sót đoạn quan trọng), dẫn đến Faithfulness và Relevancy bị chấm 0 điểm.
- **Câu ID 40 & ID 32 (Multi-hop):** Các câu hỏi đòi hỏi kết hợp thông tin từ 2 văn bản khác nhau (chính sách thử việc và quy trình bảo mật / đào tạo nội bộ). Do retrieval top_k=3 chỉ lấy được các đoạn rời rạc của một văn bản, context bị thiếu mất phần điều kiện của văn bản thứ hai, khiến câu trả lời không kết nối đầy đủ hai khía cạnh.
- **Câu ID 41 (Adversarial):** Câu hỏi về số ngày phép năm có bẫy xung đột giữa 2 phiên bản tài liệu `nghi_phep_nam_v2023.md` (12 ngày) và `nghi_phep_nam_v2024.md` (14 ngày). Hệ thống BM25 lấy cả hai đoạn nhưng LLM chưa phân biệt được ngày hiệu lực của phiên bản mới nhất, dẫn đến câu trả lời bị mâu thuẫn hoặc không xác định.

## Matrix và nhóm yếu nhất

| Metric | factual | multi_hop | adversarial |
|---|---|---|---|
| faithfulness | 7 | 15 | 3 |
| context_recall | 4 | 1 | 4 |
| context_precision | 3 | 1 | 1 |
| answer_relevancy | 6 | 3 | 2 |

Nhóm yếu theo mean thấp nhất: multi_hop; mean: 0.4273.
Worst metric xuất hiện nhiều nhất: faithfulness; số câu: 25.

### Phân tích nguyên nhân & Giải pháp cải tiến:
- **Nguyên nhân nhóm multi_hop yếu nhất (0.4273):** Nhóm multi_hop đòi hỏi phải suy luận tổng hợp từ nhiều nguồn dữ liệu (cross-document). Phương pháp chunking đơn lẻ 256 ký tự và top_k=3 quá nhỏ khiến các mẩu thông tin cần thiết bị phân mảnh, dẫn đến context_recall thấp (0.4208) và kéo theo faithfulness giảm sâu (0.2161).
- **Đề xuất cải tiến:**
  1. Tăng `RERANK_TOP_K` từ 3 lên 5 để bao quát đủ ngữ cảnh cho các câu multi-hop.
  2. Áp dụng Parent-Document Retrieval (trả về nội dung Parent chunk ~2048 ký tự thay vì chỉ Child chunk 256 ký tự) giúp cung cấp đầy đủ ngữ cảnh liên kết.
  3. Bổ sung Query Decomposition hoặc HyDE để phân tách câu multi-hop thành các truy vấn đơn trước khi tìm kiếm.
  4. Cách kiểm chứng: Chạy lại `python scripts/run_experiments.py --phase a --live` và theo dõi sự gia tăng của `per_distribution["multi_hop"]["avg_score"]`.

## Bẫy adversarial và giới hạn

### So sánh và phân tích bẫy:
- Trong nhóm Adversarial, các câu hỏi chứa bẫy xung đột phiên bản (chính sách mật khẩu v1 vs v2, phép năm 2023 vs 2024) và bẫy phủ định ("không được phép làm gì"). Điểm trung bình của nhóm Adversarial đạt 0.6431, cao hơn multi_hop nhưng điểm context_recall vẫn bị kéo xuống (0.5833).
- Việc điểm Adversarial đạt 0.6431 không đồng nghĩa với việc pipeline đã nhận thức hoàn hảo về version conflict; nguyên nhân là do BM25 vô tình ưu tiên từ khóa của văn bản có mật độ từ ngữ cao hơn.
- Giới hạn thực nghiệm: Bộ kiểm thử gồm 50 câu hỏi là tập mẫu ban đầu; việc sử dụng mô hình evaluator `gpt-4o-mini` có chi phí rẻ nhưng độ nhạy với ngữ nghĩa tiếng Việt chuyên sâu về chính sách có thể có sai lệch nhất định so với chuyên gia con người.
