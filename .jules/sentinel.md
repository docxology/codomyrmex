## 2024-05-24 - Arbitrary Code Execution in Autograd MCP Tools
**Vulnerability:** The `autograd_compute` tool previously used `eval()` to execute user-supplied strings directly, leading to arbitrary code execution risks.
**Learning:** Avoid using `eval()` for executing untrusted input strings, even if providing a restricted namespace.
**Learning:** Replacing `eval()` with safe AST evaluation allows execution of complex mathematical expressions while explicitly whitelisting the operators and node types, avoiding malicious payloads.
**Prevention:** Always use safe expression parsers, AST processing, or domain-specific language parsers for dynamically executing code derived from users or external systems instead of `eval()` or `exec()`.
