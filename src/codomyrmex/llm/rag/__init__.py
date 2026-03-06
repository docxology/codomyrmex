"""RAG (Retrieval-Augmented Generation) pipeline."""

from .models import Chunk, Document, DocumentType, GenerationContext, RetrievalResult
from .pipeline import (
    RAG_PROMPT_TEMPLATE,
    ContextFormatter,
    RAGPipeline,
    create_rag_prompt,
)
from .splitters import RecursiveTextSplitter, SentenceSplitter, TextSplitter
from .vectorstore import InMemoryVectorStore, VectorStore

__all__ = [
    "RAG_PROMPT_TEMPLATE",
    "Chunk",
    "ContextFormatter",
    "Document",
    "DocumentType",
    "GenerationContext",
    "InMemoryVectorStore",
    "RAGPipeline",
    "RecursiveTextSplitter",
    "RetrievalResult",
    "SentenceSplitter",
    "TextSplitter",
    "VectorStore",
    "create_rag_prompt",
]
