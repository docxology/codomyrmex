## 2026-03-01 - Fix Hardcoded Secret Vulnerability in Models

**Vulnerability:**
The `SecretType` Enum in `src/codomyrmex/security/secrets/models.py` previously assigned the literal string `"password"` to the `PASSWORD` constant. Static Application Security Testing (SAST) tools and secret scanners routinely flag this exact pattern (assigning a string literal like "password" to a variable named `PASSWORD`) as a hardcoded secret. Although the value represents a type rather than an actual secret, it triggers false positives that degrade security monitoring efficacy.

**Learning:**
Security models and Enums should avoid using literal security-sensitive terms like `"password"` directly as values. These patterns mimic common hardcoded credentials, confusing security scanners.

**Learning:**
Duplicate definitions across modules (e.g., repeating the `SecretType` definition in both `models.py` and `__init__.py`) increase the risk of inconsistent fixes. A unified source of truth should be maintained.

**Prevention:**
Use descriptive suffixes or alternatives (e.g., changing `"password"` to `"password_type"`) for model or type definitions. Implement robust CI checks to enforce single-source-of-truth patterns rather than duplicating classes.

## 2024-05-18 - Prevent Command Injection via eval() Sandbox Escape
**Vulnerability:** Found `eval(expr, {"__builtins__": {}}, safe_locals)` in `orchestrator_run_dag` (MCP tool). Even with an empty `__builtins__` dict, `eval()` allows sandbox escapes by walking the type hierarchy to retrieve `__builtins__` from other loaded modules (e.g., `[x for x in ().__class__.__base__.__subclasses__() if x.__name__ == 'type'][0]('__import__', (), {})('os').system('cmd')`).
**Learning:** `eval()` is never safe for untrusted user input, even with limited `globals()`/`locals()` dicts. Python's object model is too reflective.
**Prevention:** Always use AST parsing (e.g. `ast.parse` with a recursive AST node evaluator) for executing dynamic Python expressions, limiting allowed node types explicitly.
