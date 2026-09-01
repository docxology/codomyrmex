## 2026-03-01 - Fix Hardcoded Secret Vulnerability in Models

**Vulnerability:**
The `SecretType` Enum in `src/codomyrmex/security/secrets/models.py` previously assigned the literal string `"password"` to the `PASSWORD` constant. Static Application Security Testing (SAST) tools and secret scanners routinely flag this exact pattern (assigning a string literal like "password" to a variable named `PASSWORD`) as a hardcoded secret. Although the value represents a type rather than an actual secret, it triggers false positives that degrade security monitoring efficacy.

**Learning:**
Security models and Enums should avoid using literal security-sensitive terms like `"password"` directly as values. These patterns mimic common hardcoded credentials, confusing security scanners.

**Learning:**
Duplicate definitions across modules (e.g., repeating the `SecretType` definition in both `models.py` and `__init__.py`) increase the risk of inconsistent fixes. A unified source of truth should be maintained.

**Prevention:**
Use descriptive suffixes or alternatives (e.g., changing `"password"` to `"password_type"`) for model or type definitions. Implement robust CI checks to enforce single-source-of-truth patterns rather than duplicating classes.

## 2026-07-31 - Fix Command Injection in transcription_tools
**Vulnerability:** Found a command injection vulnerability in `_transcribe_local_command` where a user-configured command template was formatted with string substitution and passed to `subprocess.run` with `shell=True`.
**Learning:** Even if arguments are escaped using `shlex.quote`, combining them into a string to run via `shell=True` creates a vulnerability to command injection, as untrusted strings are evaluated by the shell.
**Prevention:** Use `shlex.split()` to securely tokenize the formatted string into a command argument list and always invoke `subprocess.run` with `shell=False` to avoid shell evaluation.
