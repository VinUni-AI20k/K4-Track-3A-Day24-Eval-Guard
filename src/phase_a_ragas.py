from __future__ import annotations

"""Phase A: RAGAS Production Evaluation — 50q, 3 distributions, cluster analysis."""

import json
import math
import os
import sys
from dataclasses import asdict, dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEST_SET_PATH, ANSWERS_PATH, ARTIFACTS_DIR
from src.experiment_support import write_json

Distribution = str  # "factual" | "multi_hop" | "adversarial"

DIAGNOSTIC_TREE = {
    "faithfulness":      ("LLM hallucinating", "Tighten system prompt, lower temperature"),
    "context_recall":    ("Missing relevant chunks", "Improve chunking or add BM25"),
    "context_precision": ("Too many irrelevant chunks", "Add reranking or metadata filter"),
    "answer_relevancy":  ("Answer doesn't match question", "Improve prompt template"),
}


@dataclass
class RagasResult:
    question_id: int
    distribution: Distribution
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float

    @property
    def avg_score(self) -> float:
        return (self.faithfulness + self.answer_relevancy +
                self.context_precision + self.context_recall) / 4

    @property
    def worst_metric(self) -> str:
        scores = {
            "faithfulness":      self.faithfulness,
            "answer_relevancy":  self.answer_relevancy,
            "context_precision": self.context_precision,
            "context_recall":    self.context_recall,
        }
        return min(scores, key=scores.get)


# ─── Đã implement sẵn ────────────────────────────────────────────────────────

@dataclass
class RagasEvaluation:
    """Task 2 output: measured rows plus model identifiers reported by m4."""
    results: list[RagasResult]
    evaluator_models: list[str]

def load_test_set_50q(path: str = TEST_SET_PATH) -> list[dict]:
    """Load 50q test set với 3 distributions."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_answers(path: str = ANSWERS_PATH) -> list[dict]:
    """Load pre-generated answers từ setup_answers.py."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"answers_50q.json không tìm thấy tại {path}\n"
            "→ Chạy trước: python scripts/setup_answers.py --live"
        )
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_phase_a_report(results: list[RagasResult], clusters: dict, bottom: list[dict]) -> dict:
    """Provided exporter: preserve the student-produced Task 3 rows verbatim."""
    per_dist: dict[str, dict] = {}
    for dist in ["factual", "multi_hop", "adversarial"]:
        subset = [r for r in results if r.distribution == dist]
        if subset:
            per_dist[dist] = {
                "count": len(subset),
                "faithfulness":      sum(r.faithfulness for r in subset) / len(subset),
                "answer_relevancy":  sum(r.answer_relevancy for r in subset) / len(subset),
                "context_precision": sum(r.context_precision for r in subset) / len(subset),
                "context_recall":    sum(r.context_recall for r in subset) / len(subset),
                "avg_score":         sum(r.avg_score for r in subset) / len(subset),
            }

    report = {
        "total_questions": len(results),
        "per_question": [asdict(r) for r in results],
        "per_distribution": per_dist,
        "failure_clusters": clusters,
        "bottom_10": bottom,
    }
    return report


def save_phase_a_report(results: list[RagasResult], clusters: dict, bottom: list[dict],
                        path: str = os.path.join(ARTIFACTS_DIR, "ragas_50q.json")) -> None:
    write_json(path, build_phase_a_report(results, clusters, bottom))



# ─── Tasks 1-4: Sinh viên implement ──────────────────────────────────────────

def group_by_distribution(test_set: list[dict]) -> dict[str, list[dict]]:
    """Task 1: Nhóm 50 câu hỏi theo 3 distributions.

    Returns:
        {"factual": [...], "multi_hop": [...], "adversarial": [...]}
    """
    groups: dict[str, list[dict]] = {"factual": [], "multi_hop": [], "adversarial": []}
    for item in test_set:
        dist = item.get("distribution")
        if dist not in groups:
            raise ValueError(f"Unknown distribution {dist!r} for question id={item.get('id')}")
        groups[dist].append(item)
    return groups


METRICS = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")


def _metric_value(record, name: str) -> float:
    """Read one metric from an m4 record (object or mapping) as a finite float in [0, 1]."""
    raw = record[name] if isinstance(record, dict) else getattr(record, name)
    value = float(raw)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"m4 returned invalid {name}={raw!r}; fix m4 instead of faking scores")
    return value


def run_ragas_50q(answers: list[dict]) -> RagasEvaluation:
    """Task 2: Chạy RAGAS 4 metrics trên toàn bộ 50 câu hỏi.

    Gọi m4_eval.evaluate_ragas() một lần cho cả batch, ghép kết quả theo đúng thứ tự
    với distribution info từ answers list và giữ evaluator_models do m4 báo cáo.
    """
    try:
        from src.m4_eval import evaluate_ragas
    except ImportError as exc:
        raise ValueError("Missing src/m4_eval.py; cannot run RAGAS or declare its actual models") from exc

    questions     = [a["question"]     for a in answers]
    ans_texts     = [a["answer"]       for a in answers]
    contexts      = [list(a["contexts"]) for a in answers]
    ground_truths = [a["ground_truth"] for a in answers]

    raw = evaluate_ragas(questions, ans_texts, contexts, ground_truths)
    per_q = list(raw.get("per_question", []))
    if len(per_q) != len(answers):
        raise ValueError(f"m4 returned {len(per_q)} per_question rows for {len(answers)} answers")

    evaluator_models = list((raw.get("metadata") or {}).get("evaluator_models") or [])
    if not evaluator_models:
        raise ValueError("m4 metadata.evaluator_models is missing; fix the m4 adapter (do not use JUDGE_MODEL)")

    results = []
    for a, pq in zip(answers, per_q):
        results.append(RagasResult(
            question_id=a["id"], distribution=a["distribution"],
            question=a["question"], answer=a["answer"],
            contexts=a["contexts"], ground_truth=a["ground_truth"],
            **{m: _metric_value(pq, m) for m in METRICS},
        ))
    return RagasEvaluation(results, evaluator_models)


def bottom_10(results: list[RagasResult]) -> list[dict]:
    """Task 3: Lấy 10 câu hỏi có avg_score thấp nhất.

    Returns:
        [{"rank": 1, "question_id": ..., "distribution": ...,
          "question": ..., "avg_score": ..., "worst_metric": ...,
          "diagnosis": ..., "suggested_fix": ...}, ...]
    """
    # Stable tie-break by question_id so the ranking is reproducible.
    ranked = sorted(results, key=lambda r: (r.avg_score, r.question_id))[:10]
    output = []
    for rank, r in enumerate(ranked, 1):
        diag, fix = DIAGNOSTIC_TREE[r.worst_metric]
        output.append({
            "rank": rank,
            "question_id": r.question_id,
            "distribution": r.distribution,
            "question": r.question,
            "avg_score": r.avg_score,
            "worst_metric": r.worst_metric,
            "diagnosis": diag,
            "suggested_fix": fix,
        })
    return output


def cluster_analysis(results: list[RagasResult]) -> dict:
    """Task 4: Phân tích failure clusters theo (worst_metric × distribution).

    Matrix thống kê worst_metric của mọi câu, không coi mọi câu là một failure.
    Nhóm yếu nhất = distribution có avg_score trung bình thấp nhất (bỏ nhóm rỗng).
    Tổng matrix theo cột chỉ là kích thước nhóm 20/20/10, không đo chất lượng.
    """
    distributions = ("factual", "multi_hop", "adversarial")
    matrix = {metric: {d: 0 for d in distributions} for metric in DIAGNOSTIC_TREE}
    for r in results:
        matrix[r.worst_metric][r.distribution] += 1

    means = {}
    for d in distributions:
        subset = [r.avg_score for r in results if r.distribution == d]
        if subset:  # empty groups are skipped, never scored as 0
            means[d] = sum(subset) / len(subset)
    if not means:
        raise ValueError("cluster_analysis needs at least one result")

    dominant_dist = min(means, key=means.get)  # lowest quality, NOT largest group
    totals = {m: sum(matrix[m].values()) for m in matrix}
    dominant_metric = max(totals, key=totals.get)

    metric_means = {
        m: sum(getattr(r, m) for r in results) / len(results) for m in METRICS
    }
    diag, fix = DIAGNOSTIC_TREE[dominant_metric]
    ranking = ", ".join(f"{d}={v:.3f}" for d, v in sorted(means.items(), key=lambda kv: kv[1]))
    metric_line = ", ".join(f"{m}={v:.3f}" for m, v in metric_means.items())
    insight = (
        f"Nhóm yếu nhất theo avg_score trung bình là '{dominant_dist}' ({ranking}). "
        f"Metric thấp nhất xuất hiện nhiều nhất là '{dominant_metric}' "
        f"({totals[dominant_metric]}/{len(results)} câu; {matrix[dominant_metric]}). "
        f"Trung bình toàn bộ: {metric_line}. "
        f"Chẩn đoán sơ bộ: {diag}; gợi ý: {fix}. "
        "Matrix chỉ mô tả metric thấp nhất của mỗi câu, cần đọc bottom-10 trước khi kết luận nguyên nhân."
    )

    return {
        "matrix": matrix,
        "distribution_avg_scores": means,
        "dominant_failure_distribution": dominant_dist,
        "dominant_failure_metric": dominant_metric,
        "insight": insight,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from scripts.run_experiments import main
    raise SystemExit(main(["--phase", "a", *sys.argv[1:]]))
