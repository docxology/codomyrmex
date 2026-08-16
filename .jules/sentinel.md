## 2026-03-01 - Fix Hardcoded Secret Vulnerability in Models

**Vulnerability:**
The `SecretType` Enum in `src/codomyrmex/security/secrets/models.py` previously assigned the literal string "password" to the `PASSWORD` constant. Static Application Security Testing (SAST) tools and secret scanners routinely flag this exact pattern (assigning a string literal like "password" to a variable named `PASSWORD`) as a hardcoded secret. Although the value represents a type rather than an actual secret, it triggers false positives that degrade security monitoring efficacy.

**Learning:**
Security models and Enums should avoid using literal security-sensitive terms like "password" directly as values. These patterns mimic common hardcoded credentials, confusing security scanners.

**Learning:**
Duplicate definitions across modules (e.g., repeating the `SecretType` definition in both `models.py` and `__init__.py`) increase the risk of inconsistent fixes. A unified source of truth should be maintained.

**Prevention:**
Use descriptive suffixes or alternatives (e.g., changing "password" to "password_type") for model or type definitions. Implement robust CI checks to enforce single-source-of-truth patterns rather than duplicating classes.

## 2024-08-16 - Command Injection in STT Tools

**Vulnerability:** `subprocess.run` used `shell=True` with an environment-provided string template for local STT transcription commands. An attacker controlling the environment variable could inject arbitrary shell commands.

**Learning:** Even if variables interpolated into a command template are safely quoted via `shlex.quote`, the template itself can be dangerous if it is executed with `shell=True` and sourced externally. Always use `shell=False` by processing the template string with `shlex.split` after interpolation, allowing `subprocess.run` to safely execute the command as a list.

**Prevention:** Prohibit `shell=True` globally. Ensure all subprocess commands are passed as lists. For templated shell commands, interpolate safely quoted variables and then parse the result with `shlex.split()` before execution.
