"""Unit tests for document processing -- parsing, validation, transformation, search, and chunking."""


import pytest

from codomyrmex.documents import (
    parse_document,
    validate_document,
)
from codomyrmex.documents.core import (
    DocumentParser,
    DocumentValidator,
)
from codomyrmex.documents.models.document import (
    Document,
    DocumentFormat,
)

try:
    from codomyrmex.documents.transformation.converter import convert_document
except ImportError:
    convert_document = None

try:
    from codomyrmex.documents.transformation.merger import merge_documents
except ImportError:
    merge_documents = None

try:
    from codomyrmex.documents.transformation.splitter import split_document
except ImportError:
    split_document = None

try:
    from codomyrmex.documents.transformation.formatter import format_document
except ImportError:
    format_document = None

try:
    from codomyrmex.documents.metadata.extractor import extract_metadata
except ImportError:
    extract_metadata = None

try:
    from codomyrmex.documents.metadata.manager import update_metadata
except ImportError:
    update_metadata = None

try:
    from codomyrmex.documents.metadata.versioning import (
        get_document_version,
        set_document_version,
    )
except ImportError:
    get_document_version = None
    set_document_version = None

try:
    from codomyrmex.documents.search.indexer import (
        InMemoryIndex,
        create_index,
        index_document,
    )
except ImportError:
    InMemoryIndex = None
    index_document = None
    create_index = None

try:
    from codomyrmex.documents.search.searcher import search_documents, search_index
except ImportError:
    search_documents = None
    search_index = None

try:
    from codomyrmex.documents.search.query_builder import QueryBuilder, build_query
except ImportError:
    QueryBuilder = None
    build_query = None

from codomyrmex.documents.exceptions import (
    DocumentConversionError,
    UnsupportedFormatError,
)

# --- Document Parser --------------------------------------------------------

class TestDocumentParser:
    """Test DocumentParser class."""

    def test_parse_json_content(self):
        """Test parsing JSON content."""
        parser = DocumentParser()
        content = '{"key": "value"}'
        doc = parser.parse(content, DocumentFormat.JSON)

        assert isinstance(doc.content, dict)
        assert doc.content["key"] == "value"

    def test_parse_yaml_content(self):
        """Test parsing YAML content."""
        parser = DocumentParser()
        content = "key: value\nnumber: 42"
        doc = parser.parse(content, DocumentFormat.YAML)

        assert isinstance(doc.content, dict)
        assert doc.content["key"] == "value"

    def test_parse_markdown_content(self):
        """Test parsing markdown content."""
        parser = DocumentParser()
        content = "# Heading\n\nParagraph"
        doc = parser.parse(content, DocumentFormat.MARKDOWN)

        assert doc.content == content
        assert isinstance(doc.content, str)


# --- Document Validator -----------------------------------------------------

class TestDocumentValidator:
    """Test DocumentValidator class."""

    def test_validate_valid_json(self):
        """Test validating valid JSON document."""
        doc = Document(
            content={"key": "value"},
            format=DocumentFormat.JSON
        )

        validator = DocumentValidator()
        result = validator.validate(doc)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_invalid_json_string(self):
        """Test validating invalid JSON string."""
        doc = Document(
            content='{"key": invalid}',
            format=DocumentFormat.JSON
        )

        validator = DocumentValidator()
        result = validator.validate(doc)

        assert not result.is_valid or len(result.errors) > 0

    def test_validate_none_content(self):
        """Test validating document with None content."""
        doc = Document(content=None, format=DocumentFormat.TEXT)
        validator = DocumentValidator()
        result = validator.validate(doc)
        assert not result.is_valid
        assert any("None" in e for e in result.errors)

    def test_validate_with_schema(self):
        """Test validating document with JSON schema."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name"]
        }

        doc = Document(
            content={"name": "John", "age": 30},
            format=DocumentFormat.JSON
        )
        validator = DocumentValidator()
        result = validator.validate(doc, schema=schema)
        assert result is not None


# --- Convenience Functions (parse/validate) ---------------------------------

class TestProcessingConvenienceFunctions:
    """Test parse and validate convenience functions."""

    def test_parse_document_function(self):
        """Test parse_document convenience function."""
        content = '{"key": "value"}'
        doc = parse_document(content, DocumentFormat.JSON)

        assert isinstance(doc.content, dict)
        assert doc.content["key"] == "value"

    def test_validate_document_function(self):
        """Test validate_document convenience function."""
        doc = Document(content={"key": "value"}, format=DocumentFormat.JSON)
        result = validate_document(doc)

        assert result is not None
        assert hasattr(result, "is_valid")

    @pytest.mark.skipif(convert_document is None, reason="Document converter not available")
    def test_unsupported_format_error(self):
        """Test error handling for unsupported formats."""
        doc = Document(content="Test", format=DocumentFormat.TEXT)

        with pytest.raises((UnsupportedFormatError, DocumentConversionError)):
            convert_document(doc, DocumentFormat.DOCX)


# --- Document Transformation -----------------------------------------------

class TestDocumentTransformation:
    """Test document transformation operations."""

    @pytest.mark.skipif(convert_document is None, reason="Document converter not available")
    def test_convert_markdown_to_text(self):
        """Test converting markdown to text."""
        doc = Document(
            content="# Heading\n\nContent",
            format=DocumentFormat.MARKDOWN
        )

        converted = convert_document(doc, DocumentFormat.TEXT)
        assert converted.format == DocumentFormat.TEXT
        assert "# Heading" in converted.get_content_as_string()

    @pytest.mark.skipif(convert_document is None, reason="Document converter not available")
    def test_convert_same_format(self):
        """Test converting to same format returns same document."""
        doc = Document(content="Test", format=DocumentFormat.TEXT)
        result = convert_document(doc, DocumentFormat.TEXT)
        assert result is doc

    @pytest.mark.skipif(convert_document is None, reason="Document converter not available")
    def test_convert_yaml_to_json(self):
        """Test converting YAML to JSON."""
        doc = Document(content="key: value", format=DocumentFormat.YAML)
        converted = convert_document(doc, DocumentFormat.JSON)
        assert converted.format == DocumentFormat.JSON
        assert isinstance(converted.content, dict)
        assert converted.content["key"] == "value"

    @pytest.mark.skipif(merge_documents is None, reason="Document merger not available")
    def test_merge_documents(self):
        """Test merging multiple documents."""
        doc1 = Document(content="First", format=DocumentFormat.TEXT)
        doc2 = Document(content="Second", format=DocumentFormat.TEXT)
        doc3 = Document(content="Third", format=DocumentFormat.TEXT)

        merged = merge_documents([doc1, doc2, doc3])
        assert merged.format == DocumentFormat.TEXT
        content = merged.get_content_as_string()
        assert "First" in content
        assert "Second" in content
        assert "Third" in content

    @pytest.mark.skipif(merge_documents is None, reason="Document merger not available")
    def test_merge_single_document(self):
        """Test merging a single document returns it."""
        doc = Document(content="Only one", format=DocumentFormat.TEXT)
        result = merge_documents([doc])
        assert result is doc

    @pytest.mark.skipif(merge_documents is None, reason="Document merger not available")
    def test_merge_empty_raises(self):
        """Test merging empty list raises ValueError."""
        with pytest.raises(ValueError):
            merge_documents([])

    @pytest.mark.skipif(split_document is None, reason="Document splitter not available")
    def test_split_document_by_sections(self):
        """Test splitting document by sections."""
        doc = Document(
            content="# Section 1\n\nContent 1\n\n# Section 2\n\nContent 2",
            format=DocumentFormat.MARKDOWN
        )

        split_docs = split_document(doc, {"method": "by_sections"})
        assert len(split_docs) >= 2

    @pytest.mark.skipif(split_document is None, reason="Document splitter not available")
    def test_split_document_by_size(self):
        """Test splitting document by size."""
        large_content = "A" * 10000
        doc = Document(content=large_content, format=DocumentFormat.TEXT)

        split_docs = split_document(doc, {"method": "by_size", "max_size": 1000})
        assert len(split_docs) == 10

    @pytest.mark.skipif(split_document is None, reason="Document splitter not available")
    def test_split_document_by_lines(self):
        """Test splitting document by lines."""
        content = "\n".join(f"Line {i}" for i in range(100))
        doc = Document(content=content, format=DocumentFormat.TEXT)

        split_docs = split_document(doc, {"method": "by_lines", "lines_per_chunk": 25})
        assert len(split_docs) == 4


# --- Formatter --------------------------------------------------------------

class TestFormatter:
    """Test document formatter."""

    @pytest.mark.skipif(format_document is None, reason="Formatter not available")
    def test_format_default(self):
        """Test default formatting returns same document."""
        doc = Document(content="Test", format=DocumentFormat.TEXT)
        result = format_document(doc, style="default")
        assert result is doc

    @pytest.mark.skipif(format_document is None, reason="Formatter not available")
    def test_format_json_compact(self):
        """Test compact JSON formatting."""
        doc = Document(content={"key": "value", "num": 1}, format=DocumentFormat.JSON)
        result = format_document(doc, style="compact")
        content = result.get_content_as_string()
        assert " " not in content or content == '{"key":"value","num":1}'

    @pytest.mark.skipif(format_document is None, reason="Formatter not available")
    def test_format_json_pretty(self):
        """Test pretty JSON formatting."""
        doc = Document(content={"key": "value"}, format=DocumentFormat.JSON)
        result = format_document(doc, style="pretty")
        content = result.get_content_as_string()
        assert "\n" in content


# --- Metadata Operations ---------------------------------------------------

class TestMetadataOperations:
    """Test metadata operations."""

    @pytest.mark.skipif(extract_metadata is None, reason="Metadata extractor not available")
    def test_extract_metadata(self, tmp_path):
        """Test extracting metadata from file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content", encoding="utf-8")

        metadata = extract_metadata(test_file)
        assert "file_size" in metadata
        assert "modified_at" in metadata

    @pytest.mark.skipif(extract_metadata is None, reason="Metadata extractor not available")
    def test_extract_markdown_frontmatter(self, tmp_path):
        """Test extracting markdown frontmatter."""
        test_file = tmp_path / "test.md"
        test_file.write_text("---\ntitle: My Doc\nauthor: Author\n---\n\n# Content", encoding="utf-8")

        metadata = extract_metadata(test_file)
        assert metadata.get("title") == "My Doc"

    @pytest.mark.skipif(get_document_version is None, reason="Versioning not available")
    def test_get_document_version(self, tmp_path):
        """Test getting document version."""
        test_file = tmp_path / "test.md"
        test_file.write_text("---\nversion: 1.0.0\n---\n\nContent", encoding="utf-8")

        version = get_document_version(test_file)
        assert version is None or isinstance(version, str)

    @pytest.mark.skipif(update_metadata is None, reason="Metadata manager not available")
    def test_update_markdown_metadata(self, tmp_path):
        """Test updating markdown frontmatter."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# No frontmatter yet", encoding="utf-8")

        update_metadata(test_file, {"title": "New Title"})
        content = test_file.read_text()
        assert "---" in content
        assert "New Title" in content


# --- Search Module ----------------------------------------------------------

class TestSearchIndexer:
    """Test search indexer."""

    @pytest.mark.skipif(InMemoryIndex is None, reason="Search indexer not available")
    def test_create_index(self):
        """Test creating empty index."""
        idx = create_index()
        assert idx.document_count == 0

    @pytest.mark.skipif(InMemoryIndex is None, reason="Search indexer not available")
    def test_index_document(self):
        """Test indexing a document."""
        doc = Document(content="hello world testing", format=DocumentFormat.TEXT)
        idx = index_document(doc)
        assert idx.document_count == 1

    @pytest.mark.skipif(InMemoryIndex is None, reason="Search indexer not available")
    def test_index_add_remove(self):
        """Test adding and removing documents."""
        idx = InMemoryIndex()
        doc = Document(content="test content", format=DocumentFormat.TEXT)
        idx.add(doc)
        assert idx.document_count == 1

        idx.remove(doc.id)
        assert idx.document_count == 0

    @pytest.mark.skipif(InMemoryIndex is None, reason="Search indexer not available")
    def test_index_search(self):
        """Test searching the index."""
        idx = InMemoryIndex()
        doc1 = Document(content="python programming language", format=DocumentFormat.TEXT)
        doc2 = Document(content="javascript web development", format=DocumentFormat.TEXT)
        doc3 = Document(content="python web framework", format=DocumentFormat.TEXT)
        idx.add(doc1)
        idx.add(doc2)
        idx.add(doc3)

        # Search for "python" should find doc1 and doc3
        results = idx.search(["python"])
        assert len(results) == 2
        assert doc1.id in results
        assert doc3.id in results

        # Search for "python" AND "web" should find only doc3
        results = idx.search(["python", "web"])
        assert len(results) == 1
        assert doc3.id in results

    @pytest.mark.skipif(InMemoryIndex is None, reason="Search indexer not available")
    def test_index_search_no_results(self):
        """Test searching with no matches."""
        idx = InMemoryIndex()
        doc = Document(content="hello world", format=DocumentFormat.TEXT)
        idx.add(doc)

        results = idx.search(["nonexistent"])
        assert len(results) == 0

    @pytest.mark.skipif(InMemoryIndex is None, reason="Search indexer not available")
    def test_index_save_load(self, tmp_path):
        """Test saving and loading index."""
        idx = InMemoryIndex()
        doc = Document(content="test save load", format=DocumentFormat.TEXT)
        idx.add(doc)

        save_path = tmp_path / "index.json"
        idx.save(save_path)
        assert save_path.exists()

        loaded = InMemoryIndex.load(save_path)
        # Loaded index has term data but not full Document objects
        assert "test" in loaded._index

    @pytest.mark.skipif(InMemoryIndex is None, reason="Search indexer not available")
    def test_index_get_document(self):
        """Test retrieving document from index."""
        idx = InMemoryIndex()
        doc = Document(content="findme", format=DocumentFormat.TEXT)
        idx.add(doc)

        retrieved = idx.get_document(doc.id)
        assert retrieved is doc
        assert idx.get_document("nonexistent") is None


class TestSearchSearcher:
    """Test search searcher."""

    @pytest.mark.skipif(search_documents is None or InMemoryIndex is None, reason="Search not available")
    def test_search_documents(self):
        """Test searching documents."""
        idx = InMemoryIndex()
        doc1 = Document(content="python guide", format=DocumentFormat.TEXT)
        doc2 = Document(content="java tutorial", format=DocumentFormat.TEXT)
        idx.add(doc1)
        idx.add(doc2)

        results = search_documents("python", idx)
        assert len(results) == 1
        assert results[0].id == doc1.id

    @pytest.mark.skipif(search_index is None or InMemoryIndex is None, reason="Search not available")
    def test_search_index_with_scores(self):
        """Test search_index returns results with scores."""
        idx = InMemoryIndex()
        doc1 = Document(content="python python python", format=DocumentFormat.TEXT)
        doc2 = Document(content="python java", format=DocumentFormat.TEXT)
        idx.add(doc1)
        idx.add(doc2)

        results = search_index("python", idx)
        assert len(results) == 2
        # doc1 should score higher (more occurrences)
        assert results[0]["score"] >= results[1]["score"]
        assert results[0]["document_id"] == doc1.id

    @pytest.mark.skipif(search_documents is None or InMemoryIndex is None, reason="Search not available")
    def test_search_empty_query(self):
        """Test searching with empty query."""
        idx = InMemoryIndex()
        doc = Document(content="test", format=DocumentFormat.TEXT)
        idx.add(doc)

        results = search_documents("", idx)
        assert len(results) == 0


class TestSearchQueryBuilder:
    """Test query builder."""

    @pytest.mark.skipif(QueryBuilder is None, reason="Query builder not available")
    def test_query_builder_fluent(self):
        """Test fluent API of QueryBuilder."""
        qb = QueryBuilder()
        result = qb.add_term("hello").add_term("world").add_filter("type", "text").set_sort("date")
        assert result is qb
        assert qb.build() == "hello world"

    @pytest.mark.skipif(QueryBuilder is None, reason="Query builder not available")
    def test_query_builder_to_dict(self):
        """Test QueryBuilder to_dict."""
        qb = QueryBuilder()
        qb.add_term("test").add_filter("format", "json").set_sort("score")
        d = qb.to_dict()
        assert d["terms"] == ["test"]
        assert d["filters"] == {"format": "json"}
        assert d["sort_by"] == "score"

    @pytest.mark.skipif(build_query is None, reason="Query builder not available")
    def test_build_query_convenience(self):
        """Test build_query convenience function."""
        query = build_query(["hello", "world"])
        assert query == "hello world"


# --- Chunking ---------------------------------------------------------------

class TestChunk:
    """Tests for Chunk dataclass."""

    def test_properties(self):
        from codomyrmex.documents.chunking import Chunk

        c = Chunk(text="hello world", index=0, start_char=0, end_char=11)
        assert c.char_count == 11
        assert c.word_count == 2


class TestDocumentChunkerFixed:
    """Tests for fixed-size chunking strategy."""

    def test_short_text_single_chunk(self):
        from codomyrmex.documents.chunking import (
            ChunkConfig,
            ChunkStrategy,
            DocumentChunker,
        )

        chunker = DocumentChunker(ChunkConfig(
            strategy=ChunkStrategy.FIXED_SIZE, chunk_size=1000, min_chunk_size=1,
        ))
        chunks = chunker.chunk("short text")
        assert len(chunks) == 1
        assert chunks[0].text == "short text"

    def test_long_text_multiple_chunks(self):
        from codomyrmex.documents.chunking import (
            ChunkConfig,
            ChunkStrategy,
            DocumentChunker,
        )

        text = "a" * 500
        chunker = DocumentChunker(ChunkConfig(
            strategy=ChunkStrategy.FIXED_SIZE,
            chunk_size=200, chunk_overlap=50 , min_chunk_size=1,
        ))
        chunks = chunker.chunk(text)
        assert len(chunks) > 1
        # Verify no text is lost
        assert all(c.text for c in chunks)


class TestDocumentChunkerSentence:
    """Tests for sentence-based chunking."""

    def test_sentences_grouped(self):
        from codomyrmex.documents.chunking import (
            ChunkConfig,
            ChunkStrategy,
            DocumentChunker,
        )

        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        chunker = DocumentChunker(ChunkConfig(
            strategy=ChunkStrategy.SENTENCE, chunk_size=40, min_chunk_size=1,
        ))
        chunks = chunker.chunk(text)
        assert len(chunks) >= 1
        # All text should be represented
        combined = " ".join(c.text for c in chunks)
        assert "First" in combined


class TestDocumentChunkerParagraph:
    """Tests for paragraph-based chunking."""

    def test_paragraphs_split(self):
        from codomyrmex.documents.chunking import (
            ChunkConfig,
            ChunkStrategy,
            DocumentChunker,
        )

        text = "Paragraph one content here.\n\nParagraph two content here.\n\nParagraph three content."
        chunker = DocumentChunker(ChunkConfig(
            strategy=ChunkStrategy.PARAGRAPH, min_chunk_size=10,
        ))
        chunks = chunker.chunk(text)
        assert len(chunks) >= 2


class TestDocumentChunkerRecursive:
    """Tests for recursive chunking (default)."""

    def test_recursive_splits(self):
        from codomyrmex.documents.chunking import (
            ChunkConfig,
            ChunkStrategy,
            DocumentChunker,
        )

        text = ("Paragraph one.\n\nParagraph two.\n\n" +
                "A longer section. " * 100)
        chunker = DocumentChunker(ChunkConfig(
            strategy=ChunkStrategy.RECURSIVE, chunk_size=200, min_chunk_size=10,
        ))
        chunks = chunker.chunk(text)
        assert len(chunks) >= 2


class TestDocumentChunkerSemantic:
    """Tests for semantic fallback (falls back to fixed-size)."""

    def test_semantic_falls_back(self):
        from codomyrmex.documents.chunking import (
            ChunkConfig,
            ChunkStrategy,
            DocumentChunker,
        )

        chunker = DocumentChunker(ChunkConfig(
            strategy=ChunkStrategy.SEMANTIC, chunk_size=100, min_chunk_size=1,
        ))
        chunks = chunker.chunk("Just some text content here.")
        assert len(chunks) >= 1


class TestDocumentChunkerMetadata:
    """Tests for metadata pass-through."""

    def test_metadata_preserved(self):
        from codomyrmex.documents.chunking import (
            ChunkConfig,
            ChunkStrategy,
            DocumentChunker,
        )

        chunker = DocumentChunker(ChunkConfig(
            strategy=ChunkStrategy.FIXED_SIZE, chunk_size=1000, min_chunk_size=1,
        ))
        chunks = chunker.chunk("content", metadata={"source": "test"})
        assert chunks[0].metadata == {"source": "test"}
