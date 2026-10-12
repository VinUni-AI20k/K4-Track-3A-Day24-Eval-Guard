from __future__ import annotations

"""Module 4: RAGAS Evaluation — 4 metrics + failure analysis."""

import os, sys, json
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEST_SET_PATH

METRICS = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]


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


def load_test_set(path: str = TEST_SET_PATH) -> list[dict]:
    """Load test set from JSON. (Đã implement sẵn)"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def evaluate_ragas(questions: list[str], answers: list[str],
                   contexts: list[list[str]], ground_truths: list[str]) -> dict:
    """Run RAGAS evaluation.

    Returns {"<metric>": mean, "per_question": [EvalResult...],
             "metadata": {"evaluator_models": [...LLM IDs thực sự trả lời..., embedding model]}}.
    Lỗi hoặc điểm NaN sẽ raise — không trả điểm 0 giả để report trông như đã đo.
    """
    from config import LLM_API_KEY, LLM_BASE_URL, EVAL_EMBEDDING_MODEL
    if not LLM_API_KEY:
        raise RuntimeError("RAGAS cần LLM key: set OPENAI_API_KEY (và OPENAI_BASE_URL nếu dùng Gemini) trong .env")
    if not (len(questions) == len(answers) == len(contexts) == len(ground_truths)):
        raise ValueError("questions/answers/contexts/ground_truths must have the same length")

    import math
    from ragas import evaluate
    from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
    from datasets import Dataset
    from langchain_openai import OpenAIEmbeddings
    from ragas.run_config import RunConfig
    from src.llm import make_ragas_llm, reset_used_models, used_models

    dataset = Dataset.from_dict({
        "question": questions, "answer": answers,
        "contexts": contexts, "ground_truth": ground_truths,
    })
    # Gemini không hỗ trợ n>1 ("Multiple candidates is not enabled") và free tier giới hạn request
    # → answer_relevancy sinh 1 câu hỏi ngược thay vì 3.
    answer_relevancy.strictness = 1
    reset_used_models()
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        # LLM judge qua src/llm.py: cache + xoay vòng model khi hết quota
        llm=make_ragas_llm(),
        # check_embedding_ctx_length=False: gửi text thô (Gemini không nhận token ids của tiktoken)
        embeddings=OpenAIEmbeddings(model=EVAL_EMBEDDING_MODEL, api_key=LLM_API_KEY, base_url=LLM_BASE_URL,
                                    check_embedding_ctx_length=False),
        raise_exceptions=False,
        # Ít worker + timeout dài: tránh dội rate limit (16 worker mặc định → TimeoutError hàng loạt)
        run_config=RunConfig(max_workers=4, timeout=600, max_retries=3),
    )
    df = result.to_pandas()
    if len(df) != len(questions):
        raise RuntimeError(f"RAGAS returned {len(df)} rows for {len(questions)} questions")

    failed = []
    per_question = []
    for i, (_, row) in enumerate(df.iterrows()):
        scores = {}
        for m in METRICS:
            try:
                v = float(row.get(m))
            except (TypeError, ValueError):
                v = float("nan")
            if not math.isfinite(v):
                failed.append(f"q{i + 1}.{m}")
            scores[m] = v
        per_question.append(EvalResult(question=questions[i], answer=answers[i],
                                       contexts=list(contexts[i]), ground_truth=ground_truths[i], **scores))
    if failed:
        raise RuntimeError(f"RAGAS produced NaN/invalid scores ({len(failed)}): {failed[:10]} — "
                           "chạy lại (cache giữ các lượt đã xong) thay vì thay bằng 0")

    llm_models = used_models()
    if not llm_models:
        raise RuntimeError("Không ghi nhận được model LLM nào của RAGAS judge")

    out = {m: sum(getattr(r, m) for r in per_question) / len(per_question) for m in METRICS}
    out["per_question"] = per_question
    out["metadata"] = {"evaluator_models": [*llm_models, EVAL_EMBEDDING_MODEL]}
    return out


def failure_analysis(eval_results: list[EvalResult], bottom_n: int = 10) -> list[dict]:
    """Analyze bottom-N worst questions using Diagnostic Tree."""
    diagnostic_tree = {
        "faithfulness": ("LLM hallucinating", "Tighten prompt, lower temperature"),
        "context_recall": ("Missing relevant chunks", "Improve chunking or add BM25"),
        "context_precision": ("Too many irrelevant chunks", "Add reranking or metadata filter"),
        "answer_relevancy": ("Answer doesn't match question", "Improve prompt template"),
    }
    analyzed = []
    for r in eval_results:
        scores = {m: getattr(r, m) for m in METRICS}
        avg = sum(scores.values()) / len(scores)
        worst_metric = min(scores, key=scores.get)
        diagnosis, fix = diagnostic_tree[worst_metric]
        analyzed.append({
            "question": r.question, "answer": r.answer, "ground_truth": r.ground_truth,
            "worst_metric": worst_metric, "score": round(scores[worst_metric], 4),
            "avg_score": round(avg, 4), "scores": {m: round(v, 4) for m, v in scores.items()},
            "diagnosis": diagnosis, "suggested_fix": fix,
        })
    analyzed.sort(key=lambda x: x["avg_score"])
    return analyzed[:bottom_n]


if __name__ == "__main__":
    test_set = load_test_set()
    print(f"Loaded {len(test_set)} test questions")
    print("Run scripts/setup_answers.py first to generate answers, then call evaluate_ragas().")
