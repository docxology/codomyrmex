# Security Policy for Git Operations Module

## Overview

The Git Operations module handles interactions with Git repositories and the GitHub API. Security is critical as this module processes sensitive credentials, executes shell commands, and interacts with remote repositories containing potentially sensitive codebases.

## Security Considerations

### Credential Management

1. **GitHub Token Protection**: Never expose `GITHUB_TOKEN` in logs, error messages, or client-side code.
2. **SSH Key Security**: Protect SSH private keys used for repository access.
3. **Credential Storage**: Use environment variables or secure vaults for credential storage.
4. **Token Rotation**: Implement regular rotation of API tokens and access credentials.

### Command Injection Prevention

1. **Input Sanitization**: Sanitize all user inputs before passing to Git commands.
2. **Path Validation**: Validate repository paths to prevent directory traversal attacks.
3. **Branch Name Validation**: Validate branch names to prevent injection via malformed names.
4. **Commit Message Sanitization**: Sanitize commit messages to prevent command injection.

### Repository Security

1. **Clone Validation**: Verify repository URLs before cloning to prevent SSRF attacks.
2. **Submodule Security**: Validate submodule URLs to prevent malicious repository inclusion.
3. **Hook Security**: Disable or validate Git hooks when cloning untrusted repositories.
4. **LFS Security**: Validate Large File Storage objects before downloading.

### Remote Communication

1. **TLS/HTTPS**: Always use encrypted connections to remote repositories.
2. **Certificate Validation**: Verify SSL certificates for all HTTPS connections.
3. **Timeout Handling**: Implement proper timeouts to prevent hanging operations.
4. **Error Handling**: Handle errors without exposing internal credentials or paths.

## Threat Model

| Threat | Impact | Mitigation |
|--------|--------|------------|
| Credential exposure | Account compromise | Environment variables, secrets management |
| Command injection | Remote code execution | Input sanitization, parameterized commands |
| Directory traversal | Unauthorized file access | Path validation, sandboxing |
| SSRF via clone URL | Internal network access | URL validation, allowlists |
| Malicious Git hooks | Code execution | Disable hooks, use `--no-hooks` |
| Token leakage in logs | Credential theft | Sanitize logs, mask tokens |
| Man-in-the-middle | Data interception | TLS, certificate pinning |
| Repository tampering | Code integrity loss | Signed commits, GPG verification |

## Secure Implementation Patterns

```python
# Example: Secure Git command execution
import subprocess
import re
from pathlib import Path

class SecureGitOperations:
    # Patterns for validating Git inputs
    BRANCH_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9/_-]+$')
    REMOTE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')

    def __init__(self, repo_path: str, token: str = None):
        # Never log or expose credentials
        self._token = token
        self._repo_path = self._validate_path(repo_path)

    def _validate_path(self, path: str) -> Path:
        """Validate repository path to prevent traversal."""
        resolved = Path(path).resolve()
        # Ensure path is within allowed directory
        if not str(resolved).startswith(str(ALLOWED_BASE_DIR)):
            raise SecurityError("Repository path outside allowed directory")
        return resolved

    def _validate_branch_name(self, branch: str) -> str:
        """Validate branch name to prevent injection."""
        if not self.BRANCH_NAME_PATTERN.match(branch):
            raise ValidationError("Invalid branch name format")
        return branch

    def _run_git_command(self, args: list[str]) -> str:
        """Securely run Git commands."""
        # Prepend git command
        full_command = ['git'] + args

        # Set up secure environment
        env = os.environ.copy()
        if self._token:
            # Use credential helper instead of embedding token
            env['GIT_ASKPASS'] = '/path/to/secure/credential/helper'

        try:
            result = subprocess.run(
                full_command,
                cwd=self._repo_path,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            raise GitError("Operation timed out")
        except Exception as e:
            # Log error without exposing credentials
            logger.error(f"Git operation failed: {type(e).__name__}")
            raise GitError("Operation failed") from None

    def checkout_branch(self, branch: str) -> None:
        """Securely checkout a branch."""
        validated_branch = self._validate_branch_name(branch)
        self._run_git_command(['checkout', validated_branch])

    def clone_repository(self, url: str, dest: str) -> None:
        """Securely clone a repository."""
        # Validate URL format and allowed hosts
        validated_url = self._validate_clone_url(url)
        validated_dest = self._validate_path(dest)

        # Clone without hooks for untrusted repos
        self._run_git_command([
            'clone',
            '--no-checkout',  # Defer checkout until validated
            validated_url,
            str(validated_dest)
        ])

        # Disable hooks in cloned repository
        hooks_dir = validated_dest / '.git' / 'hooks'
        if hooks_dir.exists():
            for hook in hooks_dir.iterdir():
                if hook.is_file():
                    hook.chmod(0o644)  # Remove execute permission
```

## GitHub API Security

1. **Token Scoping**: Use tokens with minimum required permissions.
2. **Rate Limiting**: Implement rate limiting to prevent abuse.
3. **Webhook Validation**: Validate webhook payloads with HMAC signatures.
4. **API Response Validation**: Validate API responses before processing.

## High-Risk Components

### core/git.py
- Executes Git shell commands
- Risk: Command injection through unsanitized inputs
- Mitigation: Input validation, parameterized commands

### api/github.py
- Handles GitHub API authentication
- Risk: Token exposure, API abuse
- Mitigation: Secure credential handling, rate limiting

### cli/
- Accepts user input from command line
- Risk: Injection via CLI arguments
- Mitigation: Argument parsing, validation

### tools/
- Git utility functions
- Risk: Path traversal, unsafe operations
- Mitigation: Path validation, sandboxing

## Best Practices for Using This Module

1. **Never embed credentials** - Use environment variables or secure vaults.
2. **Validate all inputs** - Sanitize branch names, paths, and URLs.
3. **Use HTTPS** - Always prefer HTTPS over SSH for remote operations.
4. **Disable hooks** - When cloning untrusted repositories, disable Git hooks.
5. **Audit operations** - Log all Git operations for security auditing.
6. **Limit permissions** - Use tokens with minimum required scopes.
7. **Verify signatures** - Enable GPG verification for commits when possible.
8. **Monitor activity** - Track unusual patterns in Git operations.

## Compliance

- Log all repository operations for audit purposes.
- Ensure credential handling complies with security policies.
- Document access patterns and data retention policies.

## Vulnerability Reporting

Report security vulnerabilities via the main project's security reporting process. Include:
- Type of vulnerability (injection, exposure, etc.)
- Affected component (core, api, cli, tools)
- Steps to reproduce
- Potential impact

**DO NOT report security vulnerabilities through public GitHub issues.**

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
