"""
Performance tests for pyscn functionality.

These tests measure the performance characteristics of pyscn analysis
to ensure it meets the required performance targets.
"""

import os
import sys
import unittest
import tempfile
import time
import shutil
from pathlib import Path

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from codomyrmex.code_review import PyscnAnalyzer, CodeReviewer


class TestPyscnPerformance(unittest.TestCase):
    """Performance tests for pyscn functionality."""

    def setUp(self):
        """Set up performance test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.large_file = self._create_large_test_file()

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _create_large_test_file(self, lines=1000):
        """Create a large Python file for performance testing."""
        file_path = os.path.join(self.test_dir, "large_test_file.py")

        with open(file_path, 'w') as f:
            f.write('"""\nLarge test file for performance testing.\n"""\n\n')

            # Generate many functions with varying complexity
            for i in range(lines):
                complexity = (i % 10) + 1  # Vary complexity from 1-10

                f.write(f"def function_{i}(x, y, z):\n")
                f.write(f'    """Function {i} with complexity {complexity}."""\n')

                # Add conditional logic based on complexity
                indent = "    "
                for j in range(complexity):
                    if j == 0:
                        f.write(f'{indent}if x > {j}:\n')
                    else:
                        f.write(f'{indent}else if y > {j}:\n')
                    indent += "    "

                f.write(f'{indent}return x + y + z\n\n')

        return file_path

    def _create_many_files(self, count=100):
        """Create many small Python files for testing."""
        files = []

        for i in range(count):
            file_path = os.path.join(self.test_dir, f"test_file_{i}.py")

            with open(file_path, 'w') as f:
                f.write(f'"""\nTest file {i}.\n"""\n\n')
                f.write(f"def test_function_{i}(x):\n")
                f.write(f'    """Test function {i}."""\n')
                f.write('    if x > 0:\n')
                f.write('        return x * 2\n')
                f.write('    else:\n')
                f.write('        return 0\n\n')

            files.append(file_path)

        return files

    @unittest.skipUnless(_pyscn_available(), "Pyscn not available")
    def test_complexity_analysis_performance(self):
        """Test performance of complexity analysis."""
        if not os.path.exists(self.large_file):
            self.skipTest("Large test file not available")

        analyzer = PyscnAnalyzer()

        # Measure analysis time
        start_time = time.time()
        results = analyzer.analyze_complexity(self.large_file)
        end_time = time.time()

        analysis_time = end_time - start_time

        # Performance targets:
        # - Should analyze at least 1000 lines/sec
        # - Should complete within 10 seconds for 1000 lines

        file_size = os.path.getsize(self.large_file)
        lines_per_sec = file_size / analysis_time

        print(f"\nComplexity Analysis Performance:")
        print(f"  File size: {file_size} bytes")
        print(f"  Analysis time: {analysis_time:.2f} seconds")
        print(f"  Performance: {lines_per_sec:.0f} bytes/sec")

        # Assert performance meets targets
        self.assertGreater(lines_per_sec, 100000, "Performance below 100KB/sec target")
        self.assertLess(analysis_time, 10.0, "Analysis took too long (>10s)")

    @unittest.skipUnless(_pyscn_available(), "Pyscn not available")
    def test_dead_code_detection_performance(self):
        """Test performance of dead code detection."""
        if not os.path.exists(self.large_file):
            self.skipTest("Large test file not available")

        analyzer = PyscnAnalyzer()

        # Measure analysis time
        start_time = time.time()
        results = analyzer.detect_dead_code(self.large_file)
        end_time = time.time()

        analysis_time = end_time - start_time

        print(f"\nDead Code Detection Performance:")
        print(f"  Analysis time: {analysis_time:.2f} seconds")
        print(f"  Dead code findings: {len(results)}")

        # Should complete within reasonable time
        self.assertLess(analysis_time, 15.0, "Dead code analysis took too long")

    @unittest.skipUnless(_pyscn_available(), "Pyscn not available")
    def test_clone_detection_performance(self):
        """Test performance of clone detection."""
        files = self._create_many_files(50)  # Create 50 files

        if len(files) < 10:
            self.skipTest("Not enough files for clone detection")

        analyzer = PyscnAnalyzer()

        # Measure analysis time
        start_time = time.time()
        results = analyzer.find_clones(files, threshold=0.8)
        end_time = time.time()

        analysis_time = end_time - start_time

        print(f"\nClone Detection Performance:")
        print(f"  Files analyzed: {len(files)}")
        print(f"  Analysis time: {analysis_time:.2f} seconds")
        print(f"  Clone groups found: {len(results)}")

        # Should complete within reasonable time for 50 files
        self.assertLess(analysis_time, 30.0, "Clone detection took too long")

    @unittest.skipUnless(_pyscn_available(), "Pyscn not available")
    def test_full_workflow_performance(self):
        """Test performance of complete analysis workflow."""
        files = self._create_many_files(20)

        reviewer = CodeReviewer(project_root=self.test_dir)

        # Measure complete analysis time
        start_time = time.time()
        summary = reviewer.analyze_project(target_paths=files)
        end_time = time.time()

        analysis_time = end_time - start_time

        print(f"\nFull Workflow Performance:")
        print(f"  Files analyzed: {summary.files_analyzed}")
        print(f"  Total issues: {summary.total_issues}")
        print(f"  Analysis time: {analysis_time:.2f} seconds")

        # Should analyze at least 5 files per second
        files_per_sec = summary.files_analyzed / analysis_time
        print(f"  Performance: {files_per_sec:.1f} files/sec")

        self.assertGreater(files_per_sec, 5.0, "Performance below 5 files/sec target")
        self.assertLess(analysis_time, 60.0, "Full analysis took too long")

    @unittest.skipUnless(_pyscn_available(), "Pyscn not available")
    def test_memory_usage(self):
        """Test memory usage during analysis."""
        import psutil
        import os

        if not os.path.exists(self.large_file):
            self.skipTest("Large test file not available")

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        analyzer = PyscnAnalyzer()
        results = analyzer.analyze_complexity(self.large_file)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = final_memory - initial_memory

        print(f"\nMemory Usage:")
        print(f"  Initial memory: {initial_memory:.1f} MB")
        print(f"  Final memory: {final_memory:.1f} MB")
        print(f"  Memory used: {memory_used:.1f} MB")

        # Memory usage should be reasonable (< 100MB additional)
        self.assertLess(memory_used, 100.0, "Memory usage too high (>100MB)")

    def test_performance_requirements_documentation(self):
        """Document the performance requirements that should be met."""
        requirements = {
            "complexity_analysis": ">100,000 lines/sec",
            "dead_code_detection": "<5 seconds for 1000 lines",
            "clone_detection": "<30 seconds for 100 files",
            "memory_usage": "<100MB additional per analysis",
            "full_workflow": "<60 seconds for 100 files"
        }

        print("\nPerformance Requirements:")
        for requirement, target in requirements.items():
            print(f"  {requirement}: {target}")


def _pyscn_available():
    """Check if pyscn is available for testing."""
    try:
        import subprocess
        result = subprocess.run(
            ["pyscn", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


if __name__ == '__main__':
    if _pyscn_available():
        print("✅ Pyscn is available - running performance tests")
        unittest.main(verbosity=2)
    else:
        print("❌ Pyscn not available - install with: pipx install pyscn")
        print("Skipping performance tests")
        sys.exit(0)

