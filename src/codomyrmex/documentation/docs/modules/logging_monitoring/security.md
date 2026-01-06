# Security Policy for Logging & Monitoring

This document outlines security procedures, policies, and critical considerations for the Logging & Monitoring module within the Codomyrmex project. The primary purpose of this module is to provide a consistent and configurable way to record application events, but logs themselves can become a source of security risk if not handled properly.

## 1. Introduction

The Logging & Monitoring module provides the `setup_logging()` and `get_logger()` functions to facilitate application-wide logging. While the module itself is simple, the act of logging and the content of logs have significant security implications.

## 2. Core Security Principles for Logging

-   **Data Minimization**: Log only what is necessary for debugging, security auditing, or operational monitoring. Avoid logging sensitive information by default.
-   **Secure by Default**: The logging configuration should promote secure practices (e.g., not logging overly verbose debug messages in production unless explicitly enabled).
-   **Protection of Log Data**: Logs, whether in files or transmitted to a central system, must be protected against unauthorized access, modification, and deletion.
-   **Developer Awareness**: Developers using the logging framework must be aware of what they are logging and the potential sensitivity of that data.

## 3. Threat Model for Logging

-   **Sensitive Data Exposure**: 
    -   Logging Personally Identifiable Information (PII), financial data, health information, API keys, session tokens, passwords, or other credentials.
    -   Logging detailed debugging information that could reveal internal system architecture or vulnerabilities (e.g., full stack traces with sensitive path information in production logs accessible to unauthorized users).
-   **Log Injection**: 
    -   If log messages are constructed by concatenating unsanitized user-supplied input, and the log output format (especially if text-based and parsed by other tools) or terminal interprets control characters (e.g., ANSI escape codes, newline characters `
`, carriage returns `\r` injected into a single log line to spoof other log entries).
    -   Malicious input might attempt to forge log entries or obfuscate legitimate ones.
-   **Insecure Log Storage/Access**: 
    -   Log files (`CODOMYRMEX_LOG_FILE`) created with overly permissive file system permissions, allowing unauthorized users to read, modify, or delete them.
    -   Insecure transmission of logs to a central logging server (e.g., over unencrypted channels).
    -   Weak access controls on centralized log management systems.
-   **Denial of Service (DoS)**:
    -   Excessive logging (intentional or due to an error condition) filling up disk space, leading to application or system failure.
    -   Overwhelming a centralized logging system with a high volume of logs.
-   **Information Leakage via Log Metadata**: 
    -   Log metadata (timestamps, source IP in web logs, usernames) can still be sensitive even if the main message is scrubbed.

## 4. Key Security Measures & Mitigations

-   **Preventing Sensitive Data Exposure**: 
    -   **Responsibility of Calling Code**: The `logging_monitoring` module provides the mechanism but **cannot automatically know what is sensitive**. Developers writing `logger.info(f"User {user_id} accessed {sensitive_data_object}")` are responsible for ensuring `sensitive_data_object` is not logged directly if it contains PII, secrets etc. Log representative, non-sensitive attributes instead, or use placeholders.
    -   **Never log raw API keys, passwords, or session tokens.**
    -   Be cautious with logging entire objects or data structures. Selectively log necessary fields.
    -   Use `DEBUG` level for highly verbose or potentially sensitive diagnostic data, and ensure `CODOMYRMEX_LOG_LEVEL` is set to `INFO` or higher in production.
    -   Consider implementing custom log filters or formatters to automatically scrub known sensitive patterns (e.g., credit card numbers, common API key formats) if such data might accidentally be logged. This is an advanced measure.
    -   If `exc_info=True` is used with `logger.error()` or `logger.exception()`, be aware that stack traces can reveal file paths and code structure. Ensure these logs are appropriately secured.
-   **Mitigating Log Injection**: 
    -   The current `logger_config.py` uses standard Python `logging` which generally handles basic special characters well. When using TEXT format, control characters like newlines in a message are typically escaped or handled by the logger itself, preventing trivial log entry spoofing.
    -   If using JSON output (`CODOMYRMEX_LOG_OUTPUT_TYPE=JSON`), ensure the JSON serialization is done correctly by the underlying handler (the module aims for this). User input should be treated as string data within a JSON field, not as part of the JSON structure itself.
    -   **Best Practice**: When incorporating variable data into log messages, use parameterized logging if the logging library supports it directly (e.g., `logger.info("User %s logged in from %s", username, ip_address)` rather than f-strings for some libraries, though Python's built-in `logging` with f-strings is generally safe for basic injection as arguments are formatted as strings). The main concern is ensuring that data logged doesn't contain control characters that downstream systems misinterpret.
-   **Secure Log Storage & Access**: 
    -   **File Permissions**: When `CODOMYRMEX_LOG_FILE` is used, the application's umask and user permissions will determine the created file's permissions. Ensure the process running the application has a restrictive umask (e.g., `027` or `077`) so log files are not world-readable or writable by default. This is an OS-level configuration.
    -   **Log Directory**: The directory specified for `CODOMYRMEX_LOG_FILE` (e.g., `logs/`) must be protected from unauthorized access.
    -   **Log Rotation**: Implement log rotation (e.g., using `logging.handlers.RotatingFileHandler` or `TimedRotatingFileHandler` if `logger_config.py` were enhanced, or via external tools like `logrotate` on Linux) to prevent log files from growing indefinitely.
    -   **Centralized Logging**: If logs are shipped to a centralized system (e.g., ELK stack, Splunk), ensure transport is encrypted (e.g., TLS) and the system has strong access controls.
-   **Preventing Denial of Service**: 
    -   Implement log rotation (see above).
    -   Monitor disk space on servers where log files are stored.
    -   Be cautious with logging in loops or frequently called functions, especially at `INFO` level or above. Use `DEBUG` for such verbose logging.
    -   Consider rate limiting logs at the source or in the collection pipeline if excessive logging from a particular component becomes an issue (advanced).
-   **Regular Log Review**: Periodically review logs (especially in development/staging) to check for accidental sensitive data leakage or unusual patterns.

## 5. Reporting a Vulnerability

If you discover a security vulnerability related to how the `logging_monitoring` module operates, or if you find that its default configurations or guidance contribute to a security risk (e.g., by making it easy to log sensitive data inadvertently, or creating insecure log files by default within its control):

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email **blanket@activeinference.institute** with the subject line: "**SECURITY Vulnerability Report: Logging & Monitoring - Security Issue**".

Please include relevant details as outlined in the project's main security policy.

## 6. Security Updates

Updates to this module (e.g., to `logger_config.py` to improve security defaults or add features like log scrubbing) will be documented in the [CHANGELOG.md](./CHANGELOG.md).

## 7. Scope

This policy primarily covers the security aspects of the `logging_monitoring` module's configuration and the data it processes (log messages). The security of underlying log storage infrastructure (file systems, remote logging services) or the manual act of logging sensitive data by developers in other modules falls outside the direct control of this module but is guided by this policy.

## 8. Best Practices for Developers Using This Module

-   **Think Before You Log**: Always consider the sensitivity of data before logging it. Avoid logging raw user inputs, full data objects, or any secrets.
-   **Use Appropriate Log Levels**: Use `DEBUG` for verbose, development-time diagnostics. Use `INFO` for general application flow events. Use `WARNING` for recoverable issues. Use `ERROR` or `CRITICAL` for significant failures.
-   **Leverage `exc_info=True` for Errors**: When logging exceptions, use `logger.error("An error occurred", exc_info=True)` or `logger.exception("An error occurred")` to capture stack traces securely.
-   **Configure for Production**: Ensure `CODOMYRMEX_LOG_LEVEL` is `INFO` or higher in production. Use `CODOMYRMEX_LOG_OUTPUT_TYPE=JSON` for better machine processing. Ensure `CODOMYRMEX_LOG_FILE` is configured with appropriate permissions and rotation.
-   **Follow Guidance in this `SECURITY.md`**: Adhere to the principles and mitigation strategies outlined here.

Thank you for helping keep Codomyrmex logging secure and effective. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
