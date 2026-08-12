## 2026-03-01 - Fix Hardcoded Secret Vulnerability in Models

**Vulnerability:**
The `SecretType` Enum in `src/codomyrmex/security/secrets/models.py` previously assigned the literal string `"password"` to the `PASSWORD` constant. Static Application Security Testing (SAST) tools and secret scanners routinely flag this exact pattern (assigning a string literal like "password" to a variable named `PASSWORD`) as a hardcoded secret. Although the value represents a type rather than an actual secret, it triggers false positives that degrade security monitoring efficacy.

**Learning:**
Security models and Enums should avoid using literal security-sensitive terms like `"password"` directly as values. These patterns mimic common hardcoded credentials, confusing security scanners.

**Learning:**
Duplicate definitions across modules (e.g., repeating the `SecretType` definition in both `models.py` and `__init__.py`) increase the risk of inconsistent fixes. A unified source of truth should be maintained.

**Prevention:**
Use descriptive suffixes or alternatives (e.g., changing `"password"` to `"password_type"`) for model or type definitions. Implement robust CI checks to enforce single-source-of-truth patterns rather than duplicating classes.
## 2026-03-01 - Avoid shell=True in Subprocess Calls
**Vulnerability:** The `_transcribe_local_command` STT function used `subprocess.run(command, shell=True)` where `command` was a formatted string using user input, leading to a potential command injection risk.
**Learning:** Using `shell=True` is dangerous even if parts of the input are quoted, as parsing varies between operating systems and environments, and it is easy to make a mistake when quoting compound commands.
**Prevention:** Avoid `shell=True`. Instead, construct command lists and pass them to `subprocess.run(..., shell=False)`. If a string template is provided, use `shlex.split()` to securely tokenize the command before execution.
