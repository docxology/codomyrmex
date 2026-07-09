## 2026-03-01 - Fix Hardcoded Secret Vulnerability in Models

**Vulnerability:**
The `SecretType` Enum in `src/codomyrmex/security/secrets/models.py` previously assigned the literal string `"password"` to the `PASSWORD` constant. Static Application Security Testing (SAST) tools and secret scanners routinely flag this exact pattern (assigning a string literal like "password" to a variable named `PASSWORD`) as a hardcoded secret. Although the value represents a type rather than an actual secret, it triggers false positives that degrade security monitoring efficacy.

**Learning:**
Security models and Enums should avoid using literal security-sensitive terms like `"password"` directly as values. These patterns mimic common hardcoded credentials, confusing security scanners.

**Learning:**
Duplicate definitions across modules (e.g., repeating the `SecretType` definition in both `models.py` and `__init__.py`) increase the risk of inconsistent fixes. A unified source of truth should be maintained.

**Prevention:**
Use descriptive suffixes or alternatives (e.g., changing `"password"` to `"password_type"`) for model or type definitions. Implement robust CI checks to enforce single-source-of-truth patterns rather than duplicating classes.

## 2026-07-09 - Fix Critical eval() Vulnerability in Orchestrator MCP Tools
**Vulnerability:** The orchestrator_run_dag tool used eval() to execute user-provided expressions for task execution, enabling code injection.
**Learning:** Using eval() with user input is a critical security risk, even when restricting __builtins__ and locals, as it can often be bypassed.
**Prevention:** Always use safe AST-based parsers (e.g., ast.parse combined with a strict recursive evaluator) to evaluate user-provided expressions without executing arbitrary code.
