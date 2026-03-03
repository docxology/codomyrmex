1. *Create `language_detection` module directories and files*
   - Create directories `src/codomyrmex/language_detection` and `src/codomyrmex/tests/unit/language_detection`.
   - Use `uv add langdetect` to install dependencies and update `pyproject.toml` or `uv.lock`.
   - Create `src/codomyrmex/language_detection/__init__.py` with docstrings and code that detects language and language probabilities.
   - Create `src/codomyrmex/language_detection/mcp_tools.py` ensuring `@mcp_tool` decorators are present and the tools are properly integrated.
   - Create `src/codomyrmex/language_detection/README.md`, `AGENTS.md`, and `SPEC.md`.
2. *Create strictly zero-mock tests*
   - Create `src/codomyrmex/tests/unit/language_detection/test_mcp_tools.py` with zero-mock tests mapping directly to the underlying langdetect tools.
3. *Update `codomyrmex` documentation*
   - Update `src/codomyrmex/README.md` to list the new `language_detection/` module.
4. *Run tests and verify formatting*
   - Run `uv run pytest src/codomyrmex/tests/unit/language_detection/test_mcp_tools.py -o "addopts="` to make sure tests pass.
   - Verify `src/codomyrmex/README.md` is updated using `cat`.
5. *Complete pre-commit steps*
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
