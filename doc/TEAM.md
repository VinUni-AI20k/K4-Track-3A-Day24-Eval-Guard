# Nhóm thực hiện K4 Track 3A

Tên nhóm: ThienBinh

Repo chung: https://github.com/longtqb04/K4-L3-DAY24-ThienBinh-Eval-Guard

Trưởng nhóm/người nộp: {{Họ tên và MSSV}}

Ngày lab/deadline áp dụng: {{Ngày giờ theo thông báo lớp}} — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: {{Commit SHA}}

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | {{Họ tên}} | {{MSSV}} | {{Phase/file/hàm}} | {{Commit/PR/report}} |
| 2 | {{Họ tên}} | {{MSSV}} | {{Phase/file/hàm}} | {{Commit/PR/report}} |
| 3 | {{Họ tên}} | {{MSSV}} | {{Phase/file/hàm}} | {{Commit/PR/report}} |

Người tích hợp/chạy batch/nộp link: {{Họ tên, công việc và bằng chứng}}.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: Windows 11 Home 10.0.26200; Python 3.11.9 (virtualenv `.venv`; máy có sẵn 3.12 nhưng NeMo 0.10 chỉ hỗ trợ đến 3.11); Microsoft Visual Studio Build Tools 2022 (17.14, workload VCTools) để build `annoy==1.17.3`.
Virtualenv/dependencies/imports: `py -3.11 -m venv .venv` → `pip install -r requirements/requirements.txt -c requirements/constraints-core.txt`: annoy build wheel thành công. Lỗi thực tế: pyarrow 26 kéo theo yêu cầu NumPy 2 xung đột với pin `numpy==1.26.4` (`ImportError: pyarrow requires NumPy 2.0`) → cài `pyarrow<20`. Sau đó `pip check`: "No broken requirements found"; `import ragas, nemoguardrails, annoy, presidio_analyzer, spacy`: OK; `python -m spacy download en_core_web_lg`: OK; unit tests 86 passed, 3 deselected (integration).
Models/Qdrant/50 answers đã chuẩn bị: Qdrant `qdrant/qdrant:v1.9.7` qua `docker compose -f infra/docker-compose.yml up -d`; embedding BGE-M3 + reranker tải từ HF Hub; LLM là Gemini free tier qua endpoint OpenAI-compatible. `setup_answers.py --live` sinh 50/50 answers `generation_mode=llm` (không fallback), 4 model generation do xoay vòng khi hết quota 20 request/model/ngày. Giới hạn: 2 PDF scan ảnh (BCTC.pdf, Nghị định 13/2023) không có text layer nên không được index; NeMo full runtime đã chạy live Phase C (guard `gemini-3.5-flash-lite`, 28/28 input, 4/4 output). Các sửa môi trường/tương thích đã làm: `m2_search` fallback `client.search()` cho qdrant-client 1.9; NeMo dùng `ChatOpenAI` cho model không phải gpt-*; `max_tokens: 1024` cho self-check prompts (Gemini thinking ẩn ăn hết 3 token mặc định); giãn cách request 4.5s cho judge/guard (giới hạn 15 RPM).
Nếu cài full NeMo chưa thành công, ghi lỗi thực tế; không dùng unit test pass
hoặc pip resolve để khẳng định runtime đã chạy.

## INDIVIDUAL

Sao chép mẫu cho mỗi thành viên; tiêu đề họ tên không dấu-MSSV.

### {{HoVaTen}}-{{MSSV}}

- Phần được giao và phần thực tế đã làm: {{Nhiệm vụ, file/hàm, mục đích}}.
- Bằng chứng: {{Commit/PR và artifacts/reports liên quan}}.
- Cách kiểm tra: {{Unit mock hoặc live experiment, lệnh và kết quả}}.
- Điều đã học: {{Khái niệm và cách thể hiện trong bài}}.
- Giới hạn/cách xử lý: {{Vấn đề và kiểm chứng}}.
- Nguồn/AI hỗ trợ nếu có: {{Công cụ, phạm vi, cách tự kiểm chứng}}.

## Cập nhật sau khi nộp

{{Ghi phiên bản nộp; nếu sửa sau deadline, ghi commit/thời điểm/lý do và thông báo
coach cho phép áp dụng bản cập nhật. Nếu không có cập nhật, ghi rõ không có.}}
