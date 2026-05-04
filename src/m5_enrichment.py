"""
Module 5: Enrichment Pipeline
==============================
Làm giàu chunks TRƯỚC khi embed: Summarize, HyQA, Contextual Prepend, Auto Metadata.

Test: pytest tests/test_m5.py
"""

import os, sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY


@dataclass
class EnrichedChunk:
    """A chunk enriched with additional context and metadata.
    
    Attributes:
        original_text (str): Original raw chunk text.
        enriched_text (str): Text after enrichment (contextual prepend, etc).
        summary (str): Auto-generated summary of the chunk (2-3 sentences).
        hypothesis_questions (list[str]): Questions the chunk can answer (HyQA).
        auto_metadata (dict): Extracted metadata (topic, entities, category, language).
        method (str): Enrichment methods applied (e.g., 'contextual+hyqa+metadata').
    """
    original_text: str
    enriched_text: str
    summary: str
    hypothesis_questions: list[str]
    auto_metadata: dict
    method: str


# ─── Technique 1: Chunk Summarization ────────────────────


def summarize_chunk(text: str) -> str:
    """Generate a concise summary of a chunk using LLM or extractive fallback.
    
    Produces a 2-3 sentence summary that reduces noise when embedding. For Vietnamese,
    uses OpenAI's gpt-4o-mini which handles Vietnamese well. Falls back to simple
    extractive summary (first N sentences) if API unavailable.
    
    Args:
        text (str): Raw chunk text (supports Vietnamese).
        
    Returns:
        str: Summary string (2-3 sentences) or empty string if text is empty.
    """
    if not text or not OPENAI_API_KEY:
        # Fallback: extractive summary (first 2 sentences)
        sentences = text.split(". ")
        summary = ". ".join(sentences[:2])
        if summary and not summary.endswith("."):
            summary += "."
        return summary
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tóm tắt đoạn văn sau trong 2-3 câu ngắn gọn bằng tiếng Việt."},
                {"role": "user", "content": text},
            ],
            max_tokens=150,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        # Fallback: extractive
        sentences = text.split(". ")
        summary = ". ".join(sentences[:2])
        if summary and not summary.endswith("."):
            summary += "."
        return summary


# ─── Technique 2: Hypothesis Question-Answer (HyQA) ─────


def generate_hypothesis_questions(text: str, n_questions: int = 3) -> list[str]:
    """Generate hypothetical questions that a chunk might answer (HyQA technique).
    
    Produces questions to index alongside the chunk, bridging vocabulary gaps.
    Example: chunk contains "12 ngày làm việc" but user asks "nghỉ phép bao nhiêu ngày?"
    HyQA would generate "Nhân viên được nghỉ bao nhiêu ngày?" allowing better matching.
    
    Uses OpenAI gpt-4o-mini for Vietnamese question generation. Returns empty list
    if API is unavailable.

    Args:
        text (str): Raw chunk text (supports Vietnamese).
        n_questions (int): Number of questions to generate (default 3).
        
    Returns:
        list[str]: List of generated questions (may be empty if API unavailable).
    """
    if not text or not OPENAI_API_KEY:
        # Fallback: return empty list
        return []
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Dựa trên đoạn văn, tạo {n_questions} câu hỏi mà đoạn văn có thể trả lời. Trả về mỗi câu hỏi trên 1 dòng."},
                {"role": "user", "content": text},
            ],
            max_tokens=200,
        )
        questions = resp.choices[0].message.content.strip().split("\n")
        return [q.strip().lstrip("0123456789.-) ") for q in questions if q.strip()]
    except Exception:
        # Fallback: return empty list
        return []


# ─── Technique 3: Contextual Prepend (Anthropic style) ──


def contextual_prepend(text: str, document_title: str = "") -> str:
    """Prepend context explaining where a chunk appears in its document.
    
    Adds a contextual sentence explaining the document context and section.
    Anthropic research shows this alone reduces retrieval failures by 49%.
    For Vietnamese: generates natural Vietnamese context descriptors.
    
    Example: "Trích từ Chương 3 - Chính sách nghỉ phép, Sổ tay VinUni 2024."

    Args:
        text (str): Raw chunk text (supports Vietnamese).
        document_title (str): Source document name/title.
        
    Returns:
        str: Text with context sentence prepended and preserved original.
    """
    if not text or not OPENAI_API_KEY:
        # Fallback: return original text
        return text
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Viết 1 câu ngắn mô tả đoạn văn này nằm ở đâu trong tài liệu và nói về chủ đề gì. Chỉ trả về 1 câu."},
                {"role": "user", "content": f"Tài liệu: {document_title}\n\nĐoạn văn:\n{text}"},
            ],
            max_tokens=80,
        )
        context = resp.choices[0].message.content.strip()
        return f"{context}\n\n{text}"
    except Exception:
        # Fallback: return original text
        return text


# ─── Technique 4: Auto Metadata Extraction ──────────────


def extract_metadata(text: str) -> dict:
    """Automatically extract structured metadata from chunk using LLM.
    
    Extracts: topic, entities (NER), category (policy/hr/it/finance),
    and language. Enables rich filtering during search/retrieval.
    
    Example metadata: {'topic': 'vacation policy', 'entities': ['12 days', '5 years'],
                       'category': 'hr', 'language': 'vi'}
    
    For Vietnamese: Uses OpenAI gpt-4o-mini for multilingual NER and categorization.
    Falls back to empty dict if API unavailable.

    Args:
        text (str): Raw chunk text (supports Vietnamese).
        
    Returns:
        dict: Metadata dict with topic, entities, category, language keys.
    """
    if not text or not OPENAI_API_KEY:
        # Fallback: return empty dict
        return {}
    
    try:
        from openai import OpenAI
        import json
        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": 'Trích xuất metadata từ đoạn văn. Trả về JSON với fields: "topic", "entities", "category" (policy|hr|it|finance), "language" (vi|en). Tránh trả về markdown code block, chỉ JSON thuần.'},
                {"role": "user", "content": text},
            ],
            max_tokens=150,
        )
        content = resp.choices[0].message.content.strip()
        # Remove markdown code block if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        return json.loads(content)
    except Exception:
        # Fallback: return empty dict
        return {}


# ─── Full Enrichment Pipeline ────────────────────────────


def enrich_chunks(
    chunks: list[dict],
    methods: list[str] | None = None,
) -> list[EnrichedChunk]:
    """Run the enrichment pipeline on a list of chunks.
    
    Applies selected enrichment techniques (summarization, HyQA, contextual prepend,
    auto metadata extraction) to improve retrieval quality. This is an offline,
    one-time cost that benefits all subsequent queries.
    
    Enrichment methods:
    - 'summary': Generate concise summaries to reduce embedding noise
    - 'hyqa': Generate hypothetical questions for better query matching
    - 'contextual': Prepend document context (Anthropic technique)
    - 'metadata': Extract topic, entities, category for filtering
    - 'full': Apply all methods

    Args:
        chunks (list[dict]): List of chunks, each with 'text' and 'metadata' keys.
        methods (list[str] | None): Enrichment methods to apply.
                Default: ['contextual', 'hyqa', 'metadata']
        
    Returns:
        list[EnrichedChunk]: Enriched chunks ready for embedding and indexing.
    """
    if methods is None:
        # Default enrichment: contextual + HyQA + metadata (good balance)
        methods = ["contextual", "hyqa", "metadata"]

    enriched: list[EnrichedChunk] = []

    for chunk in chunks:
        text: str = chunk.get("text", "")
        metadata: dict = chunk.get("metadata", {})
        
        # Apply selected enrichment methods
        # Step 1: Generate summary if requested
        summary: str = ""
        if "summary" in methods or "full" in methods:
            summary = summarize_chunk(text)
        
        # Step 2: Generate hypothesis questions if requested
        questions: list[str] = []
        if "hyqa" in methods or "full" in methods:
            questions = generate_hypothesis_questions(text)
        
        # Step 3: Prepend contextual information if requested
        enriched_text: str = text
        if "contextual" in methods or "full" in methods:
            enriched_text = contextual_prepend(text, metadata.get("source", ""))
        
        # Step 4: Extract auto metadata if requested
        auto_meta: dict = {}
        if "metadata" in methods or "full" in methods:
            auto_meta = extract_metadata(text)
        
        # Create enriched chunk
        enriched.append(EnrichedChunk(
            original_text=text,
            enriched_text=enriched_text or text,
            summary=summary or "",
            hypothesis_questions=questions or [],
            auto_metadata={**metadata, **auto_meta},
            method="+".join(methods),
        ))
    
    return enriched


# ─── Main ────────────────────────────────────────────────

if __name__ == "__main__":
    """Demo enrichment pipeline on a sample Vietnamese HR policy chunk."""
    sample = "Nhân viên chính thức được nghỉ phép năm 12 ngày làm việc mỗi năm. Số ngày nghỉ phép tăng thêm 1 ngày cho mỗi 5 năm thâm niên công tác."

    print("=== Enrichment Pipeline Demo ===")
    print(f"\nOriginal chunk:\n  {sample}\n")
    print("-" * 70)

    # Demo each enrichment technique individually
    print("\n1. Summarization:")
    s = summarize_chunk(sample)
    print(f"   {s if s else '(No API key available)'}")

    print("\n2. Hypothesis Questions (HyQA):")
    qs = generate_hypothesis_questions(sample)
    if qs:
        for q in qs:
            print(f"   - {q}")
    else:
        print("   (No API key available)")

    print("\n3. Contextual Prepend:")
    ctx = contextual_prepend(sample, "Sổ tay nhân viên VinUni 2024")
    print(f"   {ctx}")

    print("\n4. Auto Metadata Extraction:")
    meta = extract_metadata(sample)
    if meta:
        for key, value in meta.items():
            print(f"   {key}: {value}")
    else:
        print("   (No API key available)")
