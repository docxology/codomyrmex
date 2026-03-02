"""
MCP tools for the data_curation module.

Exposes MinHash-based deduplication capabilities through the Model Context
Protocol so that AI agents can deduplicate text corpora and estimate
document similarity.
"""

from __future__ import annotations


from codomyrmex.model_context_protocol.decorators import mcp_tool

from .minhash import DataCurator, MinHash


@mcp_tool(category="data_curation")
def data_curation_deduplicate(texts: list, threshold: float = 0.8) -> dict:
    """Deduplicate a list of texts using MinHash + LSH.

    Args:
        texts: List of text strings to deduplicate
        threshold: Jaccard similarity threshold (0.0-1.0) for considering
            two documents as near-duplicates. Default 0.8.

    Returns:
        dict with keys: unique_texts (list[str]), stats (dict with
        total_documents, unique_documents, duplicates_removed,
        duplicate_pairs_found, deduplication_ratio)
    """
    curator = DataCurator(similarity_threshold=threshold)
    unique_texts, stats = curator.deduplicate(texts)
    return {
        "unique_texts": unique_texts,
        "stats": stats,
    }


@mcp_tool(category="data_curation")
def data_curation_similarity(text_a: str, text_b: str) -> dict:
    """Estimate Jaccard similarity between two texts using MinHash.

    Args:
        text_a: First text document
        text_b: Second text document

    Returns:
        dict with keys: similarity (float), are_similar (bool at 0.8 threshold)
    """
    mh = MinHash()
    sig_a = mh.signature(text_a)
    sig_b = mh.signature(text_b)
    sim = mh.jaccard_estimate(sig_a, sig_b)
    return {
        "similarity": round(sim, 4),
        "are_similar": sim >= 0.8,
    }
