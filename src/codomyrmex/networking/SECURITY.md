# Security Policy for Networking Module

This document outlines security procedures and policies for the Networking module.

## Reporting a Vulnerability

If you discover a security vulnerability within this module, please report it to us as soon as possible.
We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email security@codomyrmex.dev with the subject line: "SECURITY Vulnerability Report: Networking Module - [Brief Description]".

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

This security policy applies only to the `Networking` module within the Codomyrmex project. For project-wide security concerns, please refer to the main project's security policy or contact the core project maintainers.

## Security Considerations for Networking Module

### Transport Layer Security

- **TLS/SSL**: All network communications should use TLS 1.2 or higher.
- **Certificate Verification**: SSL certificates must be verified by default.
- **Certificate Pinning**: Optional certificate pinning for high-security scenarios.

### Connection Security

- **Timeout Configuration**: Prevent resource exhaustion with proper timeouts.
- **Connection Pooling**: Secure connection reuse with proper lifecycle management.
- **Proxy Support**: Secure proxy configuration for controlled network access.
- **SSH host keys**: `SSHClient` rejects unknown host keys by default. Never
  replace this with an accepting policy in production; provision trusted host
  keys through `known_hosts_file` or the system known-hosts database. The
  `allow_unknown_host_keys=True` compatibility option is intentionally unsafe
  and should be limited to isolated development environments.

### WebSocket Security

- **Origin Validation**: Verify WebSocket connection origins with an explicit
  allowlist; wildcard origins are not accepted for exposed listeners.
- **Bind Address**: PAI WebSocket push binds to loopback by default. A
  non-loopback bind requires both a bearer token and explicit origins.
- **Message Validation**: Validate all incoming WebSocket messages.
- **Connection Limits**: Prevent resource exhaustion from excessive connections.

### Common Vulnerabilities Mitigated

1. **Man-in-the-Middle (MITM)**: TLS encryption and certificate verification.
2. **Server-Side Request Forgery (SSRF)**: URL validation and allowlisting.
3. **Denial of Service (DoS)**: Timeouts, rate limiting, and connection limits.
4. **DNS Rebinding**: Host header validation and IP allowlisting.
5. **Open Redirects**: URL validation before following redirects.

### Network Security Best Practices

- Never trust user-provided URLs without validation.
- Use allowlists for permitted hosts and IP ranges.
- Implement circuit breakers for external service calls.
- Monitor network traffic for anomalies.

## Best Practices for Using This Module

- Always use the latest stable version of the module.
- Enable TLS/HTTPS for all network communications.
- Verify SSL certificates (never disable verification in production).
- Configure appropriate timeouts for all connections.
- Implement retry logic with exponential backoff.
- Use connection pooling to manage resources efficiently.
- Log network errors for monitoring and debugging.
- Validate URLs before making requests.
- Use IP allowlists for sensitive internal services.
- Follow the principle of least privilege when configuring access or permissions.
- Regularly review configurations and logs for suspicious activity.

## Secure Configuration

```python
# Example secure networking configuration
from codomyrmex.networking import HTTPClient, WebSocketClient

# Configure HTTP client with security defaults
http_client = HTTPClient(
    timeout=30,
    public_only=True,
)

# Configure WebSocket client securely
ws_client = WebSocketClient(
    url="wss://secure.example.com/socket",
    verify_ssl=True,
    origin="https://yourapp.com"
)

# Always handle connection errors gracefully
try:
    response = http_client.get("https://api.example.com/data")
except NetworkError as e:
    logger.error(f"Network request failed: {e}")
```

## Public-only HTTP clients

`HTTPClient(public_only=True)` is an opt-in boundary for a Python caller that
accepts untrusted HTTP(S) destination URLs. The default remains unrestricted for
backward compatibility with intentionally configured local services.

The protected adapter validates each prepared request, including redirect hops.
It rejects URL credentials, `Host` header overrides, explicit proxies, and disabled
TLS certificate verification. It ignores environment proxies and netrc credentials.
Both HTTP and HTTPS connections resolve the hostname at socket creation, reject an
empty answer or any non-public address in the complete answer, and connect directly
to a validated numeric sockaddr without a second hostname resolution. Every new
connection, including a retry, repeats that resolution and validation. Existing
pooled sockets retain the public peer to which they were connected. Original host
names remain intact for the HTTP `Host` header, TLS SNI, and certificate checks.

Non-public includes loopback, private, link-local/metadata, shared-address,
unspecified, multicast, reserved, and documentation ranges. Scoped IPv6, IPv4-mapped
IPv6, NAT64 well-known/local-use prefixes, 6to4, Teredo, and IPv4-compatible IPv6 are
refused rather than inferred safe from their enclosing IPv6 range.

This boundary depends on the requests/urllib3 connection extension API. The locked
dependency versions are the validation target; upgrades need the focused networking
checks. Configure certificate paths explicitly when an environment normally supplies
them. The protected session's adapters must not be replaced by callers.

This option does not authorize outbound access or restrict traffic to approved
public services. It cannot certify host routing, deployment-specific translation
prefixes, public relays, or what a remote server does with received data. Deployments
requiring an enforceable egress boundary should apply network controls too.

The networking MCP tools do not expose arbitrary HTTP requests. The video
transcriber passes caller URLs to an external CLI or REST pipeline; its configured
REST API intentionally defaults to loopback. AgentMail webhook registration submits
callback URLs to the AgentMail SDK, whose service performs later delivery. Neither
path uses this HTTP client. Their MCP wrappers instead deny delegation by default
and require an explicit per-tool host grant through
`CODOMYRMEX_MCP_DELEGATED_URL_TOOLS` before constructing a backend/provider. See the
[delegated URL deployment policy](../model_context_protocol/SECURITY.md#delegated-url-tools).
Enabling a wrapper trusts a separately contained execution environment; it does not
make this HTTP client responsible for the external backend's DNS, redirects, proxies,
or actual destinations. Direct trusted Python backend APIs retain local-service
compatibility.

## Security Audit Checklist

- [ ] TLS 1.2+ is enforced for all connections
- [ ] SSL certificate verification is enabled
- [ ] Timeouts are configured for all connections
- [ ] URL validation is implemented
- [ ] Host allowlisting is configured where appropriate
- [ ] Connection limits are set to prevent DoS
- [ ] Proxy settings are secured (if used)
- [ ] Network errors are logged appropriately
- [ ] Retry logic includes proper backoff
- [ ] WebSocket origins are validated

Thank you for helping keep Codomyrmex and the Networking module secure.
