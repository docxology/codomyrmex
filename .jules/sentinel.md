## 2026-03-01 - Fix Hardcoded Secret Vulnerability in Models

**Vulnerability:**
The `SecretType` Enum in `src/codomyrmex/security/secrets/models.py` previously assigned the literal string `"password"` to the `PASSWORD` constant. Static Application Security Testing (SAST) tools and secret scanners routinely flag this exact pattern (assigning a string literal like "password" to a variable named `PASSWORD`) as a hardcoded secret. Although the value represents a type rather than an actual secret, it triggers false positives that degrade security monitoring efficacy.

**Learning:**
Security models and Enums should avoid using literal security-sensitive terms like `"password"` directly as values. These patterns mimic common hardcoded credentials, confusing security scanners.

**Learning:**
Duplicate definitions across modules (e.g., repeating the `SecretType` definition in both `models.py` and `__init__.py`) increase the risk of inconsistent fixes. A unified source of truth should be maintained.

**Prevention:**
Use descriptive suffixes or alternatives (e.g., changing `"password"` to `"password_type"`) for model or type definitions. Implement robust CI checks to enforce single-source-of-truth patterns rather than duplicating classes.
## 2026-07-20 - Command Injection in STT Tools
**Vulnerability:** A command injection vulnerability existed in `src/codomyrmex/agents/open_gauss/tools/transcription_tools.py` where `subprocess.run()` executed a local string command with `shell=True`.
**Learning:** The use of `shell=True` with dynamically formatted strings exposes the system to command injection, even if some variables are quoted. It requires shell invocation, leading to potential execution of arbitrary code.
**Prevention:** Securely resolve command injection vulnerabilities by tokenizing the command string into a list of arguments using `shlex.split()` and executing with `shell=False`.
