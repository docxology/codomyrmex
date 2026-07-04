## 2026-03-01 - Fix Hardcoded Secret Vulnerability in Models

**Vulnerability:**
The `SecretType` Enum in `src/codomyrmex/security/secrets/models.py` previously assigned the literal string `"password"` to the `PASSWORD` constant. Static Application Security Testing (SAST) tools and secret scanners routinely flag this exact pattern (assigning a string literal like "password" to a variable named `PASSWORD`) as a hardcoded secret. Although the value represents a type rather than an actual secret, it triggers false positives that degrade security monitoring efficacy.

**Learning:**
Security models and Enums should avoid using literal security-sensitive terms like `"password"` directly as values. These patterns mimic common hardcoded credentials, confusing security scanners.

**Learning:**
Duplicate definitions across modules (e.g., repeating the `SecretType` definition in both `models.py` and `__init__.py`) increase the risk of inconsistent fixes. A unified source of truth should be maintained.

**Prevention:**
Use descriptive suffixes or alternatives (e.g., changing `"password"` to `"password_type"`) for model or type definitions. Implement robust CI checks to enforce single-source-of-truth patterns rather than duplicating classes.

## 2026-03-01 - Fix Command Injection in subprocess calls

**Vulnerability:**
The `_execute_hooks` method in `src/codomyrmex/ci_cd_automation/deployment_orchestrator.py` executed CI/CD deployment hooks (user-provided or configuration-provided strings) using `subprocess.run(hook, shell=True)`. This represents a severe command injection vulnerability because a malicious actor could embed arbitrary shell commands (e.g., `hook = "echo hello; rm -rf /"`).

**Learning:**
Even within internal orchestration tools or deployment workflows, strings passed to subprocess should never use `shell=True` unless strictly necessary and perfectly sanitized. Refactoring from `shell=True` to `shell=False` requires handling shell built-ins in tests (e.g. replacing `exit 1` with `false`).

**Prevention:**
Always use `shell=False`. When dealing with raw command strings that need to be executed cross-platform, handle Windows appropriately (`cmd = hook` if `os.name == 'nt'`) and use `shlex.split(hook)` on POSIX systems to securely parse the string into an argument list before passing it to `subprocess.run()`.
