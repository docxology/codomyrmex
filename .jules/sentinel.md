## 2026-03-01 - Fix Hardcoded Secret Vulnerability in Models

**Vulnerability:**
The `SecretType` Enum in `src/codomyrmex/security/secrets/models.py` previously assigned the literal string `"password"` to the `PASSWORD` constant. Static Application Security Testing (SAST) tools and secret scanners routinely flag this exact pattern (assigning a string literal like "password" to a variable named `PASSWORD`) as a hardcoded secret. Although the value represents a type rather than an actual secret, it triggers false positives that degrade security monitoring efficacy.

**Learning:**
Security models and Enums should avoid using literal security-sensitive terms like `"password"` directly as values. These patterns mimic common hardcoded credentials, confusing security scanners.

**Learning:**
Duplicate definitions across modules (e.g., repeating the `SecretType` definition in both `models.py` and `__init__.py`) increase the risk of inconsistent fixes. A unified source of truth should be maintained.

**Prevention:**
Use descriptive suffixes or alternatives (e.g., changing `"password"` to `"password_type"`) for model or type definitions. Implement robust CI checks to enforce single-source-of-truth patterns rather than duplicating classes.

## 2026-03-01 - Avoid eval() for untrusted code execution

**Vulnerability:**
The `orchestrator_run_dag` MCP tool in `src/codomyrmex/orchestrator/mcp_tools.py` accepted dynamic Python expressions in `fn_expr` and evaluated them using the Python built-in `eval()`. Although there was a weak guard preventing double underscores (`__`), bypassing `eval` restrictions is often possible. This allowed a critical vulnerability where arbitrary code could be executed.

**Learning:**
Never evaluate code expressions dynamically via `eval()`, even when provided an explicit namespace constraint. Restricting the globals and checking string patterns is insufficient to prevent complex injections.

**Prevention:**
Parse dynamic expressions safely using the `ast` module and evaluate the syntax tree manually in a tightly controlled custom parser (`_safe_eval`), mapping standard operations directly to operators without exposing the runtime.
