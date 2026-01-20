"""Unit tests for the refined utilities."""

import unittest
from codomyrmex.utils import RefinedUtilities

class TestUtils(unittest.TestCase):
    def test_deep_merge(self):
        dict1 = {"a": {"b": 1}}
        dict2 = {"a": {"c": 2}, "d": 3}
        expected = {"a": {"b": 1, "c": 2}, "d": 3}
        result = RefinedUtilities.deep_merge(dict1, dict2)
        self.assertEqual(result, expected)

    def test_retry(self):
        self.count = 0
        @RefinedUtilities.retry(retries=3, backoff_factor=0.1)
        def failing_func():
            self.count += 1
            if self.count < 2:
                raise ValueError("Fail")
            return "success"
        
        result = failing_func()
        self.assertEqual(result, "success")
        self.assertEqual(self.count, 2)
