"""RAG pipeline: context formatting and end-to-end retrieval-augmented generation."""

from collections.abc import Callable

from .models import Document, GenerationContext, RetrievalResult
from .splitters import RecursiveTextSplitter, TextSplitter
from .vectorstore import InMemoryVectorStore, VectorStore

RAG_PROMPT_TEMPLATE = """Use the following context to answer the question. If the answer is not in the context, say "I don't have enough information to answer that."

Context:
{context}

Question: {query}

Answer:"""


class ContextFormatter:
    """Format retrieved results into context for LLM."""

    def __init__(
        self,
        template: str = "Source {i}:\n{content}\n",
        max_context_length: int = 4000,
        include_metadata: bool = False,
    ):
        self.template = template
        self.max_context_length = max_context_length
        self.include_metadata = include_metadata

    def format(self, results: list[RetrievalResult]) -> str:
        """Format results into context string."""
        parts = []
        total_length = 0

        for i, result in enumerate(results, 1):
            content = result.content
            if self.include_metadata and result.chunk.metadata:
                content = f"[{result.chunk.metadata}]\n{content}"

            part = self.template.format(i=i, content=content, score=result.score)

            if total_length + len(part) > self.max_context_length:
                remaining = self.max_context_length - total_length
                if remaining > 100:
                    parts.append(part[:remaining] + "...")
                break

            parts.append(part)
            total_length += len(part)

        return "\n".join(parts)


class RAGPipeline:
    """
    Complete RAG pipeline.

    Usage:
        pipeline = RAGPipeline(
            embedding_fn=lambda texts: [embed(t) for t in texts],
            vector_store=InMemoryVectorStore(),
        )
        doc = Document.from_text("Your long document here...")
        pipeline.index_document(doc)
        results = pipeline.retrieve("What is the main topic?", k=3)
        context = pipeline.build_context("What is the main topic?", k=3)
        response = llm.complete(f"Context:\\n{context.formatted_context}\\n\\nQuestion: {context.query}")
    """

    def __init__(
        self,
        embedding_fn: Callable[[list[str]], list[list[float]]],
        vector_store: VectorStore | None = None,
        text_splitter: TextSplitter | None = None,
        context_formatter: ContextFormatter | None = None,
    ):
        self.embedding_fn = embedding_fn
        self.vector_store = vector_store or InMemoryVectorStore()
        self.text_splitter = text_splitter or RecursiveTextSplitter()
        self.context_formatter = context_formatter or ContextFormatter()
        self._documents: dict[str, Document] = {}

    def index_document(self, document: Document) -> int:
        """Index a document for retrieval. Returns number of chunks indexed."""
        self._documents[document.id] = document
        chunks = self.text_splitter.split(document)
        texts = [c.content for c in chunks]
        embeddings = self.embedding_fn(texts)

        for chunk, embedding in zip(chunks, embeddings, strict=False):
            chunk.embedding = embedding

        self.vector_store.add(chunks)
        return len(chunks)

    def index_documents(self, documents: list[Document]) -> int:
        """Index multiple documents."""
        total = 0
        for doc in documents:
            total += self.index_document(doc)
        return total

    def retrieve(self, query: str, k: int = 5) -> list[RetrievalResult]:
        """Retrieve relevant chunks for a query."""
        query_embedding = self.embedding_fn([query])[0]
        results = self.vector_store.search(query_embedding, k=k)

        for result in results:
            doc_id = result.chunk.document_id
            if doc_id in self._documents:
                result.document = self._documents[doc_id]

        return results

    def build_context(self, query: str, k: int = 5) -> GenerationContext:
        """Build generation context from retrieval."""
        results = self.retrieve(query, k=k)
        formatted = self.context_formatter.format(results)

        return GenerationContext(
            query=query,
            retrieved=results,
            formatted_context=formatted,
            metadata={
                "num_chunks": len(results),
                "avg_score": sum(r.score for r in results) / len(results)
                if results
                else 0,
            },
        )

    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its chunks."""
        if document_id in self._documents:
            del self._documents[document_id]
            self.vector_store.delete(document_id)
            return True
        return False

    @property
    def document_count(self) -> int:
        """Get number of indexed documents."""
        return len(self._documents)


def create_rag_prompt(context: GenerationContext) -> str:
    """Create a RAG prompt from generation context."""
    return RAG_PROMPT_TEMPLATE.format(
        context=context.formatted_context,
        query=context.query,
    )
