"""Unit tests for pattern_matching module.

Tests cover:
- Module import and structure
- PatternAnalyzer: single file analysis, directory analysis
- PatternMatch dataclass fields
- AnalysisResult dataclass fields
- Multiple patterns, no-match scenarios, empty patterns
- Stub/compatibility functions
- Edge cases: empty files, binary-like content, nested directories
- run_codomyrmex_analysis convenience function
"""

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
            from codomyrmex.coding.pattern_matching import run_codomyrmex_analysis
            assert run_codomyrmex_analysis is not None
        except ImportError as e:
            pytest.fail(f"Failed to import run_codomyrmex_analysis: {e}")

    def test_pattern_matching_module_structure(self, code_dir):
        """Test that pattern_matching package has expected exports."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        import codomyrmex.coding.pattern_matching as pm_pkg

        # Check the package exports the key names
        assert hasattr(pm_pkg, 'run_codomyrmex_analysis')
        assert hasattr(pm_pkg, 'run_full_analysis')
        assert hasattr(pm_pkg, 'analyze_repository_path')
        assert hasattr(pm_pkg, 'PatternAnalyzer')

    @pytest.mark.skip(reason="Embedding function requires configured embedding backend")
    def test_get_embedding_function(self, code_dir):
        """Test get_embedding_function returns a callable."""
        sys.path.insert(0, str(code_dir))
        try:
            from codomyrmex.pattern_matching import get_embedding_function

            func = get_embedding_function()
            assert callable(func)

            # Test calling the function (it raises NotImplementedError currently)
            with pytest.raises(NotImplementedError):
                func("test")
        finally:
            sys.path.remove(str(code_dir))

    def test_print_once_functionality(self, capsys, code_dir):
        """Test print_once function outputs a message."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import print_once

        print_once("Test message")

        captured = capsys.readouterr()
        assert "Test message" in captured.out

    def test_perform_repository_index(self, code_dir):
        """Test _perform_repository_index stub function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import (
            _perform_repository_index,
        )

        # Stub takes a single path string, should not raise
        _perform_repository_index("/some/path")

    def test_perform_text_search(self, code_dir):
        """Test _perform_text_search stub function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import (
            _perform_text_search,
        )

        results = _perform_text_search("TODO", "/some/path")
        assert isinstance(results, list)

    def test_perform_dependency_analysis(self, code_dir):
        """Test _perform_dependency_analysis stub function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import (
            _perform_dependency_analysis,
        )

        # Stub takes a single path string, should not raise
        _perform_dependency_analysis("/some/path")

    def test_perform_symbol_extraction(self, code_dir):
        """Test _perform_symbol_extraction stub function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import (
            _perform_symbol_extraction,
        )

        symbols = _perform_symbol_extraction("/some/path")
        assert isinstance(symbols, list)

    def test_perform_symbol_usage_analysis(self, code_dir):
        """Test _perform_symbol_usage_analysis stub function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import (
            _perform_symbol_usage_analysis,
        )

        usage = _perform_symbol_usage_analysis("/some/path")
        assert isinstance(usage, dict)

    def test_perform_chunking_examples(self, code_dir):
        """Test _perform_chunking_examples stub function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import (
            _perform_chunking_examples,
        )

        chunks = _perform_chunking_examples("some text to chunk")
        assert isinstance(chunks, list)
        assert len(chunks) > 0

    @pytest.mark.skip(reason="Text search context extraction requires configured search backend")
    def test_perform_text_search_context_extraction(self, code_dir):
        """Test _perform_text_search_context_extraction stub function."""
        sys.path.insert(0, str(code_dir))
        try:
            from codomyrmex.pattern_matching.api import _perform_text_search_context_extraction

            # It currently raises NotImplementedError
            with pytest.raises(NotImplementedError):
                _perform_text_search_context_extraction("dummy path", "query")
        finally:
            sys.path.remove(str(code_dir))

    def test_run_full_analysis(self, code_dir):
        """Test run_full_analysis function is callable and returns dict."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import (
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

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import (
            analyze_repository_path,
        )

        result = analyze_repository_path("/some/path")
        assert isinstance(result, dict)
        assert "status" in result

    def test_pattern_analyzer_basic(self, tmp_path, code_dir):
        """Test PatternAnalyzer with real files."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import PatternAnalyzer

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

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import (
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

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import (
            AnalysisResult,
            run_codomyrmex_analysis,
        )

        (tmp_path / "sample.py").write_text("import os\n# HACK: temp workaround\n")

        result = run_codomyrmex_analysis(str(tmp_path), {"hack": "HACK"})
        assert isinstance(result, AnalysisResult)
        assert len(result.matches) == 1

    # ==================================================================
    # New tests: PatternMatch dataclass
    # ==================================================================

    def test_pattern_match_fields(self, code_dir):
        """PatternMatch stores pattern_name, file_path, line_number, matched_text, confidence."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import PatternMatch

        pm = PatternMatch(
            pattern_name="todo",
            file_path="/some/file.py",
            line_number=42,
            matched_text="# TODO: fix",
        )
        assert pm.pattern_name == "todo"
        assert pm.file_path == "/some/file.py"
        assert pm.line_number == 42
        assert pm.matched_text == "# TODO: fix"
        assert pm.confidence == 1.0  # default

    def test_pattern_match_custom_confidence(self, code_dir):
        """PatternMatch can have a custom confidence value."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import PatternMatch

        pm = PatternMatch(
            pattern_name="test",
            file_path="/f.py",
            line_number=1,
            matched_text="text",
            confidence=0.75,
        )
        assert pm.confidence == 0.75

    # ==================================================================
    # New tests: AnalysisResult dataclass
    # ==================================================================

    def test_analysis_result_defaults(self, code_dir):
        """AnalysisResult has empty matches and errors by default."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import AnalysisResult

        ar = AnalysisResult(total_files=5, files_analyzed=5)
        assert ar.total_files == 5
        assert ar.files_analyzed == 5
        assert ar.matches == []
        assert ar.errors == []

    # ==================================================================
    # New tests: PatternAnalyzer edge cases
    # ==================================================================

    def test_pattern_analyzer_empty_patterns(self, tmp_path, code_dir):
        """Analyzer with empty patterns dict finds no matches."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import PatternAnalyzer

        test_file = tmp_path / "test.py"
        test_file.write_text("# TODO: important\n")

        analyzer = PatternAnalyzer({})
        matches = analyzer.analyze_file(str(test_file))
        assert matches == []

    def test_pattern_analyzer_no_match_in_file(self, tmp_path, code_dir):
        """Analyzer finds no matches when patterns are absent from file."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import PatternAnalyzer

        test_file = tmp_path / "clean.py"
        test_file.write_text("def clean():\n    return True\n")

        analyzer = PatternAnalyzer({"todo": "TODO", "fixme": "FIXME"})
        matches = analyzer.analyze_file(str(test_file))
        assert matches == []

    def test_pattern_analyzer_multiple_patterns_same_line(self, tmp_path, code_dir):
        """Multiple patterns matching the same line produce multiple matches."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import PatternAnalyzer

        test_file = tmp_path / "multi.py"
        test_file.write_text("# TODO FIXME: urgent\n")

        analyzer = PatternAnalyzer({"todo": "TODO", "fixme": "FIXME"})
        matches = analyzer.analyze_file(str(test_file))
        assert len(matches) == 2
        names = {m.pattern_name for m in matches}
        assert names == {"todo", "fixme"}

    def test_pattern_analyzer_multiple_matches_different_lines(self, tmp_path, code_dir):
        """Pattern found on multiple lines produces multiple matches."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import PatternAnalyzer

        test_file = tmp_path / "many_todos.py"
        test_file.write_text("# TODO: first\nprint('ok')\n# TODO: second\n")

        analyzer = PatternAnalyzer({"todo": "TODO"})
        matches = analyzer.analyze_file(str(test_file))
        assert len(matches) == 2
        assert matches[0].line_number == 1
        assert matches[1].line_number == 3

    def test_pattern_analyzer_nonexistent_file(self, code_dir):
        """Analyzer handles nonexistent file gracefully (returns empty)."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import PatternAnalyzer

        analyzer = PatternAnalyzer({"todo": "TODO"})
        matches = analyzer.analyze_file("/nonexistent/path/file.py")
        assert matches == []

    def test_pattern_analyzer_empty_file(self, tmp_path, code_dir):
        """Analyzer handles empty file (no matches, no errors)."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import PatternAnalyzer

        test_file = tmp_path / "empty.py"
        test_file.write_text("")

        analyzer = PatternAnalyzer({"todo": "TODO"})
        matches = analyzer.analyze_file(str(test_file))
        assert matches == []

    def test_pattern_analyzer_matched_text_truncation(self, tmp_path, code_dir):
        """Matched text is truncated to 100 characters."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import PatternAnalyzer

        long_line = "# TODO: " + "x" * 200 + "\n"
        test_file = tmp_path / "long.py"
        test_file.write_text(long_line)

        analyzer = PatternAnalyzer({"todo": "TODO"})
        matches = analyzer.analyze_file(str(test_file))
        assert len(matches) == 1
        assert len(matches[0].matched_text) <= 100

    def test_pattern_analyzer_directory_default_extensions(self, tmp_path, code_dir):
        """analyze_directory defaults to .py, .js, .ts extensions."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import PatternAnalyzer

        (tmp_path / "code.py").write_text("# TODO: python\n")
        (tmp_path / "code.js").write_text("// TODO: javascript\n")
        (tmp_path / "code.txt").write_text("TODO: text file\n")

        analyzer = PatternAnalyzer({"todo": "TODO"})
        result = analyzer.analyze_directory(str(tmp_path))

        # Should find matches in .py and .js, but not .txt
        matched_files = {m.file_path for m in result.matches}
        assert any(f.endswith(".py") for f in matched_files)
        assert any(f.endswith(".js") for f in matched_files)
        assert not any(f.endswith(".txt") for f in matched_files)

    def test_pattern_analyzer_directory_empty(self, tmp_path, code_dir):
        """analyze_directory on directory with no matching files."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import PatternAnalyzer

        analyzer = PatternAnalyzer({"todo": "TODO"})
        result = analyzer.analyze_directory(str(tmp_path), extensions=[".py"])
        assert result.total_files == 0
        assert result.files_analyzed == 0
        assert result.matches == []

    def test_pattern_analyzer_directory_nested(self, tmp_path, code_dir):
        """analyze_directory searches nested subdirectories."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import PatternAnalyzer

        subdir = tmp_path / "sub"
        subdir.mkdir()
        (subdir / "nested.py").write_text("# HACK: nested\n")

        analyzer = PatternAnalyzer({"hack": "HACK"})
        result = analyzer.analyze_directory(str(tmp_path), extensions=[".py"])
        assert len(result.matches) == 1
        assert result.matches[0].pattern_name == "hack"

    # ==================================================================
    # New tests: stub functions
    # ==================================================================

    @pytest.mark.skip(reason="Code summarization requires configured LLM backend")
    def test_perform_code_summarization(self, code_dir):
        """Test _perform_code_summarization raises NotImplementedError."""
        sys.path.insert(0, str(code_dir))
        try:
            from codomyrmex.pattern_matching.api import _perform_code_summarization

            with pytest.raises(NotImplementedError):
                _perform_code_summarization("dummy_code")
        finally:
            sys.path.remove(str(code_dir))

    def test_perform_docstring_indexing(self, code_dir):
        """_perform_docstring_indexing runs without error."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import (
            _perform_docstring_indexing,
        )

        # Should not raise
        _perform_docstring_indexing("/some/path")

    @pytest.mark.skip(reason="Embedding function requires configured embedding backend")
    def test_embedding_function_returns_consistent_length(self, code_dir):
        """Embedding function returns a list of consistent length for different inputs."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import (
            get_embedding_function,
        )

        embed_fn = get_embedding_function()
        result1 = embed_fn("short")
        result2 = embed_fn("a much longer piece of text to embed")
        assert len(result1) == len(result2)

    def test_run_codomyrmex_analysis_no_patterns(self, tmp_path, code_dir):
        """run_codomyrmex_analysis with no patterns returns empty matches."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import (
            run_codomyrmex_analysis,
        )

        (tmp_path / "test.py").write_text("# Nothing to match\n")
        result = run_codomyrmex_analysis(str(tmp_path))
        assert result.matches == []

    def test_analyze_repository_path_returns_path(self, code_dir):
        """analyze_repository_path includes the input path in its result."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import (
            analyze_repository_path,
        )

        result = analyze_repository_path("/custom/repo")
        assert result["path"] == "/custom/repo"

    def test_run_full_analysis_returns_path(self, code_dir):
        """run_full_analysis includes the input path in its result."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import (
            run_full_analysis,
        )

        result = run_full_analysis("/custom/path")
        assert result["path"] == "/custom/path"
        assert result["full_analysis"] is True
