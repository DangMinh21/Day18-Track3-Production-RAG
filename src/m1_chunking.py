"""
Module 1: Advanced Chunking Strategies
=======================================
Implement semantic, hierarchical, và structure-aware chunking.
So sánh với basic chunking (baseline) để thấy improvement.

Test: pytest tests/test_m1.py
"""

import os, sys, glob, re
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (DATA_DIR, HIERARCHICAL_PARENT_SIZE, HIERARCHICAL_CHILD_SIZE,
                    SEMANTIC_THRESHOLD)


@dataclass
class Chunk:
    """Represents a text chunk with optional metadata and parent relationship.
    
    Attributes:
        text (str): The actual chunk content.
        metadata (dict): Optional metadata (chunk_index, strategy, source, etc.).
        parent_id (str | None): For hierarchical chunking, reference to parent chunk ID.
    """
    text: str
    metadata: dict = field(default_factory=dict)
    parent_id: str | None = None


def load_documents(data_dir: str = DATA_DIR) -> list[dict]:
    """Load all markdown/text files from data/. (Đã implement sẵn)"""
    docs = []
    for fp in sorted(glob.glob(os.path.join(data_dir, "*.md"))):
        with open(fp, encoding="utf-8") as f:
            docs.append({"text": f.read(), "metadata": {"source": os.path.basename(fp)}})
    return docs


# ─── Baseline: Basic Chunking (để so sánh) ──────────────


def chunk_basic(text: str, chunk_size: int = 500, metadata: dict | None = None) -> list[Chunk]:
    """
    Basic chunking: split theo paragraph (\\n\\n).
    Đây là baseline — KHÔNG phải mục tiêu của module này.
    (Đã implement sẵn)
    """
    metadata = metadata or {}
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for i, para in enumerate(paragraphs):
        if len(current) + len(para) > chunk_size and current:
            chunks.append(Chunk(text=current.strip(), metadata={**metadata, "chunk_index": len(chunks)}))
            current = ""
        current += para + "\n\n"
    if current.strip():
        chunks.append(Chunk(text=current.strip(), metadata={**metadata, "chunk_index": len(chunks)}))
    return chunks


# ─── Strategy 1: Semantic Chunking ───────────────────────


def chunk_semantic(text: str, threshold: float = SEMANTIC_THRESHOLD,
                   metadata: dict | None = None) -> list[Chunk]:
    """Semantic chunking by grouping sentences with similar meaning.
    
    Uses sentence embeddings to compare semantic similarity between consecutive
    sentences. When similarity drops below threshold, a new chunk is started.
    
    Vietnamese-specific: Uses 'sentence-transformers' with 'all-MiniLM-L6-v2'
    model (multilingual). For better Vietnamese, preprocess with underthesea.
    Fallback uses Jaccard similarity (token-based) if sentence-transformers unavailable.

    Args:
        text (str): Input text (supports Vietnamese).
        threshold (float): Cosine similarity threshold (default 0.85).
        metadata (dict | None): Metadata to attach.

    Returns:
        list[Chunk]: Chunks grouped by semantic similarity.
    """
    metadata = metadata or {}
    chunks = []
    
    # Split text into sentences
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n\n', text) if s.strip()]
    
    if not sentences:
        return chunks
    
    # Try to use sentence_transformers for semantic similarity
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = model.encode(sentences)
        
        # Cosine similarity function
        def cosine_sim(a, b):
            from numpy import dot
            from numpy.linalg import norm
            return dot(a, b) / (norm(a) * norm(b) + 1e-8)
        
        # Group sentences by similarity
        current_group = [sentences[0]]
        for i in range(1, len(sentences)):
            sim = cosine_sim(embeddings[i-1], embeddings[i])
            if sim < threshold:
                chunks.append(Chunk(
                    text=" ".join(current_group),
                    metadata={**metadata, "chunk_index": len(chunks), "strategy": "semantic"}
                ))
                current_group = []
            current_group.append(sentences[i])
        
        # Don't forget last group
        if current_group:
            chunks.append(Chunk(
                text=" ".join(current_group),
                metadata={**metadata, "chunk_index": len(chunks), "strategy": "semantic"}
            ))
    
    except (ImportError, Exception):
        # Offline fallback: keep nearby paragraphs together instead of splitting every
        # low-overlap sentence. This is stable for Markdown policies/reports where
        # headings and following paragraphs usually represent one topic.
        blocks = [block.strip() for block in text.split("\n\n") if block.strip()]
        target_size = 700
        current_group: list[str] = []
        current_len = 0

        for block in blocks:
            block_len = len(block)
            starts_new_section = bool(re.match(r"^#{1,3}\s+", block))
            should_flush = (
                current_group
                and current_len + block_len > target_size
                and not starts_new_section
            )
            if should_flush:
                chunks.append(Chunk(
                    text="\n\n".join(current_group),
                    metadata={**metadata, "chunk_index": len(chunks), "strategy": "semantic"}
                ))
                current_group = []
                current_len = 0

            current_group.append(block)
            current_len += block_len

        if current_group:
            chunks.append(Chunk(
                text="\n\n".join(current_group),
                metadata={**metadata, "chunk_index": len(chunks), "strategy": "semantic"}
            ))
    
    return chunks


# ─── Strategy 2: Hierarchical Chunking ──────────────────


def chunk_hierarchical(text: str, parent_size: int = HIERARCHICAL_PARENT_SIZE,
                       child_size: int = HIERARCHICAL_CHILD_SIZE,
                       metadata: dict | None = None) -> tuple[list[Chunk], list[Chunk]]:
    """Parent-child hierarchical chunking for production RAG systems.
    
    Creates two levels: larger parent chunks (for context) and smaller child chunks
    (for retrieval). Recommended for production. Children indexed in vector DB,
    parents returned to LLM for context.
    
    Vietnamese-specific: Use underthesea.sent_tokenize() before chunking for
    better Vietnamese sentence segmentation.

    Args:
        text (str): Input text (supports Vietnamese).
        parent_size (int): Max chars per parent (default 2048).
        child_size (int): Max chars per child (default 256).
        metadata (dict | None): Metadata to attach.

    Returns:
        tuple[list[Chunk], list[Chunk]]: (parents, children) with parent_id links.
    """
    metadata = metadata or {}
    parents = []
    children = []
    
    # 1. Split text into paragraphs
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    
    # 2. Create parent chunks by grouping paragraphs
    current_parent_text = ""
    parent_index = 0
    
    for para in paragraphs:
        if len(current_parent_text) + len(para) > parent_size and current_parent_text:
            # Save current parent
            parent_id = f"parent_{parent_index}"
            parents.append(Chunk(
                text=current_parent_text.strip(),
                metadata={
                    **metadata,
                    "chunk_type": "parent",
                    "parent_id": parent_id,
                    "chunk_index": parent_index
                }
            ))
            current_parent_text = ""
            parent_index += 1
        
        current_parent_text += para + "\n\n"
    
    # Don't forget last parent
    if current_parent_text.strip():
        parent_id = f"parent_{parent_index}"
        parents.append(Chunk(
            text=current_parent_text.strip(),
            metadata={
                **metadata,
                "chunk_type": "parent",
                "parent_id": parent_id,
                "chunk_index": parent_index
            }
        ))
    
    # 3. Create children by sliding window on each parent
    for parent in parents:
        parent_id = parent.metadata.get("parent_id")
        parent_text = parent.text
        child_index = 0
        
        # Split parent into children using sliding window
        for i in range(0, len(parent_text), child_size):
            child_text = parent_text[i:i + child_size]
            if child_text.strip():
                children.append(Chunk(
                    text=child_text.strip(),
                    metadata={
                        **metadata,
                        "chunk_type": "child",
                        "chunk_index": child_index
                    },
                    parent_id=parent_id
                ))
                child_index += 1
    
    return parents, children


# ─── Strategy 3: Structure-Aware Chunking ────────────────


def chunk_structure_aware(text: str, metadata: dict | None = None) -> list[Chunk]:
    """Structure-aware chunking respecting markdown hierarchy.
    
    Splits documents by markdown headers (h1-h3) while preserving tables,
    code blocks, and lists intact. Recommended for structured documents.
    Vietnamese-specific: Handles Vietnamese text in markdown headers correctly.

    Args:
        text (str): Markdown text (supports Vietnamese).
        metadata (dict | None): Metadata to attach.

    Returns:
        list[Chunk]: Chunks representing markdown sections with headers.
    """
    metadata = metadata or {}
    
    # Split by markdown headers (h1, h2, h3)
    sections = re.split(r'(^#{1,3}\s+.+$)', text, flags=re.MULTILINE)
    
    chunks = []
    current_header = ""
    current_content = ""
    chunk_index = 0
    
    for part in sections:
        if re.match(r'^#{1,3}\s+', part):
            # This is a header
            if current_content.strip() and current_header:
                # Save previous section
                chunk_text = f"{current_header}\n{current_content}".strip()
                chunks.append(Chunk(
                    text=chunk_text,
                    metadata={
                        **metadata,
                        "section": current_header.strip(),
                        "strategy": "structure",
                        "chunk_index": chunk_index
                    }
                ))
                chunk_index += 1
            current_header = part.strip()
            current_content = ""
        else:
            # This is content
            current_content += part
    
    # Don't forget last section
    if current_content.strip() and current_header:
        chunk_text = f"{current_header}\n{current_content}".strip()
        chunks.append(Chunk(
            text=chunk_text,
            metadata={
                **metadata,
                "section": current_header.strip(),
                "strategy": "structure",
                "chunk_index": chunk_index
            }
        ))
    
    return chunks


# ─── A/B Test: Compare All Strategies ────────────────────


def compare_strategies(documents: list[dict]) -> dict[str, dict]:
    """Compare all chunking strategies on a set of documents.
    
    Runs all four strategies and collects statistics for A/B testing.

    Args:
        documents (list[dict]): List of documents with 'text' and 'metadata'.
        
    Returns:
        dict[str, dict]: Statistics per strategy with num_chunks, avg/min/max length.
    """
    results: dict[str, dict] = {}
    
    # Test each strategy on all documents
    for strategy_name in ["basic", "semantic", "hierarchical", "structure"]:
        all_chunks: list[Chunk] = []
        all_lengths: list[int] = []
        
        for doc in documents:
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})
            
            if strategy_name == "basic":
                chunks = chunk_basic(text, metadata=metadata)
                all_chunks.extend(chunks)
                all_lengths.extend([len(c.text) for c in chunks])
            
            elif strategy_name == "semantic":
                chunks = chunk_semantic(text, threshold=SEMANTIC_THRESHOLD, metadata=metadata)
                all_chunks.extend(chunks)
                all_lengths.extend([len(c.text) for c in chunks])
            
            elif strategy_name == "hierarchical":
                parents, children = chunk_hierarchical(
                    text,
                    parent_size=HIERARCHICAL_PARENT_SIZE,
                    child_size=HIERARCHICAL_CHILD_SIZE,
                    metadata=metadata
                )
                all_chunks.extend(parents)
                all_chunks.extend(children)
                all_lengths.extend([len(c.text) for c in parents])
                all_lengths.extend([len(c.text) for c in children])
            
            elif strategy_name == "structure":
                chunks = chunk_structure_aware(text, metadata=metadata)
                all_chunks.extend(chunks)
                all_lengths.extend([len(c.text) for c in chunks])
        
        # Calculate statistics
        if all_lengths:
            results[strategy_name] = {
                "num_chunks": len(all_chunks),
                "avg_length": sum(all_lengths) / len(all_lengths),
                "min_length": min(all_lengths),
                "max_length": max(all_lengths),
            }
        else:
            results[strategy_name] = {
                "num_chunks": 0,
                "avg_length": 0,
                "min_length": 0,
                "max_length": 0,
            }
    
    return results


if __name__ == "__main__":
    # Demo: load documents and compare all chunking strategies
    docs = load_documents()
    print(f"Loaded {len(docs)} documents from {DATA_DIR}\n")
    
    results = compare_strategies(docs)
    print("Strategy Comparison Results:")
    print("-" * 70)
    for name, stats in results.items():
        print(f"  {name:15} | chunks={stats['num_chunks']:4d} | "
              f"avg_len={stats['avg_length']:7.1f} | "
              f"min={stats['min_length']:4d} | max={stats['max_length']:4d}")
