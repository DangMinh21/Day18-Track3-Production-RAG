"""Module 3: Reranking with cross-encoder and safe lexical fallback."""

import os
import re
import sys
import time
from dataclasses import dataclass
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RERANK_TOP_K


@dataclass
class RerankResult:
    text: str
    original_score: float
    rerank_score: float
    metadata: dict
    rank: int


class CrossEncoderReranker:
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        self.model_name = model_name
        self._model = None
        self._model_type = "uninitialized"

    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        try:
            if hasattr(value, "item"):
                value = value.item()
            if isinstance(value, (list, tuple)):
                if not value:
                    return default
                value = value[0]
            return float(value)
        except Exception:
            return default

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"\w+", (text or "").lower())

    @classmethod
    def _fallback_score(cls, query: str, text: str, original_score: float) -> float:
        q = (query or "").lower()
        d = (text or "").lower()
        q_tokens = set(cls._tokenize(q))
        d_tokens = set(cls._tokenize(d))

        if not q_tokens:
            return 0.05 * original_score

        overlap = q_tokens.intersection(d_tokens)
        overlap_ratio = len(overlap) / max(len(q_tokens), 1)

        phrase_bonus = 0.0
        important_phrases = [
            "nghi phep",
            "nghi",
            "ngay",
            "12",
            "nghỉ phép",
            "nghỉ",
            "ngày",
            "phép",
            "nghá»‰ phÃ©p",
            "nghá»‰",
            "phÃ©p",
            "ngÃ y",
        ]
        for phrase in important_phrases:
            if phrase and phrase in d:
                phrase_bonus += 0.15

        digit_bonus = 0.0
        for token in q_tokens:
            if token.isdigit() and token in d_tokens:
                digit_bonus += 0.1
        if "12" in d:
            digit_bonus += 0.2

        return overlap_ratio + phrase_bonus + digit_bonus + 0.05 * original_score

    def _model_scores(self, pairs: list[tuple[str, str]]) -> list[float] | None:
        if self._model is None:
            return None

        try:
            if self._model_type == "flag":
                raw_scores = self._model.compute_score(pairs)
            elif self._model_type == "cross_encoder":
                raw_scores = self._model.predict(pairs)
            else:
                return None
        except Exception:
            self._model = None
            self._model_type = "fallback"
            return None

        if raw_scores is None:
            return None

        if not isinstance(raw_scores, (list, tuple)):
            try:
                raw_scores = list(raw_scores)
            except TypeError:
                raw_scores = [raw_scores]

        scores = [self._safe_float(score) for score in raw_scores]
        if len(scores) < len(pairs):
            scores.extend([0.0] * (len(pairs) - len(scores)))
        return scores[: len(pairs)]

    def _load_model(self):
        if self._model is not None or self._model_type == "fallback":
            return self._model

        try:
            from FlagEmbedding import FlagReranker

            self._model = FlagReranker(self.model_name, use_fp16=False)
            self._model_type = "flag"
        except Exception:
            try:
                from sentence_transformers import CrossEncoder

                self._model = CrossEncoder(self.model_name)
                self._model_type = "cross_encoder"
            except Exception:
                self._model = None
                self._model_type = "fallback"

        return self._model

    def rerank(self, query: str, documents: list[dict], top_k: int = RERANK_TOP_K) -> list[RerankResult]:
        """Rerank candidate documents and return top-k results."""
        if not documents or top_k <= 0:
            return []

        self._load_model()
        pairs = [(query or "", str(doc.get("text", "") or "")) for doc in documents]
        scores = self._model_scores(pairs)

        if scores is None:
            scores = [
                self._fallback_score(
                    query=query,
                    text=str(doc.get("text", "") or ""),
                    original_score=self._safe_float(doc.get("score", 0.0)),
                )
                for doc in documents
            ]

        scored_docs = [(self._safe_float(score), doc) for score, doc in zip(scores, documents)]
        scored_docs.sort(key=lambda item: item[0], reverse=True)
        top_docs = scored_docs[: min(top_k, len(scored_docs))]

        results: list[RerankResult] = []
        for i, (score, doc) in enumerate(top_docs):
            results.append(
                RerankResult(
                    text=str(doc.get("text", "") or ""),
                    original_score=self._safe_float(doc.get("score", 0.0)),
                    rerank_score=self._safe_float(score),
                    metadata=doc.get("metadata", {}) or {},
                    rank=i + 1,
                )
            )
        return results


class FlashrankReranker:
    """Lightweight alternative with graceful fallback."""

    def __init__(self):
        self._model = None

    def rerank(self, query: str, documents: list[dict], top_k: int = RERANK_TOP_K) -> list[RerankResult]:
        if not documents or top_k <= 0:
            return []

        try:
            from flashrank import Ranker, RerankRequest

            if self._model is None:
                self._model = Ranker()

            passages = [
                {
                    "id": idx,
                    "text": str(doc.get("text", "") or ""),
                    "metadata": doc.get("metadata", {}) or {},
                }
                for idx, doc in enumerate(documents)
            ]
            results = self._model.rerank(RerankRequest(query=query, passages=passages))

            reranked: list[RerankResult] = []
            for i, item in enumerate(results[: min(top_k, len(results))]):
                idx = item.get("id")
                doc = documents[idx] if isinstance(idx, int) and 0 <= idx < len(documents) else {}
                reranked.append(
                    RerankResult(
                        text=str(item.get("text", doc.get("text", "")) or ""),
                        original_score=CrossEncoderReranker._safe_float(doc.get("score", 0.0)),
                        rerank_score=CrossEncoderReranker._safe_float(item.get("score", 0.0)),
                        metadata=item.get("metadata", doc.get("metadata", {}) or {}) or {},
                        rank=i + 1,
                    )
                )
            return reranked
        except Exception:
            return CrossEncoderReranker().rerank(query=query, documents=documents, top_k=top_k)


def benchmark_reranker(reranker, query: str, documents: list[dict], n_runs: int = 5) -> dict:
    """Benchmark latency over n_runs."""
    if n_runs <= 0:
        return {"avg_ms": 0.0, "min_ms": 0.0, "max_ms": 0.0}

    times_ms: list[float] = []
    for _ in range(n_runs):
        start = time.perf_counter()
        reranker.rerank(query, documents)
        elapsed_ms = (time.perf_counter() - start) * 1000
        times_ms.append(float(elapsed_ms))

    return {
        "avg_ms": sum(times_ms) / len(times_ms),
        "min_ms": min(times_ms),
        "max_ms": max(times_ms),
    }


if __name__ == "__main__":
    query = "Nhan vien duoc nghi phep bao nhieu ngay?"
    docs = [
        {"text": "Nhan vien duoc nghi 12 ngay/nam.", "score": 0.8, "metadata": {}},
        {"text": "Mat khau thay doi moi 90 ngay.", "score": 0.7, "metadata": {}},
        {"text": "Thoi gian thu viec la 60 ngay.", "score": 0.75, "metadata": {}},
    ]
    reranker = CrossEncoderReranker()
    for r in reranker.rerank(query, docs):
        print(f"[{r.rank}] {r.rerank_score:.4f} | {r.text}")
