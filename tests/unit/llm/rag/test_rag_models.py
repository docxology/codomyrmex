"""Tests for llm.rag.models."""

from codomyrmex.llm.rag.models import (
    Chunk,
    Document,
    DocumentType,
    GenerationContext,
    RetrievalResult,
)


class TestDocumentType:
    def test_all_values(self):
        values = {t.value for t in DocumentType}
        assert "text" in values
        assert "markdown" in values
        assert "html" in values
        assert "pdf" in values
        assert "code" in values


class TestDocument:
    def test_construction(self):
        doc = Document(id="doc-1", content="Hello world.")
        assert doc.id == "doc-1"
        assert doc.content == "Hello world."
        assert doc.doc_type == DocumentType.TEXT
        assert doc.source is None

    def test_content_hash(self):
        doc = Document(id="d1", content="same content")
        doc2 = Document(id="d2", content="same content")
        assert doc.content_hash == doc2.content_hash

    def test_content_hash_different(self):
        doc1 = Document(id="d1", content="content A")
        doc2 = Document(id="d2", content="content B")
        assert doc1.content_hash != doc2.content_hash

    def test_content_hash_length(self):
        doc = Document(id="d1", content="test")
        assert len(doc.content_hash) == 32  # MD5 hex

    def test_from_text(self):
        doc = Document.from_text("Some plain text.")
        assert doc.content == "Some plain text."
        assert doc.doc_type == DocumentType.TEXT

    def test_from_text_with_id(self):
        doc = Document.from_text("Hello", doc_id="custom-id")
        assert doc.id == "custom-id"

    def test_from_text_id_auto_generated(self):
        doc = Document.from_text("Auto ID content")
        assert len(doc.id) == 12

    def test_from_text_metadata(self):
        doc = Document.from_text("Content", author="Alice", version=2)
        assert doc.metadata["author"] == "Alice"
        assert doc.metadata["version"] == 2

    def test_from_file(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("# Hello markdown")
        doc = Document.from_file(str(f))
        assert doc.content == "# Hello markdown"
        assert doc.doc_type == DocumentType.MARKDOWN
        assert doc.id == "test"

    def test_from_file_python(self, tmp_path):
        f = tmp_path / "script.py"
        f.write_text("print('hello')")
        doc = Document.from_file(str(f))
        assert doc.doc_type == DocumentType.CODE

    def test_from_file_html(self, tmp_path):
        f = tmp_path / "page.html"
        f.write_text("<html>hello</html>")
        doc = Document.from_file(str(f))
        assert doc.doc_type == DocumentType.HTML

    def test_from_file_unknown_ext(self, tmp_path):
        f = tmp_path / "data.csv"
        f.write_text("a,b,c")
        doc = Document.from_file(str(f))
        assert doc.doc_type == DocumentType.TEXT

    def test_independent_default_metadata(self):
        d1 = Document(id="a", content="a")
        d2 = Document(id="b", content="b")
        d1.metadata["x"] = 1
        assert d2.metadata == {}


class TestChunk:
    def test_construction(self):
        c = Chunk(
            id="c-1",
            content="First chunk content.",
            document_id="doc-1",
            sequence=0,
            start_char=0,
            end_char=20,
        )
        assert c.id == "c-1"
        assert c.document_id == "doc-1"
        assert c.sequence == 0

    def test_length_property(self):
        c = Chunk(
            id="c",
            content="hello",
            document_id="d",
            sequence=0,
            start_char=0,
            end_char=5,
        )
        assert c.length == 5

    def test_embedding_default_none(self):
        c = Chunk(
            id="c",
            content="text",
            document_id="d",
            sequence=0,
            start_char=0,
            end_char=4,
        )
        assert c.embedding is None

    def test_with_embedding(self):
        emb = [0.1, 0.2, 0.3]
        c = Chunk(
            id="c",
            content="text",
            document_id="d",
            sequence=0,
            start_char=0,
            end_char=4,
            embedding=emb,
        )
        assert c.embedding == [0.1, 0.2, 0.3]


class TestRetrievalResult:
    def _make_chunk(self) -> Chunk:
        return Chunk(
            id="c-1",
            content="Retrieved content.",
            document_id="d-1",
            sequence=0,
            start_char=0,
            end_char=18,
        )

    def test_construction(self):
        chunk = self._make_chunk()
        r = RetrievalResult(chunk=chunk, score=0.85)
        assert r.score == 0.85
        assert r.document is None

    def test_content_property(self):
        chunk = self._make_chunk()
        r = RetrievalResult(chunk=chunk, score=0.9)
        assert r.content == "Retrieved content."

    def test_with_document(self):
        chunk = self._make_chunk()
        doc = Document(id="d-1", content="Full doc.")
        r = RetrievalResult(chunk=chunk, score=0.75, document=doc)
        assert r.document is not None
        assert r.document.id == "d-1"


class TestGenerationContext:
    def _make_result(self, content: str, score: float) -> RetrievalResult:
        chunk = Chunk(
            id="c",
            content=content,
            document_id="d",
            sequence=0,
            start_char=0,
            end_char=len(content),
        )
        return RetrievalResult(chunk=chunk, score=score)

    def test_construction(self):
        ctx = GenerationContext(
            query="What is RAG?",
            retrieved=[],
            formatted_context="",
        )
        assert ctx.query == "What is RAG?"
        assert ctx.num_sources == 0

    def test_num_sources(self):
        r1 = self._make_result("source 1", 0.9)
        r2 = self._make_result("source 2", 0.8)
        ctx = GenerationContext(
            query="query",
            retrieved=[r1, r2],
            formatted_context="context",
        )
        assert ctx.num_sources == 2

    def test_formatted_context(self):
        ctx = GenerationContext(
            query="q",
            retrieved=[],
            formatted_context="Formatted context here.",
        )
        assert ctx.formatted_context == "Formatted context here."

    def test_independent_default_metadata(self):
        ctx1 = GenerationContext(query="q1", retrieved=[], formatted_context="")
        ctx2 = GenerationContext(query="q2", retrieved=[], formatted_context="")
        ctx1.metadata["key"] = "val"
        assert ctx2.metadata == {}
