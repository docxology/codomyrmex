#!/usr/bin/env python3
"""
Unit tests for the Build Synthesis module.
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.build_synthesis.build_orchestrator import (
    check_build_environment,
    synthesize_build_artifact,
    validate_build_output,
    orchestrate_build_pipeline
)


class TestBuildSynthesis(unittest.TestCase):
    """Test cases for build synthesis functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_check_build_environment(self):
        """Test build environment checking."""
        result = check_build_environment()
        # This should work regardless of what's installed
        self.assertIsInstance(result, bool)

    def test_synthesize_python_executable(self):
        """Test synthesis of Python executable."""
        source_file = os.path.join(self.test_dir, "test_script.py")
        output_file = os.path.join(self.test_dir, "test_executable.py")

        # Create a simple Python script
        with open(source_file, 'w') as f:
            f.write("""
def main():
    print("Hello from test script!")

if __name__ == "__main__":
    main()
""")

        result = synthesize_build_artifact(
            source_path=source_file,
            output_path=output_file,
            artifact_type="executable"
        )

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))

        # Check that the output contains expected content
        with open(output_file, 'r') as f:
            content = f.read()
            self.assertIn("import", content)
            self.assertIn("main()", content)

    def test_validate_build_output(self):
        """Test build output validation."""
        # Create a test file with proper Python code
        test_file = os.path.join(self.test_dir, "test_output.py")
        with open(test_file, 'w') as f:
            f.write("# Test Python file\nimport sys\ndef main():\n    print('Hello')\n\nif __name__ == '__main__':\n    main()\n")

        validation = validate_build_output(test_file)

        self.assertTrue(validation["exists"])
        self.assertTrue(validation["is_file"])
        self.assertTrue(validation["size_bytes"] > 0)
        self.assertEqual(len(validation["errors"]), 0)

    def test_orchestrate_build_pipeline(self):
        """Test build pipeline orchestration."""
        build_config = {
            "dependencies": [],
            "build_commands": [
                ["python", "-c", "print('Test build command')"]
            ],
            "artifacts": []
        }

        results = orchestrate_build_pipeline(build_config)

        self.assertIsInstance(results, dict)
        self.assertIn("overall_success", results)
        self.assertIn("stages", results)
        self.assertIn("artifacts", results)
        self.assertIn("errors", results)

    def test_synthesize_nonexistent_source(self):
        """Test synthesis with nonexistent source file."""
        result = synthesize_build_artifact(
            source_path="/nonexistent/file.py",
            output_path=os.path.join(self.test_dir, "output.py"),
            artifact_type="executable"
        )

        self.assertFalse(result)

    def test_validate_nonexistent_output(self):
        """Test validation of nonexistent output file."""
        validation = validate_build_output("/nonexistent/file.py")

        self.assertFalse(validation["exists"])
        self.assertIn("does not exist", validation["errors"][0])


if __name__ == '__main__':
    unittest.main()