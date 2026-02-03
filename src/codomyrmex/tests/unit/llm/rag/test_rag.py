"""
Tests for LLM RAG Module
"""

import pytest
from codomyrmex.llm.rag import (
    Document,
    DocumentType,
    Chunk,
    RetrievalResult,
    RecursiveTextSplitter,
    SentenceSplitter,
    InMemoryVectorStore,
    ContextFormatter,
    RAGPipeline,
    create_rag_prompt,
)


class TestDocument:
    """Tests for Document class."""
    
    def test_from_text(self):
        """Should create from text."""
        doc = Document.from_text("Hello world", doc_id="test")
        assert doc.id == "test"
        assert doc.content == "Hello world"
        assert doc.doc_type == DocumentType.TEXT
    
    def test_content_hash(self):
        """Should compute content hash."""
        doc = Document.from_text("test content")
        assert doc.content_hash is not None
        assert len(doc.content_hash) == 32  # MD5 hex


class TestRecursiveTextSplitter:
    """Tests for RecursiveTextSplitter."""
    
    def test_split_by_paragraphs(self):
        """Should split by paragraphs first."""
        splitter = RecursiveTextSplitter(chunk_size=100)
        doc = Document.from_text("Para one.\n\nPara two.\n\nPara three.")
        
        chunks = splitter.split(doc)
        assert len(chunks) >= 1
        assert all(isinstance(c, Chunk) for c in chunks)
    
    def test_chunk_metadata(self):
        """Chunks should have correct metadata."""
        splitter = RecursiveTextSplitter(chunk_size=50)
        doc = Document.from_text("Short text.", doc_id="doc1")
        
        chunks = splitter.split(doc)
        assert chunks[0].document_id == "doc1"
        assert chunks[0].sequence == 0


class TestSentenceSplitter:
    """Tests for SentenceSplitter."""
    
    def test_split_sentences(self):
        """Should split by sentences."""
        splitter = SentenceSplitter(sentences_per_chunk=2)
        doc = Document.from_text("One. Two. Three. Four. Five.")
        
        chunks = splitter.split(doc)
        assert len(chunks) >= 2


class TestInMemoryVectorStore:
    """Tests for InMemoryVectorStore."""
    
    def test_add_and_search(self):
        """Should add and search chunks."""
        store = InMemoryVectorStore()
        
        chunk = Chunk(
            id="c1",
            content="test content",
            document_id="d1",
            sequence=0,
            start_char=0,
            end_char=12,
            embedding=[1.0, 0.0, 0.0],
        )
        store.add([chunk])
        
        results = store.search([1.0, 0.0, 0.0], k=5)
        
        assert len(results) == 1
        assert results[0].chunk.id == "c1"
        assert results[0].score > 0.99
    
    def test_delete(self):
        """Should delete by document ID."""
        store = InMemoryVectorStore()
        
        store.add([
            Chunk(id="c1", content="a", document_id="d1", sequence=0, start_char=0, end_char=1, embedding=[1.0]),
            Chunk(id="c2", content="b", document_id="d2", sequence=0, start_char=0, end_char=1, embedding=[1.0]),
        ])
        
        deleted = store.delete("d1")
        assert deleted == 1
        assert store.count == 1


class TestContextFormatter:
    """Tests for ContextFormatter."""
    
    def test_format(self):
        """Should format results."""
        formatter = ContextFormatter()
        
        chunk = Chunk(id="c1", content="Test content", document_id="d1", sequence=0, start_char=0, end_char=12)
        results = [RetrievalResult(chunk=chunk, score=0.9)]
        
        context = formatter.format(results)
        
        assert "Test content" in context
        assert "Source 1" in context
    
    def test_max_length(self):
        """Should respect max length."""
        formatter = ContextFormatter(max_context_length=50)
        
        chunks = [
            Chunk(id=f"c{i}", content="Long content here..." * 10, document_id="d", sequence=i, start_char=0, end_char=100)
            for i in range(5)
        ]
        results = [RetrievalResult(chunk=c, score=0.5) for c in chunks]
        
        context = formatter.format(results)
        assert len(context) <= 60  # Allow some buffer for truncation


class TestRAGPipeline:
    """Tests for RAGPipeline."""
    
    @pytest.fixture
    def mock_embed_fn(self):
        """Create mock embedding function."""
        def embed(texts):
            # Simple deterministic embeddings
            return [[hash(t) % 100 / 100 for _ in range(10)] for t in texts]
        return embed
    
    def test_index_document(self, mock_embed_fn):
        """Should index document."""
        pipeline = RAGPipeline(embedding_fn=mock_embed_fn)
        
        doc = Document.from_text("This is test content for indexing.")
        chunks = pipeline.index_document(doc)
        
        assert chunks >= 1
        assert pipeline.document_count == 1
    
    def test_retrieve(self, mock_embed_fn):
        """Should retrieve relevant chunks."""
        pipeline = RAGPipeline(embedding_fn=mock_embed_fn)
        
        doc = Document.from_text("Python is a programming language. It is widely used.")
        pipeline.index_document(doc)
        
        results = pipeline.retrieve("programming language", k=3)
        
        assert len(results) >= 1
        assert all(isinstance(r, RetrievalResult) for r in results)
    
    def test_build_context(self, mock_embed_fn):
        """Should build generation context."""
        pipeline = RAGPipeline(embedding_fn=mock_embed_fn)
        
        doc = Document.from_text("Machine learning is a branch of AI.")
        pipeline.index_document(doc)
        
        context = pipeline.build_context("What is ML?", k=2)
        
        assert context.query == "What is ML?"
        assert len(context.formatted_context) > 0
    
    def test_delete_document(self, mock_embed_fn):
        """Should delete document."""
        pipeline = RAGPipeline(embedding_fn=mock_embed_fn)
        
        doc = Document.from_text("Content", doc_id="to_delete")
        pipeline.index_document(doc)
        
        assert pipeline.delete_document("to_delete") is True
        assert pipeline.document_count == 0


class TestRAGPrompt:
    """Tests for RAG prompt creation."""
    
    def test_create_rag_prompt(self):
        """Should create formatted prompt."""
        from codomyrmex.llm.rag import GenerationContext
        
        chunk = Chunk(id="c1", content="AI content", document_id="d1", sequence=0, start_char=0, end_char=10)
        context = GenerationContext(
            query="What is AI?",
            retrieved=[RetrievalResult(chunk=chunk, score=0.9)],
            formatted_context="Source 1:\nAI content",
        )
        
        prompt = create_rag_prompt(context)
        
        assert "What is AI?" in prompt
        assert "AI content" in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
