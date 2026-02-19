# Security Considerations for Scrape Module

**Version**: v0.1.7 | **Last Updated**: February 2026

## Overview

This document outlines security considerations and best practices for using the scrape module. Web scraping involves accessing external resources and handling potentially sensitive data, so proper security measures are essential.

## API Key Management

### Secure Storage
- **Never commit API keys to version control**
- Store API keys in environment variables or secure configuration files
- Use `.env` files with `.gitignore` protection
- Consider using secret management services for production

### Environment Variables
```bash
# Recommended: Use environment variables
export FIRECRAWL_API_KEY="fc-your-api-key"

# Or use .env file (ensure it's in .gitignore)
echo "FIRECRAWL_API_KEY=fc-your-api-key" >> .env
```

### Programmatic Configuration
```python
# Avoid hardcoding API keys
# BAD:
config = ScrapeConfig(api_key="fc-hardcoded-key")

# GOOD:
config = ScrapeConfig.from_env()  # Reads from environment
```

## Rate Limiting and Throttling

### Respect Rate Limits
- Firecrawl and other providers have rate limits
- Implement appropriate delays between requests
- Monitor API usage to avoid exceeding limits
- Use `ScrapeConfig.rate_limit` when available

### Best Practices
```python
import time

# Add delays between requests
for url in urls:
    result = scraper.scrape(url)
    time.sleep(1)  # Respect rate limits
```

## Robots.txt Compliance

### Default Behavior
- The module respects `robots.txt` by default (`respect_robots_txt=True`)
- This is a legal and ethical best practice
- Only disable when you have explicit permission

### Configuration
```python
# Respect robots.txt (default)
options = ScrapeOptions(respect_robots_txt=True)

# Only disable if you have permission
options = ScrapeOptions(respect_robots_txt=False)
```

## Legal and Ethical Considerations

### Terms of Service
- **Always review and comply with website Terms of Service**
- Some websites explicitly prohibit scraping
- Obtain permission when required
- Use official APIs when available

### Ethical Guidelines
- **Respect website resources**: Don't overload servers with excessive requests
- **Respect privacy**: Don't scrape personal information without consent
- **Respect copyright**: Don't redistribute scraped content without permission
- **Be transparent**: Identify your scraper with appropriate user agents

### User Agent Identification
```python
config = ScrapeConfig(
    user_agent="MyApp/1.0 (Contact: your@email.com)",
    respect_robots_txt=True,
)
```

## Input Validation

### URL Validation
- Always validate URLs before scraping
- Check for malicious URLs (e.g., file://, javascript:)
- Sanitize user-provided URLs

```python
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in ('http', 'https') and parsed.netloc
```

### Schema Validation
- Validate extraction schemas to prevent injection
- Limit schema complexity
- Sanitize prompts for LLM extraction

## Error Handling

### Information Disclosure
- Don't expose API keys in error messages
- Don't log sensitive data
- Use generic error messages for users

### Exception Handling
```python
try:
    result = scraper.scrape(url)
except ScrapeError as e:
    # Log detailed error internally
    logger.error(f"Scraping failed: {e}", exc_info=True)
    # Return generic message to user
    raise ScrapeError("Failed to scrape URL") from e
```

## Network Security

### HTTPS Only
- Prefer HTTPS URLs when possible
- Validate SSL certificates
- Be cautious with self-signed certificates

### Timeout Configuration
- Set appropriate timeouts to prevent hanging requests
- Use `ScrapeConfig.default_timeout` to limit request duration

```python
config = ScrapeConfig(
    default_timeout=30.0,  # 30 second timeout
    max_retries=3,
)
```

## Data Handling

### Sensitive Data
- Don't log scraped content that may contain sensitive information
- Encrypt stored scraped data if it contains PII
- Follow data retention policies

### Content Sanitization
- Sanitize scraped HTML before processing
- Be cautious with JavaScript execution
- Validate extracted data before use

## Dependency Security

### Package Updates
- Keep `firecrawl-py` and other dependencies updated
- Monitor for security advisories
- Use dependency scanning tools

```bash
# Check for vulnerabilities
pip-audit
# or
safety check
```

## Best Practices Summary

1. ✅ Store API keys securely (environment variables, secrets management)
2. ✅ Respect robots.txt and Terms of Service
3. ✅ Implement rate limiting and throttling
4. ✅ Validate all inputs (URLs, schemas, prompts)
5. ✅ Use appropriate timeouts
6. ✅ Don't expose sensitive data in logs or errors
7. ✅ Keep dependencies updated
8. ✅ Identify your scraper with appropriate user agents
9. ✅ Respect website resources and privacy
10. ✅ Follow legal and ethical guidelines

## Reporting Security Issues

If you discover a security vulnerability in this module, please report it responsibly:

1. **Do not** open a public issue
2. Contact the maintainers privately
3. Provide detailed information about the vulnerability
4. Allow time for the issue to be addressed before public disclosure

## Compliance

When using this module, ensure compliance with:
- **GDPR**: If scraping EU websites or handling EU user data
- **CCPA**: If scraping California websites or handling California user data
- **Website Terms of Service**: Always review and comply
- **Copyright Laws**: Respect intellectual property rights
- **Data Protection Laws**: Handle personal data appropriately


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
