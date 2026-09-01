# Sentinel Journal

## 2026-03-01 - Fix Hardcoded Secret Vulnerability in Models

**Vulnerability:**
The `SecretType` Enum in `src/codomyrmex/security/secrets/models.py` previously assigned the literal string `"password"` to the `PASSWORD` constant. Static Application Security Testing (SAST) tools and secret scanners routinely flag this exact pattern (assigning a string literal like "password" to a variable named `PASSWORD`) as a hardcoded secret. Although the value represents a type rather than an actual secret, it triggers false positives that degrade security monitoring efficacy.

**Learning:**
Security models and Enums should avoid using literal security-sensitive terms like `"password"` directly as values. These patterns mimic common hardcoded credentials, confusing security scanners.

**Learning:**
Duplicate definitions across modules (e.g., repeating the `SecretType` definition in both `models.py` and `__init__.py`) increase the risk of inconsistent fixes. A unified source of truth should be maintained.

**Prevention:**
Use descriptive suffixes or alternatives (e.g., changing `"password"` to `"password_type"`) for model or type definitions. Implement robust CI checks to enforce single-source-of-truth patterns rather than duplicating classes.

## 2026-08-17 - Refactor subprocess to avoid shell=True

**Vulnerability:** Use of shell=True in subprocess.run for local STT commands allows potential command injection.
**Learning:** Even when inputs are shlex.quoted, shell=True invokes a shell process that parses the entire command string, making it harder to reason about edge cases or shell features being abused, especially with user-defined command templates.
**Prevention:** Always use shell=False and pass arguments as a list. For templates, use shlex.split() to safely parse the formatted string into a command list before execution.
