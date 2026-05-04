"""Module 4: RAGAS evaluation and diagnostic failure analysis.

This module is responsible for the evaluation stage of the production RAG lab:
- load the curated test set,
- compute the four required RAGAS metrics,
- keep an offline heuristic fallback for tests/classroom environments,
- diagnose the weakest questions with the rubric's diagnostic tree,
- save a compact JSON report for the group deliverable.
"""

import json
import math
import os
import re
import sys
from dataclasses import dataclass
from statistics import mean
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, TEST_SET_PATH

METRIC_NAMES = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")

DIAGNOSTIC_RULES = {
    "faithfulness": (
        0.85,
        "LLM hallucinating",
        "Tighten prompt, require answers to cite context, and lower temperature",
    ),
    "context_recall": (
        0.75,
        "Missing relevant chunks",
        "Improve chunking, hybrid search, or increase retrieval top_k",
    ),
    "context_precision": (
        0.75,
        "Too many irrelevant chunks",
        "Add reranking, metadata filters, or stricter retrieval thresholds",
    ),
    "answer_relevancy": (
        0.80,
        "Answer does not match question",
        "Improve prompt template and make the model answer the exact question",
    ),
}


@dataclass
class EvalResult:
    """Per-question evaluation row used by reports and failure analysis."""

    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float


def load_test_set(path: str = TEST_SET_PATH) -> list[dict]:
    """Load test set from JSON.

    The lab test set is a list of dictionaries with at least:
    {"question": str, "ground_truth": str}.
    """
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _validate_inputs(
    questions: list[str],
    answers: list[str],
    contexts: list[list[str]],
    ground_truths: list[str],
) -> None:
    """Fail early if evaluation columns are not aligned."""
    if len({len(questions), len(answers), len(contexts), len(ground_truths)}) != 1:
        raise ValueError("questions, answers, contexts, and ground_truths must have the same length")


def _safe_float(value: Any, default: float = 0.0) -> float:
    """Convert metric values to finite JSON-safe floats."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return default if math.isnan(number) or math.isinf(number) else number


def _normalize_contexts(value: Any, fallback: list[str]) -> list[str]:
    """Handle context cells returned by different RAGAS/pandas versions."""
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
    """Tokenize English/Vietnamese text for the offline fallback metrics."""
    return set(re.findall(r"[\wÀ-ỹ]+", text.lower(), flags=re.UNICODE))


def _coverage(source: str, target: str) -> float:
    """Return how much source information appears in target."""
    source_tokens = _tokens(source)
    target_tokens = _tokens(target)
    if not source_tokens or not target_tokens:
        return 0.0
    return len(source_tokens & target_tokens) / len(source_tokens)


def _aggregate(per_question: list[EvalResult]) -> dict:
    """Create the public result shape expected by pipeline.py and tests."""
    result = {
        metric: float(mean(getattr(row, metric) for row in per_question)) if per_question else 0.0
        for metric in METRIC_NAMES
    }
    result["per_question"] = per_question
    return result


def _heuristic_evaluate(
    questions: list[str],
    answers: list[str],
    contexts: list[list[str]],
    ground_truths: list[str],
) -> dict:
    """Deterministic fallback when RAGAS/OpenAI cannot run.

    This is not a replacement for true RAGAS scoring. It simply keeps unit tests
    and offline demos functional by approximating the same four dimensions with
    token overlap.
    """
    per_question = []
    for question, answer, item_contexts, ground_truth in zip(questions, answers, contexts, ground_truths):
        context_text = " ".join(item_contexts)
        relevant_contexts = [
            ctx for ctx in item_contexts if _coverage(question, ctx) > 0 or _coverage(ground_truth, ctx) > 0
        ]
        per_question.append(
            EvalResult(
                question=question,
                answer=answer,
                contexts=item_contexts,
                ground_truth=ground_truth,
                faithfulness=_coverage(answer, context_text),
                answer_relevancy=_coverage(question, answer),
                context_precision=len(relevant_contexts) / len(item_contexts) if item_contexts else 0.0,
                context_recall=_coverage(ground_truth, context_text),
            )
        )
    return _aggregate(per_question)


def _evaluate_with_ragas(
    questions: list[str],
    answers: list[str],
    contexts: list[list[str]],
    ground_truths: list[str],
) -> dict:
    """Run real RAGAS and normalize package-version differences."""
    from datasets import Dataset
    from ragas import evaluate
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.llms import LangchainLLMWrapper
    from ragas.metrics import (
        AnswerRelevancy,
        Faithfulness,
        LLMContextPrecisionWithReference,
        LLMContextRecall,
    )

    llm = LangchainLLMWrapper(
        ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY)
    )
    embeddings = LangchainEmbeddingsWrapper(
        OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)
    )
    metrics = [
        Faithfulness(),
        AnswerRelevancy(),
        LLMContextPrecisionWithReference(),
        LLMContextRecall(),
    ]

    dataset = Dataset.from_dict(
        {
            "user_input": questions,
            "response": answers,
            "retrieved_contexts": contexts,
            "reference": ground_truths,
        }
    )
    result = evaluate(dataset, metrics=metrics, llm=llm, embeddings=embeddings)

    per_question = []
    for idx, row in result.to_pandas().iterrows():
        per_question.append(
            EvalResult(
                question=str(row.get("user_input", questions[idx])),
                answer=str(row.get("response", answers[idx])),
                contexts=_normalize_contexts(row.get("retrieved_contexts"), contexts[idx]),
                ground_truth=str(row.get("reference", ground_truths[idx])),
                faithfulness=_safe_float(row.get("faithfulness")),
                answer_relevancy=_safe_float(row.get("answer_relevancy")),
                context_precision=_safe_float(
                    row.get(
                        "context_precision",
                        row.get("context_precision_with_reference", row.get("llm_context_precision_with_reference")),
                    )
                ),
                context_recall=_safe_float(row.get("context_recall")),
            )
        )
    return _aggregate(per_question)


def evaluate_ragas(
    questions: list[str],
    answers: list[str],
    contexts: list[list[str]],
    ground_truths: list[str],
) -> dict:
    """Run the four required RAGAS metrics.

    The preferred path uses the real RAGAS package. If credentials/network/model
    calls fail, the deterministic fallback returns the same schema so the lab
    pipeline and tests still complete.
    """
    _validate_inputs(questions, answers, contexts, ground_truths)
    if OPENAI_API_KEY:
        try:
            return _evaluate_with_ragas(questions, answers, contexts, ground_truths)
        except Exception as exc:
            print(f"RAGAS unavailable, using heuristic evaluator: {exc}")
    return _heuristic_evaluate(questions, answers, contexts, ground_truths)


def failure_analysis(eval_results: list[EvalResult], bottom_n: int = 10) -> list[dict]:
    """Analyze bottom-N worst questions using the lab Diagnostic Tree."""
    ranked = sorted(
        eval_results,
        key=lambda row: mean(_safe_float(getattr(row, metric)) for metric in METRIC_NAMES),
    )
    failures = []
    for row in ranked[: max(bottom_n, 0)]:
        scores = {metric: _safe_float(getattr(row, metric)) for metric in METRIC_NAMES}
        worst_metric = min(scores, key=scores.get)
        threshold, diagnosis, suggested_fix = DIAGNOSTIC_RULES[worst_metric]

        # Keep output actionable even when the worst metric is above threshold.
        if scores[worst_metric] >= threshold:
            diagnosis = "No critical failure"
            suggested_fix = "Keep monitoring this question in the regression test set"

        failures.append(
            {
                "question": row.question,
                "worst_metric": worst_metric,
                "score": scores[worst_metric],
                "avg_score": float(mean(scores.values())),
                "diagnosis": diagnosis,
                "suggested_fix": suggested_fix,
            }
        )
    return failures


def save_report(results: dict, failures: list[dict], path: str = "ragas_report.json") -> None:
    """Save aggregate evaluation report to JSON."""
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
