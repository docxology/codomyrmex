# Security Policy for Pattern Matching

This document outlines security procedures and policies for the Pattern Matching module.

## Reporting a Vulnerability

If you discover a security vulnerability within this module, please report it to us as soon as possible.
We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email blanket@activeinference.institute with the subject line: "SECURITY Vulnerability Report: Pattern Matching - Security Issue".

Please include the following information in your report:

- A description of the vulnerability and its potential impact.
- Steps to reproduce the vulnerability, including any specific configurations or conditions required.
- Any proof-of-concept code or examples.
- The version(s) of the module affected.
- Your name and contact information (optional).

We aim to acknowledge receipt of your vulnerability report within 2-3 business days and will work with you to understand and remediate the issue. We may request additional information if needed.

Public disclosure of the vulnerability will be coordinated with you after the vulnerability has been fixed and an update is available, or after a reasonable period if a fix is not immediately possible.

## Security Updates

Security patches and updates for this module will be documented in the module changelog and released as part of regular version updates. Critical vulnerabilities may warrant out-of-band releases.

## Scope

This security policy applies only to the `Pattern Matching` module within the Codomyrmex project. For project-wide security concerns, please refer to the main project's security policy (if available) or contact the core project maintainers.

## Best Practices for Using This Module

- Always use the latest stable version of the module and its dependencies.
- **ReDoS Prevention**: Regular Expression Denial of Service (ReDoS) is a critical security concern when processing user-supplied regular expressions. The module implements several mitigation strategies:

    **Mitigation Strategies**:
    1. **Timeout Protection**: All regex operations that process user-supplied patterns should use timeout mechanisms:
       ```python
       import signal

       def safe_regex_search(pattern, text, timeout=5):
           def timeout_handler(signum, frame):
               raise TimeoutError("Regex operation timed out")

           signal.signal(signal.SIGALRM, timeout_handler)
           signal.alarm(timeout)
           try:
               result = re.search(pattern, text)
           finally:
               signal.alarm(0)
           return result
       ```

    2. **Pattern Complexity Validation**: Validate regex patterns before execution:
       - Limit quantifier nesting depth (e.g., `{n,m}` should not be deeply nested)
       - Detect catastrophic backtracking patterns (e.g., `(a+)+b`)
       - Reject patterns with excessive alternations (`|`)
       - Limit pattern length to reasonable bounds (e.g., 1000 characters)

    3. **Input Text Limits**:
       - Limit the length of input text processed by user-supplied regexes (e.g., max 10MB)
       - For file-based searches, process files in chunks rather than loading entire files
       - Implement resource quotas for regex operations

    4. **Regex Engine Selection**:
       - Consider using `regex` library (backtracking-limited) instead of `re` for untrusted patterns
       - Use RE2 (via `google-re2` Python bindings) for production systems handling untrusted input
       - Document which regex engine is used in each function

    5. **Monitoring and Logging**:
       - Log all regex operations that exceed normal execution time
       - Monitor for patterns that consistently cause performance issues
       - Alert on regex operations that exceed resource thresholds

    **Implementation in Pattern Matching Module**:
    - The `search_text_pattern` MCP tool validates pattern complexity before execution
    - Text search operations have configurable timeout limits
    - File processing is chunked to prevent memory exhaustion
    - All regex operations are logged with execution time for monitoring
- **AST Parsing Security**: If using Abstract Syntax Tree (AST) based matching on code from untrusted sources:
    - Ensure the AST parsing library is robust and kept up-to-date against known vulnerabilities.
    - Be aware that malformed code could cause the parser to crash or consume excessive resources.
- **Semantic Matching Risks**: If semantic matching involves sending code/text to external LLMs or embedding models:
    - Ensure API keys are handled securely (as per `ai_code_editing` guidelines).
    - Be mindful of data privacy if sending sensitive code/text to third-party services.
- **Resource Limits**: Pattern matching against very large inputs or with extremely complex patterns (regex, AST queries, semantic models) can consume significant CPU and memory. Implement timeouts or resource controls at the application level if necessary.
- **Input Validation**: Validate inputs to pattern matching functions (e.g., pattern syntax, input types) to prevent errors or unexpected behavior.
- **Output Handling**: Sanitize or validate outputs if they are derived from matched content and might be displayed or used in sensitive contexts.
- Follow the principle of least privilege when configuring access or permissions related to this module.
- Regularly review configurations and logs for suspicious activity.

Thank you for helping keep Codomyrmex and the Pattern Matching module secure.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
