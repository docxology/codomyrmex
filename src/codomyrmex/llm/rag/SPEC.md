# Technical Specification - Rag

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.llm.rag`  
**Last Updated**: 2026-01-29

## 1. Purpose

Retrieval-Augmented Generation pipeline with document processing

## 2. Architecture

### 2.1 Components

```
rag/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `llm`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.llm.rag
from codomyrmex.llm.rag import (
    DocumentType,             # Enum: TEXT, MARKDOWN, HTML, PDF, CODE
    Document,                 # Dataclass: id + content + doc_type + source + metadata; from_text(), from_file()
    Chunk,                    # Dataclass: id + content + document_id + sequence + char offsets + optional embedding
    RetrievalResult,          # Dataclass: chunk + score + optional parent document
    GenerationContext,        # Dataclass: query + retrieved results + formatted_context string
    TextSplitter,             # ABC for text splitting strategies
    RecursiveTextSplitter,    # Split by separators ("\n\n", "\n", ". ", " ", "") with configurable chunk_size/overlap
    SentenceSplitter,         # Split by sentence boundaries with configurable sentences_per_chunk/overlap
    VectorStore,              # ABC for vector storage (add, search, delete)
    InMemoryVectorStore,      # Simple in-memory cosine-similarity vector store
    ContextFormatter,         # Format retrieval results into LLM-ready context strings
    RAGPipeline,              # End-to-end pipeline: index documents -> retrieve -> build context
    RAG_PROMPT_TEMPLATE,      # Default RAG prompt template string
    create_rag_prompt,        # Helper to render RAG_PROMPT_TEMPLATE from a GenerationContext
)

# Key class signatures:
class RAGPipeline:
    def __init__(self, embedding_fn: Callable[[list[str]], list[list[float]]], vector_store: VectorStore | None = None,
                 text_splitter: TextSplitter | None = None, context_formatter: ContextFormatter | None = None): ...
    def index_document(self, document: Document) -> int: ...
    def index_documents(self, documents: list[Document]) -> int: ...
    def retrieve(self, query: str, k: int = 5) -> list[RetrievalResult]: ...
    def build_context(self, query: str, k: int = 5) -> GenerationContext: ...
    def delete_document(self, document_id: str) -> bool: ...

class Document:
    @classmethod
    def from_text(cls, text: str, doc_id: str | None = None, **metadata) -> Document: ...
    @classmethod
    def from_file(cls, path: str, encoding: str = "utf-8") -> Document: ...

class RecursiveTextSplitter(TextSplitter):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, separators: list[str] | None = None): ...
    def split(self, document: Document) -> list[Chunk]: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Embedding function injected as a callable**: `RAGPipeline` accepts `embedding_fn: Callable[[list[str]], list[list[float]]]` rather than coupling to a specific provider, keeping the pipeline agnostic.
2. **Recursive text splitting with separator fallback**: `RecursiveTextSplitter` tries `["\n\n", "\n", ". ", " ", ""]` in order, falling back to finer-grained separators only when chunks exceed `chunk_size`.
3. **Context length budget in formatter**: `ContextFormatter.max_context_length` truncates retrieved content to fit within the LLM's context window.

### 4.2 Limitations

- `InMemoryVectorStore` performs brute-force cosine similarity; not suitable for large corpora.
- PDF document type is declared in `DocumentType` but `Document.from_file` does not parse PDF content -- only text-based formats are read.
- No de-duplication of overlapping chunks across multiple `index_document` calls for the same document.

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/llm/rag/
```

## 6. Future Considerations

- Add hybrid retrieval combining keyword (BM25) and vector search
- Support PDF parsing via `Document.from_file` for the `PDF` document type
- Add metadata-filtered retrieval (e.g., filter by document source or date)
