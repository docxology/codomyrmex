import pytest
import unittest
from unittest.mock import MagicMock, patch
from codomyrmex.coding.debugging import (
    ErrorAnalyzer,
    ErrorDiagnosis,
    PatchGenerator,
    FixVerifier,
    Patch,
    Debugger
)

@pytest.mark.unit
class TestErrorAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = ErrorAnalyzer()
        
    def test_parse_python_syntax_error(self):
        stderr = 'File "test.py", line 1\n    if True\n          ^\nSyntaxError: invalid syntax'
        diagnosis = self.analyzer.analyze("", stderr, 1)
        self.assertIsNotNone(diagnosis)
        self.assertEqual(diagnosis.error_type, "SyntaxError")
        self.assertEqual(diagnosis.line_number, 1)
        self.assertEqual(diagnosis.file_path, "test.py")

    def test_parse_python_runtime_error(self):
        stderr = 'Traceback (most recent call last):\n  File "main.py", line 10, in <module>\n    print(1/0)\nZeroDivisionError: division by zero'
        diagnosis = self.analyzer.analyze("", stderr, 1)
        self.assertIsNotNone(diagnosis)
        self.assertEqual(diagnosis.error_type, "ZeroDivisionError")
        self.assertEqual(diagnosis.line_number, 10)
        self.assertEqual(diagnosis.message, "division by zero")

    def test_timeout_error(self):
        diagnosis = self.analyzer.analyze("", "Terminated", 124)
        self.assertIsNotNone(diagnosis)
        self.assertEqual(diagnosis.error_type, "TimeoutError")
        self.assertTrue(diagnosis.is_timeout)

@pytest.mark.unit
class TestPatchGenerator(unittest.TestCase):
    def setUp(self):
        self.mock_llm = MagicMock()
        self.generator = PatchGenerator(llm_client=self.mock_llm)
        
    def test_generate_no_file_path(self):
        diagnosis = ErrorDiagnosis("Error", "msg")
        patches = self.generator.generate("code", diagnosis)
        self.assertEqual(patches, [])
        
    def test_generate_llm_call(self):
        # We just test that the prompt construction doesn't crash
        # Since we mocked the LLM response to be empty/nothing in our placeholder impl
        diagnosis = ErrorDiagnosis("Error", "msg", "file.py", 10, "trace")
        patches = self.generator.generate("code", diagnosis)
        # In current stub implementation, it returns empty list if llm returns nothing
        self.assertIsInstance(patches, list)

@pytest.mark.unit
class TestDebugger(unittest.TestCase):
    def setUp(self):
        self.debugger = Debugger()
        self.debugger.analyzer = MagicMock()
        self.debugger.patcher = MagicMock()
        self.debugger.verifier = MagicMock()
        
    def test_debug_flow_success(self):
        # Setup mocks
        diagnosis = ErrorDiagnosis("ValError", "fail", "f.py", 1)
        self.debugger.analyzer.analyze.return_value = diagnosis
        
        mypatch = Patch("f.py", "diff", "fix it", 0.9)
        self.debugger.patcher.generate.return_value = [mypatch]
        
        # Verify success
        verification = MagicMock()
        verification.success = True
        self.debugger.verifier.verify.return_value = verification
        
        # Run
        result = self.debugger.debug("source", "out", "err", 1)
        
        # Assertions
        self.debugger.analyzer.analyze.assert_called_once()
        self.debugger.patcher.generate.assert_called_once()
        self.debugger.verifier.verify.assert_called_once()
        self.assertIsNotNone(result) # Should return patched source

if __name__ == "__main__":
    unittest.main()
