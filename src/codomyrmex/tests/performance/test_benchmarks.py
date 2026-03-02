
import importlib

import pytest

from codomyrmex.coding.parsers.tree_sitter import TreeSitterParser
from codomyrmex.coding.parsers.tree_sitter.languages.languages import LanguageManager


@pytest.mark.benchmark
def test_module_import_time(benchmark):
    """Benchmark import time of the main codomyrmex package."""
    def import_codomyrmex():
        import codomyrmex
        importlib.reload(codomyrmex)

    benchmark(import_codomyrmex)

@pytest.mark.benchmark
def test_ast_parsing_speed(benchmark):
    """Benchmark AST parsing speed using TreeSitterParser."""
    # Try to get python language
    # Assuming LanguageManager has discovered languages or we can try to find them
    # If not found, we skip
    python_lang = LanguageManager.get_language("python")

    if not python_lang:
        # Try to discover in standard locations?
        # For now, just skip if not loaded
        pytest.skip("Tree-sitter python language not available")

    parser = TreeSitterParser(python_lang)
    # A decently sized python snippet
    code = """
    class Example:
        def __init__(self):
            self.value = 0

        def compute(self, x):
            if x > 0:
                return x * x
            else:
                return 0

        def loop(self):
            for i in range(100):
                self.compute(i)
    """ * 10

    def parse_code():
        parser.parse(code)

    benchmark(parse_code)
