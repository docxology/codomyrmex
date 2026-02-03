#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) Demo Script

Demonstrates a complete RAG pipeline including document processing,
embedding, retrieval, and augmented generation.

Features:
    - Document chunking and processing
    - Vector similarity search
    - Context augmentation
    - Answer generation with citations
"""

import sys
import math
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_warning


@dataclass
class Document:
    """A document for RAG processing."""
    content: str
    source: str
    metadata: dict = field(default_factory=dict)


@dataclass
class Chunk:
    """A chunk of a document."""
    content: str
    source: str
    chunk_id: int
    embedding: Optional[List[float]] = None


@dataclass
class SearchResult:
    """A search result with relevance score."""
    chunk: Chunk
    score: float


class SimpleVectorStore:
    """A simple in-memory vector store for demonstration."""
    
    def __init__(self):
        self.chunks: List[Chunk] = []
    
    def add_chunk(self, chunk: Chunk):
        """Add a chunk to the store."""
        if chunk.embedding is None:
            chunk.embedding = self._embed(chunk.content)
        self.chunks.append(chunk)
    
    def search(self, query: str, top_k: int = 3) -> List[SearchResult]:
        """Search for similar chunks."""
        query_embedding = self._embed(query)
        
        results = []
        for chunk in self.chunks:
            score = self._cosine_similarity(query_embedding, chunk.embedding)
            results.append(SearchResult(chunk=chunk, score=score))
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def _embed(self, text: str, dim: int = 64) -> List[float]:
        """Generate a simple hash-based pseudo-embedding."""
        text_hash = hashlib.sha256(text.lower().encode()).hexdigest()
        embedding = []
        for i in range(0, min(len(text_hash), dim * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            normalized = (byte_val - 128) / 128.0
            embedding.append(normalized)
        while len(embedding) < dim:
            embedding.append(0.0)
        # Normalize
        magnitude = math.sqrt(sum(x**2 for x in embedding))
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        return embedding[:dim]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(a**2 for a in vec1))
        mag2 = math.sqrt(sum(b**2 for b in vec2))
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot_product / (mag1 * mag2)


def chunk_document(doc: Document, chunk_size: int = 200, overlap: int = 50) -> List[Chunk]:
    """Split a document into overlapping chunks."""
    chunks = []
    text = doc.content
    start = 0
    chunk_id = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end]
        
        # Try to end at a sentence boundary
        if end < len(text):
            last_period = chunk_text.rfind('. ')
            if last_period > chunk_size // 2:
                chunk_text = chunk_text[:last_period + 1]
        
        chunks.append(Chunk(
            content=chunk_text.strip(),
            source=doc.source,
            chunk_id=chunk_id
        ))
        
        start = start + chunk_size - overlap
        chunk_id += 1
    
    return chunks


def demo_document_processing():
    """Demonstrate document processing and chunking."""
    print_info("📄 Document Processing Demo\n")
    
    # Sample documents
    documents = [
        Document(
            content="""Python is a high-level, interpreted programming language known for 
            its simple syntax and readability. It was created by Guido van Rossum and first 
            released in 1991. Python supports multiple programming paradigms, including 
            procedural, object-oriented, and functional programming. It has a large standard 
            library and an active community that contributes thousands of third-party packages.""",
            source="python_intro.txt"
        ),
        Document(
            content="""Machine learning is a subset of artificial intelligence that enables 
            computers to learn from data without being explicitly programmed. Common types 
            include supervised learning, unsupervised learning, and reinforcement learning. 
            Deep learning, a subset of machine learning, uses neural networks with many layers 
            to learn complex patterns in large amounts of data.""",
            source="ml_overview.txt"
        ),
        Document(
            content="""OpenRouter is an API gateway that provides unified access to multiple 
            LLM providers through a single API. It supports models from OpenAI, Anthropic, 
            Google, Meta, and many others. OpenRouter also offers free models for development 
            and testing, making it ideal for prototyping LLM applications.""",
            source="openrouter_docs.txt"
        ),
    ]
    
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc, chunk_size=150, overlap=30)
        all_chunks.extend(chunks)
        print(f"  Document: {doc.source}")
        print(f"    Original length: {len(doc.content)} chars")
        print(f"    Chunks created: {len(chunks)}")
        print()
    
    print(f"  Total chunks: {len(all_chunks)}")
    return all_chunks


def demo_vector_search(chunks: List[Chunk]):
    """Demonstrate vector similarity search."""
    print_info("\n🔍 Vector Search Demo\n")
    
    # Build vector store
    store = SimpleVectorStore()
    for chunk in chunks:
        store.add_chunk(chunk)
    
    print(f"  Indexed {len(store.chunks)} chunks\n")
    
    # Search queries
    queries = [
        "What is Python used for?",
        "How does machine learning work?",
        "What is OpenRouter?",
    ]
    
    for query in queries:
        print(f"  Query: \"{query}\"")
        results = store.search(query, top_k=2)
        print("  Top matches:")
        for i, result in enumerate(results, 1):
            print(f"    {i}. [{result.score:.4f}] {result.chunk.source}")
            print(f"       \"{result.chunk.content[:80]}...\"")
        print()
    
    return store


def demo_rag_pipeline(store: SimpleVectorStore):
    """Demonstrate complete RAG pipeline."""
    print_info("🔗 RAG Pipeline Demo\n")
    
    query = "What programming language is known for its simple syntax?"
    
    print(f"  User Query: \"{query}\"\n")
    
    # Step 1: Retrieve relevant context
    print("  Step 1: Retrieving relevant context...")
    results = store.search(query, top_k=2)
    
    context_parts = []
    for result in results:
        context_parts.append(f"[{result.chunk.source}]: {result.chunk.content}")
    
    context = "\n\n".join(context_parts)
    print(f"    Retrieved {len(results)} relevant chunks\n")
    
    # Step 2: Build augmented prompt
    print("  Step 2: Building augmented prompt...")
    augmented_prompt = f"""Answer the following question based on the provided context.
Include citations in the format [source.txt].

Context:
{context}

Question: {query}

Answer:"""
    
    print(f"    Prompt length: {len(augmented_prompt)} chars\n")
    
    # Step 3: Generate response (simulated)
    print("  Step 3: Generating response...")
    simulated_response = """Based on the context, Python is the programming language known 
for its simple syntax and readability [python_intro.txt]. It was created by Guido van 
Rossum and supports multiple programming paradigms including procedural, object-oriented, 
and functional programming [python_intro.txt]."""
    
    print(f"\n  Response:")
    print(f"  {'-' * 50}")
    print(f"  {simulated_response}")
    print(f"  {'-' * 50}")
    
    print_warning("\n  Note: Response is simulated. Connect to OpenRouter for real generation!")


def main():
    """Main demonstration."""
    setup_logging()
    print("=" * 60)
    print("  RAG Demo - Retrieval-Augmented Generation Pipeline")
    print("=" * 60)
    print()
    
    chunks = demo_document_processing()
    store = demo_vector_search(chunks)
    demo_rag_pipeline(store)
    
    print()
    print_success("✅ Demo completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
