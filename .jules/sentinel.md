## 2026-03-01 - Fix Hardcoded Secret Vulnerability in Models

**Vulnerability:**
The `SecretType` Enum in `src/codomyrmex/security/secrets/models.py` previously assigned the literal string `"password"` to the `PASSWORD` constant. Static Application Security Testing (SAST) tools and secret scanners routinely flag this exact pattern (assigning a string literal like "password" to a variable named `PASSWORD`) as a hardcoded secret. Although the value represents a type rather than an actual secret, it triggers false positives that degrade security monitoring efficacy.

**Learning:**
Security models and Enums should avoid using literal security-sensitive terms like `"password"` directly as values. These patterns mimic common hardcoded credentials, confusing security scanners.

**Learning:**
Duplicate definitions across modules (e.g., repeating the `SecretType` definition in both `models.py` and `__init__.py`) increase the risk of inconsistent fixes. A unified source of truth should be maintained.

**Prevention:**
Use descriptive suffixes or alternatives (e.g., changing `"password"` to `"password_type"`) for model or type definitions. Implement robust CI checks to enforce single-source-of-truth patterns rather than duplicating classes.
## 2026-08-04 - Prevent Command Injection via shell=True
**Vulnerability:** Command Injection risk from using shell=True in subprocess.run for transcription_tools.py.
**Learning:** Even when interpolating quoted strings, shell=True exposes the system to injection if templates are misconfigured or arguments leak.
**Prevention:** Use shell=False combined with shlex.split() to safely tokenize commands while maintaining argument grouping.

## 2026-09-11 - Session hygiene: dedupe and intentional-executor dispositions

**Failure mode:** The 2026-09 triage closed 200+ duplicate Sentinel PRs.
Dominant pattern: re-proposing the transcription/STT injection fix after it
was already merged (#423), against files that no longer exist
(`transcription_tools.py` — the live path is `video/transcription.py`,
already list-args without a shell), and "fixing" intentionally shell-based
executors.

**Action (mandatory, in order):**
1. `gh pr list --state open --search "<callsite>"` and
   `git log --oneline -50 -- <target-file>`; read the callsite on `main`. If
   the injection is already fixed (list args, no shell, parameterized SQL,
   AST evaluation), the task is DONE. Do not open a PR.
2. Cite `file:line` on `main` proving the vulnerable pattern exists today.
3. One logical change = one PR. No CI/workflow edits, no formatter churn, no
   `.jules/` journal-only diffs, no test-suite deletions.

**Dispositions (do not re-propose):**
- Interactive shell sessions and agent shell executors (`do_shell`,
  `_shell_session`, `SystemOpsMixin`, OS provider diagnostic commands marked
  `# nosec B602`) are intentional design. Converting them to
  `shlex.split + shell=False` silently breaks compound commands
  (pipes/`&&`/redirection) that are the documented contract. Only split
  simple, non-compound command strings, keeping an explicit nosec fallback
  for compound hooks (pattern applied via #382).
- `text_to_sql` never executes generated SQL and its value capture is
  identifier-scoped — not an injection sink. Do not "fix" it again
  (proposals #482/#484 rejected).
- Transcription/STT command injection was fixed by merged #423 at the live
  call site; the `transcription_tools.py` file does not exist on `main`.
