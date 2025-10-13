"""
Error handling tests for the code review module.

Tests comprehensive error handling scenarios including tool failures,
invalid inputs, and edge cases.
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from codomyrmex.code_review import (
    CodeReviewer,
    PyscnAnalyzer,
    ToolNotFoundError,
    ConfigurationError,
    CodeReviewError,
    AnalysisType,
    SeverityLevel
)


class TestErrorHandling(unittest.TestCase):
    """Test comprehensive error handling."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_pyscn_not_available_error(self):
        """Test error when pyscn is not available."""
        with patch('subprocess.run', side_effect=FileNotFoundError("pyscn not found")):
            with self.assertRaises(ToolNotFoundError) as cm:
                PyscnAnalyzer()

            self.assertIn("pyscn not found", str(cm.exception))
            self.assertIn("pipx install pyscn", str(cm.exception))

    def test_pyscn_command_failure(self):
        """Test error when pyscn command fails."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "pyscn: command failed"

            analyzer = PyscnAnalyzer()

            # Should handle the error gracefully
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write('def test(): pass\n')
                test_file = f.name

            try:
                results = analyzer.analyze_complexity(test_file)
                # Should return empty list on error
                self.assertEqual(results, [])
            finally:
                os.unlink(test_file)

    def test_invalid_file_path(self):
        """Test error handling for invalid file paths."""
        reviewer = CodeReviewer()

        # Test with non-existent file
        with self.assertRaises(FileNotFoundError):
            reviewer.analyze_file("/non/existent/file.py")

    def test_invalid_project_path(self):
        """Test error handling for invalid project paths."""
        with self.assertRaises(FileNotFoundError):
            CodeReviewer(project_root="/non/existent/path")

    def test_timeout_handling(self):
        """Test timeout handling for long-running analyses."""
        with patch('subprocess.run') as mock_run:
            # Simulate a hanging process
            mock_run.side_effect = TimeoutError("Command timed out")

            analyzer = PyscnAnalyzer()

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write('def test(): pass\n')
                test_file = f.name

            try:
                results = analyzer.analyze_complexity(test_file)
                # Should handle timeout gracefully
                self.assertEqual(results, [])
            finally:
                os.unlink(test_file)

    def test_memory_error_handling(self):
        """Test handling of memory errors."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = MemoryError("Out of memory")

            analyzer = PyscnAnalyzer()

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write('def test(): pass\n')
                test_file = f.name

            try:
                results = analyzer.analyze_complexity(test_file)
                # Should handle memory error gracefully
                self.assertEqual(results, [])
            finally:
                os.unlink(test_file)

    def test_json_decode_error_handling(self):
        """Test handling of JSON decode errors from pyscn output."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = "invalid json output"

            analyzer = PyscnAnalyzer()

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write('def test(): pass\n')
                test_file = f.name

            try:
                results = analyzer.analyze_complexity(test_file)
                # Should handle JSON error gracefully
                self.assertEqual(results, [])
            finally:
                os.unlink(test_file)

    def test_permission_error_handling(self):
        """Test handling of permission errors."""
        # Create a file we can't read
        no_read_file = os.path.join(self.test_dir, "no_read.py")
        with open(no_read_file, 'w') as f:
            f.write('def test(): pass\n')

        # Remove read permission
        os.chmod(no_read_file, 0o000)

        try:
            reviewer = CodeReviewer()

            with self.assertRaises(PermissionError):
                reviewer.analyze_file(no_read_file)
        finally:
            # Restore permissions for cleanup
            os.chmod(no_read_file, 0o644)
            os.unlink(no_read_file)

    def test_invalid_configuration(self):
        """Test handling of invalid configuration."""
        invalid_config = {
            "max_complexity": "not_a_number",  # Should be int
            "output_format": 123,  # Should be string
        }

        # Should handle invalid config gracefully or raise appropriate error
        try:
            reviewer = CodeReviewer()
            reviewer.config.update(invalid_config)
            # Should not crash, but may produce warnings
        except Exception as e:
            # If it raises an error, it should be a ConfigurationError
            self.assertIsInstance(e, (ConfigurationError, ValueError, TypeError))

    def test_unsupported_analysis_type(self):
        """Test handling of unsupported analysis types."""
        reviewer = CodeReviewer()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def test(): pass\n')
            test_file = f.name

        try:
            # Should handle unsupported analysis types gracefully
            results = reviewer.analyze_file(test_file, analysis_types=["unsupported_type"])
            # Should return empty results for unsupported types
            self.assertIsInstance(results, list)
        finally:
            os.unlink(test_file)

    def test_corrupted_pyscn_output(self):
        """Test handling of corrupted pyscn output."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = "corrupted: [unclosed json"

            analyzer = PyscnAnalyzer()

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write('def test(): pass\n')
                test_file = f.name

            try:
                results = analyzer.analyze_complexity(test_file)
                # Should handle corrupted output gracefully
                self.assertEqual(results, [])
            finally:
                os.unlink(test_file)

    def test_network_error_simulation(self):
        """Test behavior when network issues occur (simulated)."""
        # Note: pyscn doesn't actually use network for local analysis
        # but this tests the error handling framework

        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = ConnectionError("Network unreachable")

            analyzer = PyscnAnalyzer()

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write('def test(): pass\n')
                test_file = f.name

            try:
                results = analyzer.analyze_complexity(test_file)
                # Should handle network errors gracefully
                self.assertEqual(results, [])
            finally:
                os.unlink(test_file)

    def test_keyboard_interrupt_handling(self):
        """Test handling of keyboard interrupts during analysis."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = KeyboardInterrupt("User interrupted")

            analyzer = PyscnAnalyzer()

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write('def test(): pass\n')
                test_file = f.name

            try:
                results = analyzer.analyze_complexity(test_file)
                # Should handle interruption gracefully
                self.assertEqual(results, [])
            finally:
                os.unlink(test_file)

    def test_system_exit_handling(self):
        """Test handling of system exit during analysis."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = SystemExit("System exit")

            analyzer = PyscnAnalyzer()

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write('def test(): pass\n')
                test_file = f.name

            try:
                results = analyzer.analyze_complexity(test_file)
                # Should handle system exit gracefully
                self.assertEqual(results, [])
            finally:
                os.unlink(test_file)

    def test_resource_exhaustion_handling(self):
        """Test handling of resource exhaustion."""
        # Create an extremely large file to test resource limits
        large_file = os.path.join(self.test_dir, "huge_file.py")

        # Write a very large file (but not too large to avoid actual memory issues)
        with open(large_file, 'w') as f:
            for i in range(10000):  # 10k lines
                f.write(f'def function_{i}():\n')
                f.write(f'    """Function {i}."""\n')
                f.write('    return "test"\n\n')

        reviewer = CodeReviewer()

        # Should handle large files without crashing
        try:
            results = reviewer.analyze_file(large_file)
            self.assertIsInstance(results, list)
        except Exception as e:
            # If it fails, should be with a reasonable error
            self.assertIsInstance(e, (MemoryError, TimeoutError, CodeReviewError))

    def test_unicode_handling_errors(self):
        """Test handling of unicode encoding errors."""
        # Create file with problematic unicode
        unicode_file = os.path.join(self.test_dir, "unicode_test.py")

        with open(unicode_file, 'wb') as f:
            # Write some bytes that might cause encoding issues
            f.write(b'def test():\n')
            f.write(b'    return "\xff\xfe invalid unicode"\n')

        reviewer = CodeReviewer()

        # Should handle encoding errors gracefully
        try:
            results = reviewer.analyze_file(unicode_file)
            self.assertIsInstance(results, list)
        except UnicodeDecodeError:
            # This is acceptable - file has encoding issues
            pass
        except Exception as e:
            # Other errors should be handled gracefully
            self.assertIsInstance(e, (UnicodeDecodeError, CodeReviewError))

    def test_circular_dependency_handling(self):
        """Test handling of circular dependencies in analysis."""
        # Create files with circular imports (Python will handle this)
        file1 = os.path.join(self.test_dir, "module1.py")
        file2 = os.path.join(self.test_dir, "module2.py")

        with open(file1, 'w') as f:
            f.write('from module2 import function2\n\ndef function1():\n    return function2()\n')

        with open(file2, 'w') as f:
            f.write('from module1 import function1\n\ndef function2():\n    return function1()\n')

        reviewer = CodeReviewer()

        # Should handle circular imports gracefully
        try:
            results = reviewer.analyze_file(file1)
            self.assertIsInstance(results, list)
        except Exception as e:
            # Import errors are acceptable
            self.assertIsInstance(e, (ImportError, CodeReviewError))

    def test_syntax_error_handling(self):
        """Test handling of Python syntax errors."""
        syntax_error_file = os.path.join(self.test_dir, "syntax_error.py")

        with open(syntax_error_file, 'w') as f:
            f.write('def invalid_function(\n    return "missing closing paren"')  # Syntax error

        reviewer = CodeReviewer()

        # Should handle syntax errors gracefully
        try:
            results = reviewer.analyze_file(syntax_error_file)
            self.assertIsInstance(results, list)
        except SyntaxError:
            # Syntax errors are acceptable for invalid files
            pass
        except Exception as e:
            # Other errors should be handled gracefully
            self.assertIsInstance(e, (SyntaxError, CodeReviewError))

    def test_empty_file_handling(self):
        """Test handling of empty files."""
        empty_file = os.path.join(self.test_dir, "empty.py")

        with open(empty_file, 'w') as f:
            f.write('')  # Empty file

        reviewer = CodeReviewer()

        # Should handle empty files gracefully
        results = reviewer.analyze_file(empty_file)
        self.assertIsInstance(results, list)

    def test_binary_file_handling(self):
        """Test handling of binary files."""
        binary_file = os.path.join(self.test_dir, "binary_file")

        with open(binary_file, 'wb') as f:
            f.write(b'\x00\x01\x02\x03binary content\xff\xfe')  # Binary content

        reviewer = CodeReviewer()

        # Should handle binary files gracefully
        try:
            results = reviewer.analyze_file(binary_file)
            self.assertIsInstance(results, list)
        except Exception as e:
            # Binary files may cause various errors, all should be handled
            self.assertIsInstance(e, (UnicodeDecodeError, CodeReviewError))

    def test_concurrent_access_handling(self):
        """Test handling of concurrent access to the same files."""
        shared_file = os.path.join(self.test_dir, "shared.py")

        with open(shared_file, 'w') as f:
            f.write('def test(): return "shared"\n')

        reviewer1 = CodeReviewer()
        reviewer2 = CodeReviewer()

        # Both should be able to analyze the same file
        results1 = reviewer1.analyze_file(shared_file)
        results2 = reviewer2.analyze_file(shared_file)

        self.assertIsInstance(results1, list)
        self.assertIsInstance(results2, list)

    def test_graceful_degradation(self):
        """Test graceful degradation when tools fail."""
        with patch.object(CodeReviewer, '_run_pylint', side_effect=Exception("Pylint failed")):
            with patch.object(CodeReviewer, '_run_flake8', side_effect=Exception("Flake8 failed")):
                with patch.object(CodeReviewer, '_run_mypy', side_effect=Exception("MyPy failed")):

                    reviewer = CodeReviewer()

                    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                        f.write('def test(): pass\n')
                        test_file = f.name

                    try:
                        # Should still work even if all traditional tools fail
                        results = reviewer.analyze_file(test_file)
                        self.assertIsInstance(results, list)
                    finally:
                        os.unlink(test_file)

    def test_error_logging(self):
        """Test that errors are properly logged."""
        with patch('codomyrmex.code_review.logger') as mock_logger:
            with patch('subprocess.run', side_effect=Exception("Test error")):

                analyzer = PyscnAnalyzer()

                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write('def test(): pass\n')
                    test_file = f.name

                try:
                    analyzer.analyze_complexity(test_file)
                finally:
                    os.unlink(test_file)

                # Should have logged the error
                mock_logger.error.assert_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)

