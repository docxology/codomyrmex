"""Unit tests for pattern_matching module."""

import pytest
import sys
import os
import tempfile
import json
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path


class TestPatternMatching:
    """Test cases for pattern matching functionality."""

    def test_pattern_matching_import(self, code_dir):
        """Test that we can import pattern_matching module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from pattern_matching import run_codomyrmex_analysis
            assert run_codomyrmex_analysis is not None
        except ImportError as e:
            pytest.fail(f"Failed to import run_codomyrmex_analysis: {e}")

    def test_pattern_matching_module_structure(self, code_dir):
        """Test that pattern_matching has expected structure."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from pattern_matching import run_codomyrmex_analysis

        assert hasattr(run_codomyrmex_analysis, '__file__')
        assert hasattr(run_codomyrmex_analysis, 'run_full_analysis')
        assert hasattr(run_codomyrmex_analysis, 'analyze_repository_path')

    def test_get_embedding_function_with_sentence_transformer(self, code_dir):
        """Test get_embedding_function when SentenceTransformer is available."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from pattern_matching.run_codomyrmex_analysis import get_embedding_function

        with patch('pattern_matching.run_codomyrmex_analysis.SentenceTransformer') as mock_st:
            mock_model = MagicMock()
            # Mock encode to return a numpy-like array that has .tolist()
            mock_result = MagicMock()
            mock_result.tolist.return_value = [0.1, 0.2, 0.3]
            mock_model.encode.return_value = mock_result
            mock_st.return_value = mock_model

            embed_fn = get_embedding_function('test-model')

            assert embed_fn is not None
            result = embed_fn("test text")
            assert result == [0.1, 0.2, 0.3]
            mock_st.assert_called_once_with('test-model')

    def test_get_embedding_function_without_sentence_transformer(self, code_dir):
        """Test get_embedding_function when SentenceTransformer is not available."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        with patch('pattern_matching.run_codomyrmex_analysis.SentenceTransformer', None):
            # Reset the global _embed_fn_instance to ensure clean state
            import pattern_matching.run_codomyrmex_analysis as pm_module
            pm_module._embed_fn_instance = None

            from pattern_matching.run_codomyrmex_analysis import get_embedding_function

            result = get_embedding_function('test-model')
            assert result is None

    @patch('pattern_matching.run_codomyrmex_analysis.logger')
    def test_print_once_functionality(self, mock_logger, code_dir):
        """Test print_once function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from pattern_matching.run_codomyrmex_analysis import print_once, PRINTED_ONCE_KEYS

        # Clear the set for testing
        PRINTED_ONCE_KEYS.clear()

        mock_logger.info = MagicMock()

        # First call should print
        print_once("test_key", "Test message", _logger=mock_logger)
        mock_logger.info.assert_called_once_with("(test_key) Test message")

        # Second call should not print
        mock_logger.info.reset_mock()
        print_once("test_key", "Test message", _logger=mock_logger)
        mock_logger.info.assert_not_called()

    @patch('kit.Repository')
    @patch('pattern_matching.run_codomyrmex_analysis.logger')
    def test_perform_repository_index(self, mock_logger, mock_repo_class, code_dir):
        """Test _perform_repository_index function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from pattern_matching.run_codomyrmex_analysis import _perform_repository_index

        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        with tempfile.TemporaryDirectory() as temp_dir:
            errors = _perform_repository_index(mock_repo, temp_dir, "test_module", {}, mock_logger)

            assert len(errors) == 0
            mock_repo.write_index.assert_called_once()

    @patch('kit.Repository')
    @patch('pattern_matching.run_codomyrmex_analysis.logger')
    def test_perform_text_search(self, mock_logger, mock_repo_class, code_dir):
        """Test _perform_text_search function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from pattern_matching.run_codomyrmex_analysis import _perform_text_search

        mock_repo = MagicMock()
        mock_repo.search_text.return_value = [{"file_path": "test.py", "line_number": 1}]
        mock_repo_class.return_value = mock_repo

        with tempfile.TemporaryDirectory() as temp_dir:
            results, errors = _perform_text_search(mock_repo, temp_dir, "test_module", {"text_search_queries": ["TODO"]}, mock_logger)

            assert len(errors) == 0
            assert "TODO" in results
            mock_repo.search_text.assert_called()

    @patch('kit.Repository')
    @patch('pattern_matching.run_codomyrmex_analysis.logger')
    def test_perform_dependency_analysis_python_files(self, mock_logger, mock_repo_class, code_dir):
        """Test _perform_dependency_analysis with Python files."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from pattern_matching.run_codomyrmex_analysis import _perform_dependency_analysis

        mock_repo = MagicMock()
        mock_repo.get_file_tree.return_value = [
            {"path": "test.py", "is_dir": False},
            {"path": "README.md", "is_dir": False}
        ]
        mock_analyzer = MagicMock()
        mock_analyzer.generate_dependency_report.return_value = {"dependencies": [], "cycles": []}
        mock_repo.get_dependency_analyzer.return_value = mock_analyzer
        mock_repo_class.return_value = mock_repo

        with tempfile.TemporaryDirectory() as temp_dir:
            errors = _perform_dependency_analysis(mock_repo, temp_dir, "test_module", {}, mock_logger)

            assert len(errors) == 0
            mock_repo.get_dependency_analyzer.assert_called_once_with('python')
            mock_analyzer.export_dependency_graph.assert_called()

    @patch('kit.Repository')
    @patch('pattern_matching.run_codomyrmex_analysis.logger')
    def test_perform_dependency_analysis_no_python_files(self, mock_logger, mock_repo_class, code_dir):
        """Test _perform_dependency_analysis with no Python files."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from pattern_matching.run_codomyrmex_analysis import _perform_dependency_analysis

        mock_repo = MagicMock()
        mock_repo.get_file_tree.return_value = [
            {"path": "README.md", "is_dir": False},
            {"path": "docs.txt", "is_dir": False}
        ]
        mock_repo_class.return_value = mock_repo

        with tempfile.TemporaryDirectory() as temp_dir:
            errors = _perform_dependency_analysis(mock_repo, temp_dir, "test_module", {}, mock_logger)

            assert len(errors) == 0
            mock_logger.info.assert_called_with("Skipped: Python dependency analysis for test_module (no .py files found)")

    @patch('kit.Repository')
    @patch('pattern_matching.run_codomyrmex_analysis.logger')
    def test_perform_symbol_extraction(self, mock_logger, mock_repo_class, code_dir):
        """Test _perform_symbol_extraction function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from pattern_matching.run_codomyrmex_analysis import _perform_symbol_extraction

        mock_repo = MagicMock()
        mock_repo.extract_symbols.return_value = [{"name": "test_function", "type": "function"}]
        mock_repo_class.return_value = mock_repo

        with tempfile.TemporaryDirectory() as temp_dir:
            symbols, errors = _perform_symbol_extraction(mock_repo, temp_dir, "test_module", {}, mock_logger)

            assert len(errors) == 0
            assert len(symbols) == 1
            assert symbols[0]["name"] == "test_function"
            mock_repo.extract_symbols.assert_called_once()

    @patch('kit.Repository')
    @patch('pattern_matching.run_codomyrmex_analysis.logger')
    def test_perform_symbol_usage_analysis(self, mock_logger, mock_repo_class, code_dir):
        """Test _perform_symbol_usage_analysis function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from pattern_matching.run_codomyrmex_analysis import _perform_symbol_usage_analysis

        mock_repo = MagicMock()
        mock_repo.find_symbol_usages.return_value = [{"file_path": "test.py", "line_number": 5}]
        mock_repo_class.return_value = mock_repo

        symbols_data = [{"name": "test_symbol"}]

        with tempfile.TemporaryDirectory() as temp_dir:
            errors = _perform_symbol_usage_analysis(mock_repo, symbols_data, temp_dir, "test_module",
                                                  {"symbols_to_find_usages": ["test_symbol"]}, mock_logger)

            assert len(errors) == 0
            mock_repo.find_symbol_usages.assert_called_once_with("test_symbol")

    @patch('kit.Repository')
    @patch('pattern_matching.run_codomyrmex_analysis.logger')
    def test_perform_chunking_examples(self, mock_logger, mock_repo_class, code_dir):
        """Test _perform_chunking_examples function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from pattern_matching.run_codomyrmex_analysis import _perform_chunking_examples

        mock_repo = MagicMock()
        mock_repo.get_file_tree.return_value = [
            {"path": "test.py", "is_dir": False},
            {"path": "README.md", "is_dir": False}
        ]
        mock_repo.chunk_file_by_lines.return_value = ["line 1", "line 2"]
        mock_repo.chunk_file_by_symbols.return_value = ["symbol chunk"]
        mock_repo_class.return_value = mock_repo

        with tempfile.TemporaryDirectory() as temp_dir:
            errors = _perform_chunking_examples(mock_repo, temp_dir, "test_module", {"max_files_for_chunking_examples": 1}, mock_logger)

            assert len(errors) == 0
            mock_repo.chunk_file_by_lines.assert_called()

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

    @patch('pattern_matching.run_codomyrmex_analysis.setup_logging')
    @patch('pattern_matching.run_codomyrmex_analysis.get_logger')
    @patch('pattern_matching.run_codomyrmex_analysis.ensure_core_deps_installed')
    @patch('os.path.exists')
    @patch('shutil.rmtree')
    @patch('os.makedirs')
    def test_run_full_analysis_setup(self, mock_makedirs, mock_rmtree, mock_exists,
                                   mock_ensure_deps, mock_get_logger, mock_setup_logging, code_dir):
        """Test run_full_analysis setup phase."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from pattern_matching.run_codomyrmex_analysis import run_full_analysis

        mock_exists.return_value = True
        mock_get_logger.return_value = MagicMock()

        # This test focuses on the setup phase without actually running analysis
        # We'll patch tqdm to avoid the actual module analysis loop
        with patch('tqdm.tqdm') as mock_tqdm:
            mock_tqdm.return_value = []  # Empty list to skip module analysis

            try:
                run_full_analysis()
            except Exception:
                # We expect this to fail or be interrupted since we're mocking heavily
                # The important thing is that the setup phase works
                pass

        mock_setup_logging.assert_called_once()
        mock_ensure_deps.assert_called_once()

    def test_analyze_repository_path_error_handling(self, code_dir):
        """Test analyze_repository_path error handling."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from pattern_matching.run_codomyrmex_analysis import analyze_repository_path

        with patch('kit.Repository', side_effect=Exception("Repository initialization failed")):
            with patch('pattern_matching.run_codomyrmex_analysis.logger') as mock_logger:
                mock_logger_instance = MagicMock()
                mock_logger_instance.error = MagicMock()

                with patch('pattern_matching.run_codomyrmex_analysis.logger', mock_logger_instance):
                    with tempfile.TemporaryDirectory() as temp_dir:
                        errors = analyze_repository_path("/nonexistent/path", "test_output", {}, "test")

                        assert len(errors) > 0
                        assert "Could not initialize Repository" in errors[0]

    def test_text_search_context_extraction_with_mock_repo(self, code_dir):
        """Test text search context extraction with mocked repository."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from pattern_matching.run_codomyrmex_analysis import _perform_text_search_context_extraction

        mock_repo = MagicMock()
        text_search_results = {
            "TODO": [
                {"file_path": "test.py", "line_number": 10}
            ]
        }

        with patch('pattern_matching.run_codomyrmex_analysis.logger') as mock_logger:
            with tempfile.TemporaryDirectory() as temp_dir:
                errors = _perform_text_search_context_extraction(
                    mock_repo, text_search_results, temp_dir, "test_module", {}, mock_logger
                )

                assert len(errors) == 0
