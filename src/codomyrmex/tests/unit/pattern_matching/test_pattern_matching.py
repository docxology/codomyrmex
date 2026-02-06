"""Unit tests for pattern_matching module."""

import sys

import pytest


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

    def test_get_embedding_function(self, code_dir):
        """Test get_embedding_function returns a callable."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.pattern_matching.run_codomyrmex_analysis import (
            get_embedding_function,
        )

        embed_fn = get_embedding_function()
        # The stub returns a lambda that produces a list of floats
        assert callable(embed_fn)
        result = embed_fn("test text")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_print_once_functionality(self, capsys, code_dir):
        """Test print_once function outputs a message."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.pattern_matching.run_codomyrmex_analysis import print_once

        print_once("Test message")

        captured = capsys.readouterr()
        assert "Test message" in captured.out

    def test_perform_repository_index(self, code_dir):
        """Test _perform_repository_index stub function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.pattern_matching.run_codomyrmex_analysis import (
            _perform_repository_index,
        )

        # Stub takes a single path string, should not raise
        _perform_repository_index("/some/path")

    def test_perform_text_search(self, code_dir):
        """Test _perform_text_search stub function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.pattern_matching.run_codomyrmex_analysis import (
            _perform_text_search,
        )

        results = _perform_text_search("TODO", "/some/path")
        assert isinstance(results, list)

    def test_perform_dependency_analysis(self, code_dir):
        """Test _perform_dependency_analysis stub function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.pattern_matching.run_codomyrmex_analysis import (
            _perform_dependency_analysis,
        )

        # Stub takes a single path string, should not raise
        _perform_dependency_analysis("/some/path")

    def test_perform_symbol_extraction(self, code_dir):
        """Test _perform_symbol_extraction stub function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.pattern_matching.run_codomyrmex_analysis import (
            _perform_symbol_extraction,
        )

        symbols = _perform_symbol_extraction("/some/path")
        assert isinstance(symbols, list)

    def test_perform_symbol_usage_analysis(self, code_dir):
        """Test _perform_symbol_usage_analysis stub function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.pattern_matching.run_codomyrmex_analysis import (
            _perform_symbol_usage_analysis,
        )

        usage = _perform_symbol_usage_analysis("/some/path")
        assert isinstance(usage, dict)

    def test_perform_chunking_examples(self, code_dir):
        """Test _perform_chunking_examples stub function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.pattern_matching.run_codomyrmex_analysis import (
            _perform_chunking_examples,
        )

        chunks = _perform_chunking_examples("some text to chunk")
        assert isinstance(chunks, list)
        assert len(chunks) > 0

    def test_perform_text_search_context_extraction(self, code_dir):
        """Test _perform_text_search_context_extraction stub function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.pattern_matching.run_codomyrmex_analysis import (
            _perform_text_search_context_extraction,
        )

        context = _perform_text_search_context_extraction("TODO", "/some/path")
        assert isinstance(context, str)

    def test_run_full_analysis(self, code_dir):
        """Test run_full_analysis function is callable and returns dict."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.pattern_matching.run_codomyrmex_analysis import (
            run_full_analysis,
        )

        assert callable(run_full_analysis)
        result = run_full_analysis("/some/path")
        assert isinstance(result, dict)
        assert "full_analysis" in result

    def test_analyze_repository_path(self, code_dir):
        """Test analyze_repository_path function returns dict."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.pattern_matching.run_codomyrmex_analysis import (
            analyze_repository_path,
        )

        result = analyze_repository_path("/some/path")
        assert isinstance(result, dict)
        assert "status" in result

    def test_pattern_analyzer_basic(self, tmp_path, code_dir):
        """Test PatternAnalyzer with real files."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.pattern_matching.run_codomyrmex_analysis import PatternAnalyzer

        # Create test file with a known pattern
        test_file = tmp_path / "test.py"
        test_file.write_text("# TODO: fix this\ndef hello():\n    pass\n")

        analyzer = PatternAnalyzer({"todo": "TODO"})
        matches = analyzer.analyze_file(str(test_file))

        assert len(matches) == 1
        assert matches[0].pattern_name == "todo"
        assert matches[0].line_number == 1

    def test_pattern_analyzer_directory(self, tmp_path, code_dir):
        """Test PatternAnalyzer.analyze_directory with real files."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.pattern_matching.run_codomyrmex_analysis import (
            AnalysisResult,
            PatternAnalyzer,
        )

        # Create test files
        (tmp_path / "a.py").write_text("# FIXME: broken\n")
        (tmp_path / "b.py").write_text("def ok():\n    pass\n")

        analyzer = PatternAnalyzer({"fixme": "FIXME"})
        result = analyzer.analyze_directory(str(tmp_path), extensions=[".py"])

        assert isinstance(result, AnalysisResult)
        assert result.total_files == 2
        assert result.files_analyzed == 2
        assert len(result.matches) == 1
        assert result.matches[0].pattern_name == "fixme"

    def test_run_codomyrmex_analysis_function(self, tmp_path, code_dir):
        """Test the convenience run_codomyrmex_analysis function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.pattern_matching.run_codomyrmex_analysis import (
            AnalysisResult,
            run_codomyrmex_analysis,
        )

        (tmp_path / "sample.py").write_text("import os\n# HACK: temp workaround\n")

        result = run_codomyrmex_analysis(str(tmp_path), {"hack": "HACK"})
        assert isinstance(result, AnalysisResult)
        assert len(result.matches) == 1
