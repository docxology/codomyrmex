# Security Policy for LLM Module

## Overview

The LLM (Large Language Model) module handles interactions with language models including Ollama and other providers. Security is critical as this module processes potentially sensitive prompts and responses, and interacts with external AI services.

## Security Considerations

### Input Security

1. **Prompt Sanitization**: Sanitize user inputs before sending to LLMs to prevent prompt injection.
2. **Input Validation**: Validate prompt length, format, and content.
3. **Rate Limiting**: Implement rate limits to prevent abuse and cost overruns.
4. **Content Filtering**: Optionally filter prompts for prohibited content before processing.

### Output Security

1. **Response Validation**: Validate LLM responses before returning to callers.
2. **Sensitive Data Detection**: Detect and handle potentially sensitive information in responses.
3. **Output Sanitization**: Sanitize outputs if they will be rendered or executed.
4. **Response Logging**: Log responses appropriately without exposing sensitive data.

### External Service Communication

1. **API Key Protection**: Never expose API keys in logs, errors, or client-side code.
2. **TLS/HTTPS**: Always use encrypted connections to LLM providers.
3. **Timeout Handling**: Implement proper timeouts to prevent hanging connections.
4. **Error Handling**: Handle API errors without exposing internal details.

### Local Model Security (Ollama)

1. **Model Source Verification**: Verify model integrity when downloading.
2. **Resource Limits**: Limit GPU/CPU/memory usage to prevent resource exhaustion.
3. **Execution Isolation**: Isolate model execution from sensitive system resources.
4. **Model Access Control**: Control which users/processes can run which models.

## Portable MLX Profiling Artifacts

The portable collector constructs synthetic `MLXConfig` values without native
MLX imports, model loading, provider requests, or credentials. Its PEP 723
dependency installation can require network access; the generated dashboard has
no scripts or remote assets. It does not collect inference or Metal metrics.

- Treat environment/build/dependency metadata, revision/dirty status, source
  hashes, and profiler filenames/function names as potentially identifying.
  Basename-only hotspots and synthetic model/cache paths are not anonymization.
- Use a trusted output location and restrict access before collecting. Symlink
  output directories and existing named artifacts are rejected; exclusive file
  creation is not a sandbox, permission policy, or atomic bundle transaction.
  Preserve partial failures and retry at a fresh location.
- HTML/SVG renderers escape dynamic content, and Markdown metadata is normalized
  and encoded as literal text. These protections do not authorize executing
  imported report content or accepting arbitrary bundles as trusted evidence.
- Bundle validation rejects inconsistent median/MAD versus raw samples, invalid
  numeric evidence, and noninteger allocations or retained bytes exceeding peak.
  Validation checks consistency, not scientific truth or provenance authenticity.
- The final SHA-256 manifest detects changed bytes, not malicious replacement of
  both report and manifest. Review the source snapshot and revision/dirty state
  independently before sharing or trusting results. Missing manifests identify
  incomplete output.
- Active tracemalloc, CPU profiling, tracing, or monitoring is rejected without
  taking over caller instrumentation. Use an uninstrumented subprocess under
  coverage; do not disable another agent's diagnostic session.

See the [profiling study](../../../docs/modules/llm/mlx-profiling-study.md) and
[script agent workflow](../../../scripts/llm/PAI.md#portable-mlx-configuration-evidence).

## Threat Model

| Threat | Impact | Mitigation |
| --- | --- | --- |
| Prompt injection | Unauthorized actions | Input sanitization, prompt design |
| API key exposure | Account compromise | Environment variables, secrets management |
| Response data leakage | Information disclosure | Response filtering, secure logging |
| Model poisoning | Corrupted outputs | Model verification, trusted sources |
| Resource exhaustion | DoS | Rate limiting, resource quotas |
| Man-in-the-middle | Data interception | TLS, certificate validation |

## Secure Implementation Patterns

```python
# Example: Secure LLM request handling
class SecureLLMClient:
    def __init__(self, api_key: str):
        # Never log or expose the API key
        self._api_key = api_key
        self._rate_limiter = RateLimiter(max_requests_per_minute=60)

    async def generate(self, prompt: str, user_id: str) -> str:
        """Securely generate LLM response."""
        # Rate limiting
        if not self._rate_limiter.allow(user_id):
            raise RateLimitError("Too many requests")

        # Validate and sanitize input
        sanitized_prompt = self._sanitize_prompt(prompt)
        if len(sanitized_prompt) > MAX_PROMPT_LENGTH:
            raise ValidationError("Prompt too long")

        # Make secure request
        try:
            response = await self._make_request(sanitized_prompt)
        except Exception as e:
            # Log error without exposing details
            logger.error(f"LLM request failed for user {user_id}")
            raise LLMError("Generation failed") from None

        # Filter response
        filtered_response = self._filter_response(response)

        # Audit log (without sensitive content)
        audit_log.record_llm_request(
            user_id=user_id,
            prompt_length=len(sanitized_prompt),
            response_length=len(filtered_response)
        )

        return filtered_response

    def _sanitize_prompt(self, prompt: str) -> str:
        """Sanitize prompt to prevent injection."""
        # Remove potential injection patterns
        # Implementation depends on use case
        return prompt.strip()
```

## API Key Management

1. Store API keys in environment variables or secure vaults
2. Rotate keys regularly
3. Use separate keys for development and production
4. Monitor key usage for anomalies

## Compliance

- Log all LLM interactions for audit purposes
- Ensure data handling complies with privacy regulations
- Document model usage and data retention policies

## Vulnerability Reporting

Report security vulnerabilities via the main project's security reporting process. Include:

- Provider/model affected
- Type of vulnerability (injection, exposure, etc.)
- Steps to reproduce
