from __future__ import annotations

"""RAGAS adapter retaining Day 24 result shape and evaluator provenance."""

import json
import math
import os
from dataclasses import dataclass

from config import GENERATION_MODEL, TEST_SET_PATH

RAGAS_LLM_MODEL = os.getenv("RAGAS_LLM_MODEL", GENERATION_MODEL)
RAGAS_EMBEDDING_MODEL = os.getenv("RAGAS_EMBEDDING_MODEL", "text-embedding-3-small")


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
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _validated_score(value, name: str) -> float:
    score = float(value)
    if not math.isfinite(score) or not 0 <= score <= 1:
        raise ValueError(f"RAGAS {name} must be finite and within [0, 1], got {value!r}")
    return score


def evaluate_ragas(
    questions: list[str],
    answers: list[str],
    contexts: list[list[str]],
    ground_truths: list[str],
) -> dict:
    """Run four RAGAS metrics and report the exact configured evaluator models."""
    lengths = {len(questions), len(answers), len(contexts), len(ground_truths)}
    if len(lengths) != 1:
        raise ValueError("questions, answers, contexts and ground_truths must have equal lengths")
    if not questions:
        return {
            "faithfulness": 0.0,
            "answer_relevancy": 0.0,
            "context_precision": 0.0,
            "context_recall": 0.0,
            "per_question": [],
            "metadata": {"evaluator_models": [RAGAS_EMBEDDING_MODEL, RAGAS_LLM_MODEL]},
        }
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required for a real RAGAS evaluation")

    from datasets import Dataset
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from ragas import evaluate
    from ragas.llms import LangchainLLMWrapper
    from ragas.metrics import answer_relevancy, context_precision, context_recall
    from ragas.metrics._faithfulness import Faithfulness
    from ragas.run_config import RunConfig

    # RAGAS 0.1.x passes temperature at call time; GPT-5 nano requires it omitted.
    gpt5_model = RAGAS_LLM_MODEL.lower().startswith("gpt-5")

    class NoTemperatureChatOpenAI(ChatOpenAI):
        def _get_request_payload(self, input_, *, stop=None, **kwargs):
            payload = super()._get_request_payload(input_, stop=stop, **kwargs)
            payload.pop("temperature", None)
            return payload

    chat_llm = (
        NoTemperatureChatOpenAI(model=RAGAS_LLM_MODEL)
        if gpt5_model
        else ChatOpenAI(model=RAGAS_LLM_MODEL, temperature=0)
    )
    llm = LangchainLLMWrapper(chat_llm)
    embeddings = OpenAIEmbeddings(model=RAGAS_EMBEDDING_MODEL)

    class ShortAnswerSegmenter:
        def __init__(self, delegate):
            self.delegate = delegate

        def segment(self, answer: str) -> list[str]:
            sentences = self.delegate.segment(answer)
            if any(sentence.strip().endswith(".") for sentence in sentences):
                return sentences
            # RAGAS 0.1.x otherwise supplies no statements for short answers.
            return [answer.strip() + "."] if answer.strip() else sentences

    faithfulness_metric = Faithfulness()
    faithfulness_metric.sentence_segmenter = ShortAnswerSegmenter(
        faithfulness_metric.sentence_segmenter
    )
    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    })
    result = evaluate(
        dataset,
        metrics=[faithfulness_metric, answer_relevancy, context_precision, context_recall],
        llm=llm,
        embeddings=embeddings,
        run_config=RunConfig(timeout=600, max_workers=8, max_retries=3),
        raise_exceptions=True,
    )
    frame = result.to_pandas()
    rows: list[EvalResult] = []
    metric_names = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")
    for index, row in frame.iterrows():
        values = {name: _validated_score(row[name], f"{name}[{index}]") for name in metric_names}
        rows.append(EvalResult(
            question=str(row["question"]),
            answer=str(row["answer"]),
            contexts=list(row["contexts"]),
            ground_truth=str(row["ground_truth"]),
            **values,
        ))
    if len(rows) != len(questions):
        raise ValueError(f"RAGAS returned {len(rows)} rows for {len(questions)} questions")

    output = {name: sum(getattr(row, name) for row in rows) / len(rows) for name in metric_names}
    output.update(
        per_question=rows,
        metadata={"evaluator_models": sorted({RAGAS_LLM_MODEL, RAGAS_EMBEDDING_MODEL})},
    )
    return output


def failure_analysis(eval_results: list[EvalResult], bottom_n: int = 10) -> list[dict]:
    diagnoses = {
        "faithfulness": ("Answer is not fully supported by context", "Tighten grounded generation."),
        "answer_relevancy": ("Answer does not directly address the question", "Use a more focused prompt."),
        "context_precision": ("Retrieved context includes irrelevant chunks", "Improve reranking or reduce top-k."),
        "context_recall": ("Retrieved context misses relevant evidence", "Improve chunking or retrieval coverage."),
    }
    output = []
    for result in eval_results:
        metrics = {name: float(getattr(result, name)) for name in diagnoses}
        worst = min(metrics, key=metrics.get)
        diagnosis, suggested_fix = diagnoses[worst]
        output.append({
            "question": result.question,
            "answer": result.answer,
            "ground_truth": result.ground_truth,
            "contexts": result.contexts,
            "average_score": sum(metrics.values()) / len(metrics),
            "worst_metric": worst,
            "score": metrics[worst],
            "diagnosis": diagnosis,
            "suggested_fix": suggested_fix,
        })
    return sorted(output, key=lambda item: item["average_score"])[:bottom_n]


def save_report(results: dict, failures: list[dict], path: str = "reports/ragas_report.json") -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    serializable = {key: value for key, value in results.items() if key != "per_question"}
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"aggregate": serializable, "num_questions": len(results.get("per_question", [])),
                   "failures": failures}, handle, ensure_ascii=False, indent=2)
