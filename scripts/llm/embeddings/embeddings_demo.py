#!/usr/bin/env python3
"""
Embeddings Demo Script

Demonstrates text embedding generation and similarity search functionality.
Uses sentence-transformers for local embeddings or API providers.

Features:
    - Text embedding generation
    - Cosine similarity calculation
    - Semantic search demonstration
"""

import sys
from pathlib import Path
import math

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_warning


def simple_hash_embedding(text: str, dim: int = 128) -> list[float]:
    """Generate a simple hash-based pseudo-embedding for demonstration.
    
    Note: This is NOT a real embedding - it's a placeholder for demonstration.
    For real embeddings, use sentence-transformers or an API.
    
    Args:
        text: Input text to embed
        dim: Embedding dimension
        
    Returns:
        List of floats representing the embedding
    """
    # Simple hash-based pseudo-embedding for demonstration
    import hashlib
    
    text_hash = hashlib.sha256(text.lower().encode()).hexdigest()
    
    # Convert hash to floats
    embedding = []
    for i in range(0, min(len(text_hash), dim * 2), 2):
        byte_val = int(text_hash[i:i+2], 16)
        normalized = (byte_val - 128) / 128.0  # Normalize to [-1, 1]
        embedding.append(normalized)
    
    # Pad if necessary
    while len(embedding) < dim:
        embedding.append(0.0)
    
    # Normalize to unit vector
    magnitude = math.sqrt(sum(x**2 for x in embedding))
    if magnitude > 0:
        embedding = [x / magnitude for x in embedding]
    
    return embedding[:dim]


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a**2 for a in vec1))
    mag2 = math.sqrt(sum(b**2 for b in vec2))
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    return dot_product / (mag1 * mag2)


def demo_embedding_generation():
    """Demonstrate embedding generation."""
    print_info("🔢 Embedding Generation Demo\n")
    
    texts = [
        "The quick brown fox jumps over the lazy dog.",
        "A fast auburn fox leaps across a sleepy canine.",
        "Python is a popular programming language.",
        "Machine learning enables computers to learn from data.",
    ]
    
    embeddings = {}
    for text in texts:
        emb = simple_hash_embedding(text, dim=8)  # Small dim for display
        embeddings[text] = emb
        emb_str = ", ".join(f"{x:.3f}" for x in emb[:4])
        print(f"  \"{text[:40]}...\"")
        print(f"    Embedding (first 4 dims): [{emb_str}, ...]")
        print()
    
    print_warning("  Note: Using pseudo-embeddings for demo. Use sentence-transformers for real embeddings.")
    return embeddings


def demo_similarity_search():
    """Demonstrate semantic similarity search."""
    print_info("\n🔍 Semantic Similarity Demo\n")
    
    # Corpus of documents
    corpus = [
        "Python is a versatile programming language used for web development.",
        "Machine learning models can recognize patterns in large datasets.",
        "The cat sat on the mat and watched the birds outside.",
        "Deep learning uses neural networks with many layers.",
        "JavaScript is commonly used for frontend web development.",
        "Natural language processing helps computers understand text.",
    ]
    
    # Query
    query = "How do neural networks work in AI?"
    
    print(f"  Query: \"{query}\"\n")
    print(f"  Searching {len(corpus)} documents...\n")
    
    # Embed query and corpus
    query_emb = simple_hash_embedding(query, dim=128)
    
    results = []
    for doc in corpus:
        doc_emb = simple_hash_embedding(doc, dim=128)
        similarity = cosine_similarity(query_emb, doc_emb)
        results.append((similarity, doc))
    
    # Sort by similarity
    results.sort(reverse=True)
    
    print("  Top matches:")
    for i, (score, doc) in enumerate(results[:3], 1):
        print(f"    {i}. [{score:.4f}] \"{doc[:50]}...\"")


def demo_embedding_caching():
    """Demonstrate embedding caching concept."""
    print_info("\n💾 Embedding Caching Demo\n")
    
    # Simulated cache
    cache = {}
    cache_hits = 0
    cache_misses = 0
    
    texts_to_embed = [
        "Hello world",
        "Machine learning",
        "Hello world",  # Duplicate - should hit cache
        "Deep learning",
        "Machine learning",  # Duplicate - should hit cache
    ]
    
    for text in texts_to_embed:
        if text in cache:
            cache_hits += 1
            print(f"  ✅ Cache HIT: \"{text}\"")
        else:
            cache_misses += 1
            cache[text] = simple_hash_embedding(text, dim=128)
            print(f"  ❌ Cache MISS: \"{text}\" (computed embedding)")
    
    total = cache_hits + cache_misses
    hit_rate = (cache_hits / total) * 100 if total > 0 else 0
    
    print(f"\n  Cache Statistics:")
    print(f"    Hits: {cache_hits}, Misses: {cache_misses}")
    print(f"    Hit Rate: {hit_rate:.1f}%")
    print(f"    Saved Computations: {cache_hits}")


def main():
    """Main demonstration."""
    setup_logging()
    print("=" * 60)
    print("  Embeddings Demo - Text Embedding & Similarity Search")
    print("=" * 60)
    print()
    
    demo_embedding_generation()
    demo_similarity_search()
    demo_embedding_caching()
    
    print()
    print_success("✅ Demo completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
