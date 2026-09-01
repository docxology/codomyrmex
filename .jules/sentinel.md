## 2026-03-01 - Fix Hardcoded Secret Vulnerability in Models

**Vulnerability:**
The `SecretType` Enum in `src/codomyrmex/security/secrets/models.py` previously assigned the literal string `"password"` to the `PASSWORD` constant. Static Application Security Testing (SAST) tools and secret scanners routinely flag this exact pattern (assigning a string literal like "password" to a variable named `PASSWORD`) as a hardcoded secret. Although the value represents a type rather than an actual secret, it triggers false positives that degrade security monitoring efficacy.

**Learning:**
Security models and Enums should avoid using literal security-sensitive terms like `"password"` directly as values. These patterns mimic common hardcoded credentials, confusing security scanners.

**Learning:**
Duplicate definitions across modules (e.g., repeating the `SecretType` definition in both `models.py` and `__init__.py`) increase the risk of inconsistent fixes. A unified source of truth should be maintained.

**Prevention:**
Use descriptive suffixes or alternatives (e.g., changing `"password"` to `"password_type"`) for model or type definitions. Implement robust CI checks to enforce single-source-of-truth patterns rather than duplicating classes.

## 2024-07-28 - [CRITICAL] Fix command injection vulnerability in subprocess.run
**Vulnerability:** Found subprocess.run executing a user-interpolated command string with shell=True, presenting a command injection risk even with shlex.quote.
**Learning:** shlex.split() properly handles tokenizing strings that contain shlex.quote() portions, so it can be safely used to transition from shell=True to shell=False without losing argument grouping.
**Prevention:** Avoid shell=True for all subprocess.run calls containing external inputs, use shell=False with properly list-tokenized command arguments.
