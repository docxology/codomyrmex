## 2026-03-01 - Fix Hardcoded Secret Vulnerability in Models

**Vulnerability:**
The `SecretType` Enum in `src/codomyrmex/security/secrets/models.py` previously assigned the literal string `"password"` to the `PASSWORD` constant. Static Application Security Testing (SAST) tools and secret scanners routinely flag this exact pattern (assigning a string literal like "password" to a variable named `PASSWORD`) as a hardcoded secret. Although the value represents a type rather than an actual secret, it triggers false positives that degrade security monitoring efficacy.

**Learning:**
Security models and Enums should avoid using literal security-sensitive terms like `"password"` directly as values. These patterns mimic common hardcoded credentials, confusing security scanners.

**Learning:**
Duplicate definitions across modules (e.g., repeating the `SecretType` definition in both `models.py` and `__init__.py`) increase the risk of inconsistent fixes. A unified source of truth should be maintained.

**Prevention:**
Use descriptive suffixes or alternatives (e.g., changing `"password"` to `"password_type"`) for model or type definitions. Implement robust CI checks to enforce single-source-of-truth patterns rather than duplicating classes.
## 2026-03-01 - Fix command injection in local STT command
**Vulnerability:** Found an instance where subprocess.run was used with shell=True for dynamically formatted CLI commands (e.g. executing local faster-whisper), presenting a potential command injection vector despite shlex.quote.
**Learning:** Relying purely on shlex.quote while maintaining shell=True is an anti-pattern. While it handles space escapes, it's safer to avoid the shell entirely.
**Prevention:** Always use shell=False combined with shlex.split to securely tokenize command templates before passing them to subprocess.run.
