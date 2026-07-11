## 2026-03-01 - Fix Hardcoded Secret Vulnerability in Models

**Vulnerability:**
The `SecretType` Enum in `src/codomyrmex/security/secrets/models.py` previously assigned the literal string `"password"` to the `PASSWORD` constant. Static Application Security Testing (SAST) tools and secret scanners routinely flag this exact pattern (assigning a string literal like "password" to a variable named `PASSWORD`) as a hardcoded secret. Although the value represents a type rather than an actual secret, it triggers false positives that degrade security monitoring efficacy.

**Learning:**
Security models and Enums should avoid using literal security-sensitive terms like `"password"` directly as values. These patterns mimic common hardcoded credentials, confusing security scanners.

**Learning:**
Duplicate definitions across modules (e.g., repeating the `SecretType` definition in both `models.py` and `__init__.py`) increase the risk of inconsistent fixes. A unified source of truth should be maintained.

**Prevention:**
Use descriptive suffixes or alternatives (e.g., changing `"password"` to `"password_type"`) for model or type definitions. Implement robust CI checks to enforce single-source-of-truth patterns rather than duplicating classes.
## 2025-02-14 - Arbitrary Code Execution via Restricted Eval Bypass in Workflow Scripts
**Vulnerability:** The `ScriptExecutor` in `codomyrmex/testing/workflow/executors.py` was using `eval` to process user-provided strings. Even though it restricted builtins via `{"__builtins__": {}}` and only provided `ctx`, attackers could still exploit this using Python object introspection, e.g., traversing `ctx.__class__.__bases__[0].__subclasses__()` to access dangerous built-ins.
**Learning:** Emptying `__builtins__` is not sufficient to prevent code injection in Python's `eval()`. Without explicitly validating the Abstract Syntax Tree (AST), Python's dynamic object model allows for traversal payloads that recover arbitrary function execution.
**Prevention:** If an expression-evaluator is necessary without a third-party sandbox, explicitly parse the untrusted string with `ast.parse` and walk the AST to explicitly block disallowed nodes (like access to attributes starting with `_`, and calls to `eval`/`exec`).
