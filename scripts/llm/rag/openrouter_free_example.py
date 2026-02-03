#!/usr/bin/env python3
"""
OpenRouter Free Example - RAG (Retrieval-Augmented Generation)

Simple example demonstrating RAG with OpenRouter's free models.
Shows how to augment LLM responses with retrieved context.

Usage:
    export OPENROUTER_API_KEY='your-key-here'
    python openrouter_free_example.py
"""

import sys
import os
from pathlib import Path

# Ensure codomyrmex is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.llm.providers import get_provider, ProviderType, ProviderConfig, Message


# Simple knowledge base (in real RAG, this would be from a vector database)
KNOWLEDGE_BASE = [
    {
        "source": "python_guide.txt",
        "content": "Python is a high-level programming language created by Guido van Rossum in 1991. It emphasizes code readability with significant whitespace."
    },
    {
        "source": "openrouter_docs.txt", 
        "content": "OpenRouter is an API gateway providing unified access to 100+ LLM models through a single API. It includes free models for development."
    },
    {
        "source": "ml_basics.txt",
        "content": "Machine learning is a subset of AI that enables computers to learn from data without being explicitly programmed."
    },
]


def simple_retrieve(query: str, top_k: int = 2) -> list:
    """Simple keyword-based retrieval (real RAG uses vector similarity)."""
    query_words = set(query.lower().split())
    
    scored = []
    for doc in KNOWLEDGE_BASE:
        doc_words = set(doc["content"].lower().split())
        overlap = len(query_words & doc_words)
        scored.append((overlap, doc))
    
    scored.sort(reverse=True)
    return [doc for _, doc in scored[:top_k]]


def rag_completion(provider, question: str) -> str:
    """Perform RAG: retrieve context, then generate answer."""
    # Retrieve relevant documents
    docs = simple_retrieve(question, top_k=2)
    
    # Build context
    context = "\n\n".join([
        f"[{doc['source']}]: {doc['content']}" 
        for doc in docs
    ])
    
    # Augmented prompt
    prompt = f"""Answer based on the following context. Cite sources in [brackets].

Context:
{context}

Question: {question}

Answer:"""
    
    messages = [Message(role="user", content=prompt)]
    
    response = provider.complete(
        messages=messages,
        model="openrouter/free",
        temperature=0.3,
        max_tokens=150,
    )
    
    return response.content, docs


def main():
    """Demonstrate RAG with OpenRouter free models."""
    print("=" * 60)
    print("  OpenRouter Free Example - RAG Pipeline")
    print("=" * 60)
    print()
    
    # Check for API key
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable not set")
        print("   Get your free API key at: https://openrouter.ai/keys")
        return 1
    
    config = ProviderConfig(api_key=api_key, timeout=60.0)
    question = "What is Python and who created it?"
    
    print(f"❓ Question: \"{question}\"")
    print()
    
    with get_provider(ProviderType.OPENROUTER, config=config) as provider:
        print("🔍 Step 1: Retrieving relevant context...")
        docs = simple_retrieve(question, top_k=2)
        for doc in docs:
            print(f"   📄 {doc['source']}")
        print()
        
        print("🤖 Step 2: Generating augmented response...")
        answer, _ = rag_completion(provider, question)
        print()
        
        print("📤 Answer:")
        print(f"   {answer}")
    
    print()
    print("✅ Example completed successfully!")
    print("   💡 RAG combines retrieval with generation for grounded responses!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
