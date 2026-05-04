"""Module 4: RAGAS evaluation with deterministic fallback analysis."""

import json
import math
import os
import re
import sys
from dataclasses import dataclass
from statistics import mean
from typing import Any, TypeAlias

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, TEST_SET_PATH

MetricName: TypeAlias = str
JsonDict: TypeAlias = dict[str, Any]
EvalSummary: TypeAlias = dict[str, float | list["EvalResult"]]

METRIC_NAMES: tuple[MetricName, ...] = (
    "faithfulness",
    "answer_relevancy",
    "context_precision",
    "context_recall",
)

DIAGNOSTIC_RULES: dict[MetricName, tuple[float, str, str]] = {
    "faithfulness": (0.85, "LLM hallucinating", "Tighten prompt and lower temperature"),
    "context_recall": (0.75, "Missing relevant chunks", "Improve chunking or add BM25/hybrid search"),
    "context_precision": (0.75, "Too many irrelevant chunks", "Add reranking or metadata filters"),
    "answer_relevancy": (0.80, "Answer does not match question", "Improve the prompt template"),
}


@dataclass
class EvalResult:
    """Per-question evaluation output for aggregate metrics and failure analysis."""

    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float


def load_test_set(path: str = TEST_SET_PATH) -> list[JsonDict]:
    """Load test set from JSON, tolerating common draft-file trailing commas."""
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        cleaned = re.sub(r",\s*([}\]])", r"\1", raw)
        data = json.loads(cleaned)
    if not isinstance(data, list):
        raise ValueError("test set must be a JSON list of question objects")
    return data


def _validate_inputs(
    questions: list[str], answers: list[str], contexts: list[list[str]], ground_truths: list[str]
) -> None:
    lengths = {len(questions), len(answers), len(contexts), len(ground_truths)}
    if len(lengths) != 1:
        raise ValueError("questions, answers, contexts, and ground_truths must have equal length")


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return default if math.isnan(number) or math.isinf(number) else number


def _as_context_list(value: Any, fallback: list[str]) -> list[str]:
    """Normalize RAGAS dataframe context cells without splitting strings into chars."""
    if value is None:
        return fallback
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    try:
        return [str(item) for item in list(value)]
    except TypeError:
        return fallback


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[\wÀ-ỹ]+", text.lower(), flags=re.UNICODE))


def _overlap_score(source: str, target: str) -> float:
    source_tokens = _tokens(source)
    target_tokens = _tokens(target)
    if not source_tokens or not target_tokens:
        return 0.0
    return len(source_tokens & target_tokens) / len(source_tokens)


def _heuristic_eval_result(
    question: str, answer: str, item_contexts: list[str], ground_truth: str
) -> EvalResult:
    joined_context = " ".join(item_contexts)
    relevant_contexts = [
        ctx for ctx in item_contexts if _overlap_score(ground_truth, ctx) > 0 or _overlap_score(question, ctx) > 0
    ]
    context_precision = len(relevant_contexts) / len(item_contexts) if item_contexts else 0.0
    return EvalResult(
        question=question,
        answer=answer,
        contexts=item_contexts,
        ground_truth=ground_truth,
        faithfulness=_overlap_score(answer, joined_context),
        answer_relevancy=_overlap_score(question, answer),
        context_precision=context_precision,
        context_recall=_overlap_score(ground_truth, joined_context),
    )


def _heuristic_evaluate(
    questions: list[str], answers: list[str], contexts: list[list[str]], ground_truths: list[str]
) -> EvalSummary:
    per_question = [
        _heuristic_eval_result(question, answer, item_contexts, ground_truth)
        for question, answer, item_contexts, ground_truth in zip(questions, answers, contexts, ground_truths)
    ]
    return _build_result(per_question)


def _build_result(per_question: list[EvalResult]) -> EvalSummary:
    aggregate = {
        metric: float(mean(getattr(item, metric) for item in per_question)) if per_question else 0.0
        for metric in METRIC_NAMES
    }
    aggregate["per_question"] = per_question
    return aggregate


def _evaluate_with_ragas(
    questions: list[str], answers: list[str], contexts: list[list[str]], ground_truths: list[str]
) -> EvalSummary:
    from datasets import Dataset
    from ragas import evaluate

    try:
        from ragas.metrics.collections import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )
    except ImportError:
        from ragas.metrics import answer_relevancy, context_precision, context_recall, faithfulness

    dataset = Dataset.from_dict(
        {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths,
            "reference": ground_truths,
        }
    )
    result = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
    df = result.to_pandas()
    per_question = []
    for idx, row in df.iterrows():
        per_question.append(
            EvalResult(
                question=str(row.get("question", questions[idx])),
                answer=str(row.get("answer", answers[idx])),
                contexts=_as_context_list(row.get("contexts"), contexts[idx]),
                ground_truth=str(row.get("ground_truth", row.get("reference", ground_truths[idx]))),
                faithfulness=_to_float(row.get("faithfulness")),
                answer_relevancy=_to_float(row.get("answer_relevancy")),
                context_precision=_to_float(row.get("context_precision")),
                context_recall=_to_float(row.get("context_recall")),
            )
        )
    return _build_result(per_question)


def evaluate_ragas(
    questions: list[str], answers: list[str], contexts: list[list[str]], ground_truths: list[str]
) -> EvalSummary:
    """Run the four required RAGAS metrics, falling back to local lexical scores."""
    _validate_inputs(questions, answers, contexts, ground_truths)
    if OPENAI_API_KEY:
        try:
            return _evaluate_with_ragas(questions, answers, contexts, ground_truths)
        except Exception as exc:
            # Keep evaluation usable in offline CI or when RAGAS/OpenAI calls are unavailable.
            print(f"RAGAS unavailable, using heuristic evaluator: {exc}")
    return _heuristic_evaluate(questions, answers, contexts, ground_truths)


def failure_analysis(eval_results: list[EvalResult], bottom_n: int = 10) -> list[JsonDict]:
    """Analyze bottom-N worst questions using Diagnostic Tree."""
    ranked = sorted(
        eval_results,
        key=lambda item: mean(_to_float(getattr(item, metric, 0.0)) for metric in METRIC_NAMES),
    )
    failures = []
    for item in ranked[: max(bottom_n, 0)]:
        scores = {metric: _to_float(getattr(item, metric, 0.0)) for metric in METRIC_NAMES}
        worst_metric = min(scores, key=scores.get)
        diagnosis, suggested_fix = _diagnose(worst_metric, scores[worst_metric])
        failures.append(
            {
                "question": item.question,
                "worst_metric": worst_metric,
                "score": scores[worst_metric],
                "avg_score": float(mean(scores.values())),
                "diagnosis": diagnosis,
                "suggested_fix": suggested_fix,
            }
        )
    return failures


def _diagnose(metric: str, score: float) -> tuple[str, str]:
    threshold, diagnosis, suggested_fix = DIAGNOSTIC_RULES[metric]
    if score < threshold:
        return diagnosis, suggested_fix
    return "No critical failure", "Keep monitoring this query in the evaluation set"


def save_report(results: EvalSummary, failures: list[JsonDict], path: str = "ragas_report.json") -> None:
    """Save aggregate scores and diagnostic failures to a JSON report."""
    report = {
        "aggregate": {k: v for k, v in results.items() if k != "per_question"},
        "num_questions": len(results.get("per_question", [])),
        "failures": failures,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report saved to {path}")


if __name__ == "__main__":
    test_set = load_test_set()
    print(f"Loaded {len(test_set)} test questions")
    print("Run pipeline.py first to generate answers, then call evaluate_ragas().")
