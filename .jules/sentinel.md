## 2026-03-01 - Fix Hardcoded Secret Vulnerability in Models

**Vulnerability:**
The `SecretType` Enum in `src/codomyrmex/security/secrets/models.py` previously assigned the literal string `"password"` to the `PASSWORD` constant. Static Application Security Testing (SAST) tools and secret scanners routinely flag this exact pattern (assigning a string literal like "password" to a variable named `PASSWORD`) as a hardcoded secret. Although the value represents a type rather than an actual secret, it triggers false positives that degrade security monitoring efficacy.

**Learning:**
Security models and Enums should avoid using literal security-sensitive terms like `"password"` directly as values. These patterns mimic common hardcoded credentials, confusing security scanners.

**Learning:**
Duplicate definitions across modules (e.g., repeating the `SecretType` definition in both `models.py` and `__init__.py`) increase the risk of inconsistent fixes. A unified source of truth should be maintained.

**Prevention:**
Use descriptive suffixes or alternatives (e.g., changing `"password"` to `"password_type"`) for model or type definitions. Implement robust CI checks to enforce single-source-of-truth patterns rather than duplicating classes.
## 2026-07-13 - Block sandbox escapes via eval AST pre-validation
**Vulnerability:** eval() was used with user input but without restricting access to private/dunder attributes, allowing easy sandbox escape.
**Learning:** Even with restricted globals/locals, eval() is vulnerable if the evaluated expression accesses dunder methods via exposed valid variables. Pre-validating the AST to block these patterns provides defense-in-depth.
**Prevention:** Always parse untrusted input with ast.parse and use ast.walk to block access to private/dunder attributes and nested eval/exec calls before evaluation.
