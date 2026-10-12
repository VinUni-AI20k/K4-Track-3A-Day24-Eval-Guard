from __future__ import annotations

"""Phase A: RAGAS Production Evaluation — 50q, 3 distributions, cluster analysis."""

import json
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
    groups = {"factual": [], "multi_hop": [], "adversarial": []}
    for item in test_set:
        dist = item.get("distribution")
        if dist not in groups:
            raise ValueError(f"Câu {item.get('id')}: distribution không hợp lệ {dist!r}")
        groups[dist].append(item)
    return groups


def run_ragas_50q(answers: list[dict]) -> RagasEvaluation:
    """Task 2: Chạy RAGAS 4 metrics trên toàn bộ 50 câu hỏi.

    Gợi ý — import từ Day 18 của bạn:
        from src.m4_eval import evaluate_ragas

    Steps:
        1. Extract questions, answers, contexts, ground_truths từ answers list
        2. Gọi evaluate_ragas() từ m4_eval.py
        3. Kết hợp kết quả với distribution info từ answers list
        4. Return RagasEvaluation(results, raw["metadata"]["evaluator_models"])
           m4 must report its actual LLM/embedding models; never guess JUDGE_MODEL.
    """
    import math
    try:
        from src.m4_eval import evaluate_ragas
    except ImportError as exc:
        raise ValueError("Missing src/m4_eval.py — copy evaluator từ Day 18; "
                         "không thể khai báo evaluator models thật.") from exc

    metric_names = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")

    def read_metric(pq, name: str, qid) -> float:
        # m4 có thể trả object (attribute) hoặc dict
        try:
            value = float(pq[name] if isinstance(pq, dict) else getattr(pq, name))
        except (KeyError, AttributeError, TypeError, ValueError) as exc:
            raise ValueError(f"Câu {qid}: thiếu hoặc sai kiểu metric {name}") from exc
        if not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError(f"Câu {qid}: {name}={value} không hữu hạn hoặc ngoài [0, 1]")
        return value

    questions     = [a["question"]     for a in answers]
    ans_texts     = [a["answer"]       for a in answers]
    contexts      = [a["contexts"]     for a in answers]
    ground_truths = [a["ground_truth"] for a in answers]

    raw = evaluate_ragas(questions, ans_texts, contexts, ground_truths)
    per_q = raw.get("per_question") or []
    if len(per_q) != len(answers):
        raise ValueError(f"m4 trả {len(per_q)} dòng cho {len(answers)} câu; "
                         f"evaluation_error={raw.get('evaluation_error')}")

    results = [
        RagasResult(
            question_id=a["id"], distribution=a["distribution"],
            question=a["question"], answer=a["answer"],
            contexts=a["contexts"], ground_truth=a["ground_truth"],
            **{m: read_metric(pq, m, a["id"]) for m in metric_names},
        )
        for a, pq in zip(answers, per_q)
    ]

    models = (raw.get("metadata") or {}).get("evaluator_models")
    if not isinstance(models, list) or not models:
        raise ValueError("m4 must report evaluator_models")
    return RagasEvaluation(results, list(models))


def bottom_10(results: list[RagasResult]) -> list[dict]:
    """Task 3: Lấy 10 câu hỏi có avg_score thấp nhất.

    Returns:
        [{"rank": 1, "question_id": ..., "distribution": ...,
          "question": ..., "avg_score": ..., "worst_metric": ...,
          "diagnosis": ..., "suggested_fix": ...}, ...]
    """
    metric_names = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")
    dist_meaning = {
        "factual":     "câu factual (tra cứu trực tiếp một đoạn)",
        "multi_hop":   "câu multi_hop (cần ghép thông tin từ nhiều đoạn)",
        "adversarial": "câu adversarial (bẫy phiên bản/phủ định)",
    }
    # Hành động theo (distribution, loại lỗi): retrieval = context_*, generation = còn lại
    dist_action = {
        ("factual", "retrieval"):
            "Factual: kiểm tra chunk chứa đáp án có lọt top-k không; thêm BM25/hybrid cho từ khoá và số hiệu chính xác.",
        ("factual", "generation"):
            "Factual: buộc trả lời ngắn, trích nguyên văn số liệu/điều khoản từ context.",
        ("multi_hop", "retrieval"):
            "Multi_hop: tăng số đoạn lấy về hoặc mở rộng parent chunk để đủ các mảnh cần ghép, rồi rerank giữ đoạn liên quan.",
        ("multi_hop", "generation"):
            "Multi_hop: yêu cầu trả lời từng bước, gắn đoạn nguồn cho từng ý trước khi tổng hợp.",
        ("adversarial", "retrieval"):
            "Adversarial: gắn metadata phiên bản/ngày hiệu lực, ưu tiên văn bản phiên bản mới khi lọc và rerank.",
        ("adversarial", "generation"):
            "Adversarial: thêm chỉ dẫn kiểm tra phiên bản và phủ định trong câu hỏi, nói rõ khi context mâu thuẫn.",
    }

    output = []
    for rank, r in enumerate(sorted(results, key=lambda r: (r.avg_score, r.question_id))[:10], 1):
        worst = r.worst_metric
        base_diag, base_fix = DIAGNOSTIC_TREE[worst]
        others = ", ".join(f"{m}={getattr(r, m):.3f}" for m in metric_names if m != worst)
        kind = "retrieval" if worst.startswith("context_") else "generation"
        not_found = "không tìm thấy" in r.answer.lower()

        diagnosis = (f"{base_diag}: {worst}={getattr(r, worst):.3f} thấp nhất "
                     f"(còn lại {others}); {dist_meaning.get(r.distribution, r.distribution)}.")
        fix = f"{base_fix}. {dist_action.get((r.distribution, kind), '')}".strip()
        if not_found:
            diagnosis += " Answer chứa 'Không tìm thấy': pipeline từ chối vì context không có thông tin cần."
            fix += " Sửa retrieval trước khi chỉnh prompt vì model đã từ chối do thiếu context."

        output.append({
            "rank": rank,
            "question_id": r.question_id,
            "distribution": r.distribution,
            "question": r.question,
            "avg_score": round(r.avg_score, 6),
            "worst_metric": worst,
            "diagnosis": diagnosis,
            "suggested_fix": fix,
        })
    return output


def cluster_analysis(results: list[RagasResult]) -> dict:
    """Task 4: Phân tích failure clusters theo (worst_metric × distribution).

    Matrix thống kê worst_metric của mọi câu, không coi mọi câu là một failure.
    Nhóm yếu nhất = distribution có avg_score trung bình thấp nhất (bỏ nhóm rỗng).
    Tổng matrix theo cột chỉ là kích thước nhóm 20/20/10, không đo chất lượng.

    Returns:
        {
          "matrix": {
            "faithfulness":      {"factual": 3, "multi_hop": 5, "adversarial": 2},
            "answer_relevancy":  {...},
            "context_precision": {...},
            "context_recall":    {...},
          },
          "dominant_failure_distribution": "multi_hop",
          "dominant_failure_metric": "context_recall",
          "insight": "..."
        }
    """
    if not results:
        raise ValueError("cluster_analysis cần ít nhất một RagasResult")

    dists = ("factual", "multi_hop", "adversarial")
    metric_names = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")
    matrix = {m: {d: 0 for d in dists} for m in metric_names}
    for r in results:
        matrix[r.worst_metric][r.distribution] += 1

    means = {}
    for d in dists:
        scores = [r.avg_score for r in results if r.distribution == d]
        if scores:  # bỏ nhóm rỗng khỏi phép chia
            means[d] = sum(scores) / len(scores)

    dominant_dist = min(means, key=means.get)  # chất lượng thấp nhất, KHÔNG phải nhóm đông nhất
    dominant_metric = max(matrix, key=lambda m: sum(matrix[m].values()))
    metric_count = sum(matrix[dominant_metric].values())
    diag, fix = DIAGNOSTIC_TREE[dominant_metric]
    all_means = ", ".join(f"{d}={v:.3f}" for d, v in means.items())
    insight = (f"Nhóm yếu nhất theo điểm trung bình là '{dominant_dist}' "
               f"(mean={means[dominant_dist]:.3f}; các nhóm: {all_means}). "
               f"Worst metric xuất hiện nhiều nhất là '{dominant_metric}' ở "
               f"{metric_count}/{len(results)} câu, chẩn đoán: {diag}. Gợi ý: {fix}.")

    return {"matrix": matrix, "distribution_avg_scores": means,
            "dominant_failure_distribution": dominant_dist,
            "dominant_failure_metric": dominant_metric, "insight": insight}


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from scripts.run_experiments import main
    raise SystemExit(main(["--phase", "a", *sys.argv[1:]]))
