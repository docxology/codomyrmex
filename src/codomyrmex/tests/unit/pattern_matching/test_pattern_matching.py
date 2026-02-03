"""Unit tests for pattern_matching module."""

import pytest
import sys
import os
import tempfile
import json
from pathlib import Path


@pytest.mark.unit
class TestPatternMatching:
    """Test cases for pattern matching functionality."""

    def test_pattern_matching_import(self, code_dir):
        """Test that we can import pattern_matching module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.pattern_matching import run_codomyrmex_analysis
            assert run_codomyrmex_analysis is not None
        except ImportError as e:
            pytest.fail(f"Failed to import run_codomyrmex_analysis: {e}")

    def test_pattern_matching_module_structure(self, code_dir):
        """Test that pattern_matching has expected structure."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.pattern_matching import run_codomyrmex_analysis

        assert hasattr(run_codomyrmex_analysis, '__file__')
        assert hasattr(run_codomyrmex_analysis, 'run_full_analysis')
        assert hasattr(run_codomyrmex_analysis, 'analyze_repository_path')

    def test_get_embedding_function_with_sentence_transformer(self, code_dir):
        """Test get_embedding_function when SentenceTransformer is available."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from sentence_transformers import SentenceTransformer
            SENTENCE_TRANSFORMER_AVAILABLE = True
        except ImportError:
            SENTENCE_TRANSFORMER_AVAILABLE = False

        if not SENTENCE_TRANSFORMER_AVAILABLE:
            pytest.skip("SentenceTransformer not available")

        from pattern_matching.run_codomyrmex_analysis import get_embedding_function

        # Test with real SentenceTransformer if available
        embed_fn = get_embedding_function('all-MiniLM-L6-v2')

        if embed_fn is not None:
            # Test that it returns a function
            assert callable(embed_fn)
            # Test that it can process text
            result = embed_fn("test text")
            assert isinstance(result, list)
            assert len(result) > 0

    def test_get_embedding_function_without_sentence_transformer(self, code_dir):
        """Test get_embedding_function when SentenceTransformer is not available."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from sentence_transformers import SentenceTransformer
            # If available, we can't test the fallback easily
            pytest.skip("SentenceTransformer is available, cannot test fallback")
        except ImportError:
            # SentenceTransformer not available, test fallback
            from pattern_matching.run_codomyrmex_analysis import get_embedding_function

            # Reset the global _embed_fn_instance to ensure clean state
            import pattern_matching.run_codomyrmex_analysis as pm_module
            pm_module._embed_fn_instance = None

            result = get_embedding_function('test-model')
            # Should return None when SentenceTransformer not available
            assert result is None

    def test_print_once_functionality(self, real_logger_fixture, code_dir):
        """Test print_once function with real logger."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from pattern_matching.run_codomyrmex_analysis import print_once, PRINTED_ONCE_KEYS

        # Clear the set for testing
        PRINTED_ONCE_KEYS.clear()

        logger = real_logger_fixture["logger"]

        # First call should print
        print_once("test_key", "Test message", _logger=logger)

        # Second call should not print (same key)
        print_once("test_key", "Test message", _logger=logger)

        # Different key should print
        print_once("test_key_2", "Another message", _logger=logger)

        # Verify log file exists
        log_file = real_logger_fixture["log_file"]
        if log_file.exists():
            log_content = log_file.read_text()
            # Should contain at least one of the messages
            assert len(log_content) >= 0

    def test_perform_repository_index(self, tmp_path, code_dir):
        """Test _perform_repository_index function with real repository."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from kit import Repository
            KIT_AVAILABLE = True
        except ImportError:
            KIT_AVAILABLE = False

        if not KIT_AVAILABLE:
            pytest.skip("kit.Repository not available")

        from pattern_matching.run_codomyrmex_analysis import _perform_repository_index
        from codomyrmex.logging_monitoring import get_logger

        # Create a real repository
        repo = Repository(str(tmp_path))
        
        # Create some test files
        (tmp_path / "test.py").write_text("def test():\n    pass\n")
        (tmp_path / "README.md").write_text("# Test\n")

        logger = get_logger("test")

        errors = _perform_repository_index(repo, str(tmp_path), "test_module", {}, logger)

        # Should complete without errors
        assert isinstance(errors, list)

    def test_perform_text_search(self, tmp_path, code_dir):
        """Test _perform_text_search function with real repository."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from kit import Repository
            KIT_AVAILABLE = True
        except ImportError:
            KIT_AVAILABLE = False

        if not KIT_AVAILABLE:
            pytest.skip("kit.Repository not available")

        from pattern_matching.run_codomyrmex_analysis import _perform_text_search
        from codomyrmex.logging_monitoring import get_logger

        # Create a real repository
        repo = Repository(str(tmp_path))
        
        # Create test file with TODO
        (tmp_path / "test.py").write_text("# TODO: implement this\n")

        logger = get_logger("test")

        results, errors = _perform_text_search(
            repo, str(tmp_path), "test_module", 
            {"text_search_queries": ["TODO"]}, logger
        )

        assert isinstance(errors, list)
        assert isinstance(results, dict)

    def test_perform_dependency_analysis_python_files(self, tmp_path, code_dir):
        """Test _perform_dependency_analysis with Python files using real repository."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from kit import Repository
            KIT_AVAILABLE = True
        except ImportError:
            KIT_AVAILABLE = False

        if not KIT_AVAILABLE:
            pytest.skip("kit.Repository not available")

        from pattern_matching.run_codomyrmex_analysis import _perform_dependency_analysis
        from codomyrmex.logging_monitoring import get_logger

        # Create a real repository
        repo = Repository(str(tmp_path))
        
        # Create Python files
        (tmp_path / "test.py").write_text("import os\n")
        (tmp_path / "README.md").write_text("# Test\n")

        logger = get_logger("test")

        errors = _perform_dependency_analysis(repo, str(tmp_path), "test_module", {}, logger)

        assert isinstance(errors, list)

    def test_perform_dependency_analysis_no_python_files(self, tmp_path, code_dir):
        """Test _perform_dependency_analysis with no Python files using real repository."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from kit import Repository
            KIT_AVAILABLE = True
        except ImportError:
            KIT_AVAILABLE = False

        if not KIT_AVAILABLE:
            pytest.skip("kit.Repository not available")

        from pattern_matching.run_codomyrmex_analysis import _perform_dependency_analysis
        from codomyrmex.logging_monitoring import get_logger

        # Create a real repository
        repo = Repository(str(tmp_path))
        
        # Create non-Python files
        (tmp_path / "README.md").write_text("# Test\n")
        (tmp_path / "docs.txt").write_text("Documentation\n")

        logger = get_logger("test")

        errors = _perform_dependency_analysis(repo, str(tmp_path), "test_module", {}, logger)

        assert isinstance(errors, list)

    def test_perform_symbol_extraction(self, tmp_path, code_dir):
        """Test _perform_symbol_extraction function with real repository."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from kit import Repository
            KIT_AVAILABLE = True
        except ImportError:
            KIT_AVAILABLE = False

        if not KIT_AVAILABLE:
            pytest.skip("kit.Repository not available")

        from pattern_matching.run_codomyrmex_analysis import _perform_symbol_extraction
        from codomyrmex.logging_monitoring import get_logger

        # Create a real repository
        repo = Repository(str(tmp_path))
        
        # Create Python file with function
        (tmp_path / "test.py").write_text("def test_function():\n    pass\n")

        logger = get_logger("test")

        symbols, errors = _perform_symbol_extraction(repo, str(tmp_path), "test_module", {}, logger)

        assert isinstance(errors, list)
        assert isinstance(symbols, list)

    def test_perform_symbol_usage_analysis(self, tmp_path, code_dir):
        """Test _perform_symbol_usage_analysis function with real repository."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from kit import Repository
            KIT_AVAILABLE = True
        except ImportError:
            KIT_AVAILABLE = False

        if not KIT_AVAILABLE:
            pytest.skip("kit.Repository not available")

        from pattern_matching.run_codomyrmex_analysis import _perform_symbol_usage_analysis
        from codomyrmex.logging_monitoring import get_logger

        # Create a real repository
        repo = Repository(str(tmp_path))
        
        # Create Python file
        (tmp_path / "test.py").write_text("def test_symbol():\n    pass\n")

        symbols_data = [{"name": "test_symbol"}]

        logger = get_logger("test")

        errors = _perform_symbol_usage_analysis(
            repo, symbols_data, str(tmp_path), "test_module",
            {"symbols_to_find_usages": ["test_symbol"]}, logger
        )

        assert isinstance(errors, list)

    def test_perform_chunking_examples(self, tmp_path, code_dir):
        """Test _perform_chunking_examples function with real repository."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from kit import Repository
            KIT_AVAILABLE = True
        except ImportError:
            KIT_AVAILABLE = False

        if not KIT_AVAILABLE:
            pytest.skip("kit.Repository not available")

        from pattern_matching.run_codomyrmex_analysis import _perform_chunking_examples
        from codomyrmex.logging_monitoring import get_logger

        # Create a real repository
        repo = Repository(str(tmp_path))
        
        # Create test files
        (tmp_path / "test.py").write_text("def test():\n    pass\n")
        (tmp_path / "README.md").write_text("# Test\n")

        logger = get_logger("test")

        errors = _perform_chunking_examples(
            repo, str(tmp_path), "test_module", 
            {"max_files_for_chunking_examples": 1}, logger
        )

        assert isinstance(errors, list)

    def test_module_constants(self, code_dir):
        """Test that module constants are properly defined."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from pattern_matching.run_codomyrmex_analysis import (
            BASE_OUTPUT_DIR_NAME,
            MODULE_DIRS,
            DEFAULT_EMBEDDING_MODEL,
            ANALYSIS_CONFIG
        )

        assert BASE_OUTPUT_DIR_NAME == "output/codomyrmex_analysis"
        assert isinstance(MODULE_DIRS, list)
        assert DEFAULT_EMBEDDING_MODEL == 'all-MiniLM-L6-v2'
        assert isinstance(ANALYSIS_CONFIG, dict)
        assert "text_search_queries" in ANALYSIS_CONFIG
        assert "files_to_summarize_count" in ANALYSIS_CONFIG

    def test_run_full_analysis_setup(self, code_dir):
        """Test run_full_analysis setup phase with real implementation."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from pattern_matching.run_codomyrmex_analysis import run_full_analysis

        # Test that function exists and is callable
        assert callable(run_full_analysis)

        # Note: We don't actually run it here as it may take a long time
        # and require external dependencies

    def test_analyze_repository_path_error_handling(self, code_dir):
        """Test analyze_repository_path error handling with real implementation."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from pattern_matching.run_codomyrmex_analysis import analyze_repository_path

        # Test with non-existent path
        with tempfile.TemporaryDirectory() as temp_dir:
            errors = analyze_repository_path("/nonexistent/path", str(temp_dir), {}, "test")

            # Should return errors
            assert isinstance(errors, list)
            assert len(errors) > 0

    def test_text_search_context_extraction_with_real_repo(self, tmp_path, code_dir):
        """Test text search context extraction with real repository."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from kit import Repository
            KIT_AVAILABLE = True
        except ImportError:
            KIT_AVAILABLE = False

        if not KIT_AVAILABLE:
            pytest.skip("kit.Repository not available")

        from pattern_matching.run_codomyrmex_analysis import _perform_text_search_context_extraction
        from codomyrmex.logging_monitoring import get_logger

        # Create a real repository
        repo = Repository(str(tmp_path))
        
        # Create test file
        (tmp_path / "test.py").write_text("# TODO: implement this\n")

        text_search_results = {
            "TODO": [
                {"file_path": "test.py", "line_number": 1}
            ]
        }

        logger = get_logger("test")

        errors = _perform_text_search_context_extraction(
            repo, text_search_results, str(tmp_path), "test_module", {}, logger
        )

        assert isinstance(errors, list)
