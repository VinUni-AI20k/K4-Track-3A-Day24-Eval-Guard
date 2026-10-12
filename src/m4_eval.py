"""RAGAS evaluation with auditable rows and explicit failure state."""
from __future__ import annotations
import json
import math
import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

METRICS = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")

# config đã load_dotenv() nên các biến môi trường dưới đây đọc được từ .env.
BASE_URL = os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE") or "https://api.openai.com/v1"
_PREFIX = "openai/" if "openrouter.ai" in BASE_URL else ""
EVAL_LLM_MODEL = os.getenv("RAGAS_LLM_MODEL", _PREFIX + "gpt-4o-mini")
EVAL_EMBEDDING_MODEL = os.getenv("RAGAS_EMBEDDING_MODEL", _PREFIX + "text-embedding-3-small")
MAX_ATTEMPTS = 3

@dataclass
class EvalResult:
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float

def load_test_set(path=config.TEST_SET_PATH):
    with open(path, encoding="utf-8") as stream:
        return json.load(stream)

def _safe_error(exc):
    message = str(exc)
    if config.OPENAI_API_KEY:
        message = message.replace(config.OPENAI_API_KEY, "[REDACTED]")
    return f"{type(exc).__name__}: {message}"[:1200]

def _unit(value):
    """Float trong [0, 1] hoặc None; chỉ kẹp sai số dấu phẩy động, không thay NaN."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(v):
        return None
    if -1e-6 <= v < 0:
        return 0.0
    if 1 < v <= 1 + 1e-6:
        return 1.0
    if not 0 <= v <= 1:
        return None
    return v

def evaluate_ragas(questions, answers, contexts, ground_truths):
    def failed(error):
        return {**dict.fromkeys(METRICS, 0.0), "per_question": [],
                "evaluation_status": "failed", "evaluation_error": error,
                "metadata": {"evaluator_models": [EVAL_LLM_MODEL, EVAL_EMBEDDING_MODEL]}}
    if not (len(questions) == len(answers) == len(contexts) == len(ground_truths)):
        raise ValueError("Evaluation inputs must have equal lengths")
    if not questions:
        return failed("No questions")
    if not config.OPENAI_API_KEY:
        return failed("Missing OPENAI_API_KEY")
    try:
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
        from ragas.run_config import RunConfig
        from datasets import Dataset
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        judge = ChatOpenAI(model=EVAL_LLM_MODEL, temperature=0,
                           api_key=config.OPENAI_API_KEY, base_url=BASE_URL,
                           timeout=90, max_retries=2)
        embeddings = OpenAIEmbeddings(model=EVAL_EMBEDDING_MODEL,
                           api_key=config.OPENAI_API_KEY, base_url=BASE_URL,
                           check_embedding_ctx_length=False, request_timeout=90, max_retries=2)

        def _score(indices):
            """Chấm các dòng `indices`; trả {i: {metric: float}} chỉ gồm dòng hợp lệ."""
            dataset = Dataset.from_dict({"question": [questions[i] for i in indices],
                                         "answer": [answers[i] for i in indices],
                                         "contexts": [contexts[i] for i in indices],
                                         "ground_truth": [ground_truths[i] for i in indices]})
            result = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
                              llm=judge, embeddings=embeddings, raise_exceptions=False,
                              run_config=RunConfig(timeout=180, max_retries=3, max_workers=4))
            rows = result.to_pandas().to_dict(orient="records")
            if len(rows) != len(indices):
                raise ValueError("RAGAS row count mismatch")
            good = {}
            for i, row in zip(indices, rows):
                scores = {metric: _unit(row[metric]) for metric in METRICS}
                if all(v is not None for v in scores.values()):
                    good[i] = scores
            return good

        scored = {}
        pending = list(range(len(questions)))
        for _ in range(MAX_ATTEMPTS):
            scored.update(_score(pending))
            pending = [i for i in pending if i not in scored]
            if not pending:
                break
        if pending:
            return failed(f"Invalid/NaN RAGAS scores after {MAX_ATTEMPTS} attempts "
                          f"at positions {[p + 1 for p in pending]}")
        per_question = [EvalResult(questions[i], answers[i], contexts[i], ground_truths[i], **scored[i])
                        for i in range(len(questions))]
        return {**{metric: sum(getattr(r, metric) for r in per_question) / len(per_question) for metric in METRICS},
                "per_question": per_question, "evaluation_status": "success", "evaluation_error": None,
                "metadata": {"evaluator_models": [EVAL_LLM_MODEL, EVAL_EMBEDDING_MODEL]}}
    except Exception as exc:
        return failed(_safe_error(exc))

def failure_analysis(eval_results: list[EvalResult], bottom_n: int = 10) -> list[dict]:
    """Analyze bottom-N worst questions using Diagnostic Tree."""
    if not eval_results or bottom_n <= 0:
        return []
    diagnostic_tree = {
        "faithfulness": (
            "LLM tự bịa câu trả lời ngoài tài liệu (LLM hallucinating)",
            "Thắt chặt system prompt, giảm nhiệt độ (temperature) về 0",
        ),
        "context_recall": (
            "Hệ thống tìm kiếm bỏ sót đoạn văn đúng (Missing relevant chunks)",
            "Cải thiện lại bước cắt đoạn hoặc bổ sung từ khóa BM25",
        ),
        "context_precision": (
            "Đoạn văn không liên quan bị xếp lên đầu (Too many irrelevant chunks)",
            "Bổ sung tầng Cross-Encoder reranking hoặc lọc theo metadata",
        ),
        "answer_relevancy": (
            "Câu trả lời bị lệch trọng tâm câu hỏi (Answer doesn't match question)",
            "Viết lại prompt hướng dẫn mô hình trả lời trực tiếp hơn",
        ),
    }

    scored_items = []
    for r in eval_results:
        metrics = {
            "faithfulness": r.faithfulness,
            "answer_relevancy": r.answer_relevancy,
            "context_precision": r.context_precision,
            "context_recall": r.context_recall,
        }
        avg_score = sum(metrics.values()) / 4.0
        worst_metric = min(metrics, key=metrics.get)
        diagnosis, suggested_fix = diagnostic_tree[worst_metric]
        scored_items.append({
            "question": r.question,
            "worst_metric": worst_metric,
            "score": metrics[worst_metric],
            "diagnosis": diagnosis,
            "suggested_fix": suggested_fix,
            "avg_score": avg_score,
        })

    scored_items.sort(key=lambda x: x["avg_score"])
    return [
        {
            "question": item["question"],
            "worst_metric": item["worst_metric"],
            "score": item["score"],
            "diagnosis": item["diagnosis"],
            "suggested_fix": item["suggested_fix"],
        }
        for item in scored_items[:bottom_n]
    ]
