# rag

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Retrieval-Augmented Generation pipeline with document processing. Provides end-to-end RAG infrastructure: load documents from text or files, split them into chunks using recursive or sentence-based strategies, store embeddings in a pluggable vector store, retrieve relevant chunks by cosine similarity, format retrieved context for LLM prompts, and generate augmented responses. The `RAGPipeline` orchestrates the full index-retrieve-format workflow.

## Key Exports

- **`DocumentType`** -- Enum of supported document types (text, markdown, html, pdf, code)
- **`Document`** -- Dataclass representing a source document with ID, content, type, source path, metadata, content hash, and factory methods `from_text()` / `from_file()`
- **`Chunk`** -- Dataclass for a document chunk with ID, content, document reference, sequence number, character offsets, metadata, and optional embedding vector
- **`RetrievalResult`** -- Dataclass pairing a `Chunk` with its similarity score and optional parent `Document`
- **`GenerationContext`** -- Dataclass combining query text, retrieved results, formatted context string, and metadata (chunk count, average score)
- **`TextSplitter`** -- Abstract base class for document splitting strategies
- **`RecursiveTextSplitter`** -- Splits text by trying progressively smaller separators (paragraph, line, sentence, word, character) with configurable chunk size and overlap
- **`SentenceSplitter`** -- Splits text by sentence boundaries with configurable sentences-per-chunk and overlap
- **`VectorStore`** -- Abstract base class for vector storage with add, search, and delete interfaces
- **`InMemoryVectorStore`** -- Simple in-memory vector store using cosine similarity for search
- **`ContextFormatter`** -- Formats retrieval results into a context string for LLM prompts with configurable template and max length
- **`RAGPipeline`** -- End-to-end pipeline that indexes documents (split + embed + store), retrieves relevant chunks for queries, and builds formatted generation contexts
- **`RAG_PROMPT_TEMPLATE`** -- Default prompt template string for RAG-augmented generation
- **`create_rag_prompt()`** -- Convenience function that renders `RAG_PROMPT_TEMPLATE` with a `GenerationContext`

## Directory Contents

- `__init__.py` - All RAG logic: document model, text splitters, vector stores, context formatter, RAG pipeline, prompt template
- `README.md` - This file
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI-specific documentation
- `SPEC.md` - Module specification
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [llm](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
