# Security Policy for Metrics Module

This document outlines security procedures, threat models, and policies for the Metrics module.

## Security Overview

The Metrics module provides application metrics collection, aggregation, and export capabilities with support for Prometheus, StatsD, and other backends. Metrics systems can inadvertently expose sensitive information and become targets for denial of service attacks.

### Security Principles

- **Data Minimization**: Collect only necessary metrics without sensitive data
- **Access Control**: Protect metrics endpoints from unauthorized access
- **Availability**: Ensure metrics collection does not impact application availability
- **Information Protection**: Prevent metrics from revealing sensitive business or security information

## Threat Model

### Assets Protected

- Application performance data
- System resource metrics
- Business metrics and KPIs
- Infrastructure topology information
- Application internals and behavior patterns

### Threat Actors

1. **External Attackers**: Attempting to gather intelligence or disrupt metrics collection
2. **Competitors**: Seeking business intelligence through metric data
3. **Malicious Insiders**: Injecting false metrics or exfiltrating data
4. **Automated Systems**: Flooding metrics endpoints for denial of service

### Attack Vectors

#### Metric Injection

**Threat Level**: Medium

**Description**: Attackers inject malicious or misleading metrics into the system.

**Attack Scenarios**:
- Injecting metrics with malicious label values (cardinality attacks)
- Manipulating metric values to hide attacks or trigger false alerts
- Using metric names/labels for log injection in downstream systems
- Injecting metrics to exhaust storage or processing capacity

**Mitigations**:
- Validate and sanitize metric names and labels
- Use allowlists for metric names and label keys
- Implement metric cardinality limits
- Authenticate metric submission sources

```python
import re
from typing import Dict

class MetricValidator:
    # Prometheus-compatible naming
    NAME_PATTERN = re.compile(r'^[a-zA-Z_:][a-zA-Z0-9_:]*$')
    LABEL_NAME_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    MAX_NAME_LENGTH = 128
    MAX_LABEL_VALUE_LENGTH = 256
    MAX_LABELS_PER_METRIC = 10

    def validate_metric_name(self, name: str) -> bool:
        """Validate metric name format and length."""
        if len(name) > self.MAX_NAME_LENGTH:
            raise ValidationError(f"Metric name exceeds {self.MAX_NAME_LENGTH} chars")
        if not self.NAME_PATTERN.match(name):
            raise ValidationError("Invalid metric name format")
        return True

    def validate_labels(self, labels: Dict[str, str]) -> bool:
        """Validate label names and values."""
        if len(labels) > self.MAX_LABELS_PER_METRIC:
            raise ValidationError(f"Too many labels (max {self.MAX_LABELS_PER_METRIC})")

        for key, value in labels.items():
            if not self.LABEL_NAME_PATTERN.match(key):
                raise ValidationError(f"Invalid label name: {key}")
            if len(value) > self.MAX_LABEL_VALUE_LENGTH:
                raise ValidationError(f"Label value too long: {key}")
            # Sanitize label values
            if '\n' in value or '\\' in value:
                raise ValidationError(f"Invalid characters in label value: {key}")

        return True
```

#### Data Exposure

**Threat Level**: High

**Description**: Sensitive information is leaked through metric names, labels, or values.

**Attack Scenarios**:
- User IDs or session tokens in metric labels revealing user activity
- Internal API endpoints exposed through request metrics
- Error metrics revealing system vulnerabilities
- Timing metrics enabling side-channel attacks
- Business metrics exposing competitive intelligence

**Mitigations**:
- Never include PII in metrics
- Use aggregated/bucketed values instead of exact numbers
- Restrict access to metrics endpoints
- Audit metric configurations for sensitive data

```python
class SecureMetrics:
    # Labels that should never contain user-specific data
    FORBIDDEN_LABEL_PATTERNS = [
        r'user_id', r'session', r'token', r'email',
        r'password', r'api_key', r'secret'
    ]

    def __init__(self):
        self.validator = MetricValidator()
        self.label_sanitizer = LabelSanitizer()

    def record(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record metric with security validation."""
        self.validator.validate_metric_name(name)

        if labels:
            # Check for forbidden labels
            self._check_forbidden_labels(labels)
            # Sanitize label values
            labels = self.label_sanitizer.sanitize(labels)
            self.validator.validate_labels(labels)

        # Record metric
        self._do_record(name, value, labels or {})

    def _check_forbidden_labels(self, labels: Dict[str, str]):
        """Check for potentially sensitive label names."""
        for label_name in labels.keys():
            for pattern in self.FORBIDDEN_LABEL_PATTERNS:
                if re.search(pattern, label_name, re.IGNORECASE):
                    raise SecurityError(
                        f"Potentially sensitive label name: {label_name}"
                    )
```

#### Denial of Service via Metric Flooding

**Threat Level**: High

**Description**: Attackers overwhelm the metrics system with excessive data, causing resource exhaustion.

**Attack Scenarios**:
- High-cardinality label explosion (unique labels per request)
- Rapid metric endpoint scraping causing CPU exhaustion
- Flooding with unique metric names exhausting memory
- Targeting metric aggregation with expensive operations

**Mitigations**:
- Implement cardinality limits per metric
- Rate limit metrics endpoint access
- Set maximum metric count limits
- Use sampling for high-volume metrics

```python
from collections import defaultdict
import time

class CardinalityLimiter:
    """Limit unique label combinations per metric."""

    def __init__(self, max_cardinality: int = 1000):
        self.max_cardinality = max_cardinality
        self.cardinality = defaultdict(set)

    def check(self, metric_name: str, labels: Dict[str, str]) -> bool:
        """Check if new label combination is allowed."""
        label_key = tuple(sorted(labels.items()))

        current = self.cardinality[metric_name]
        if label_key in current:
            return True

        if len(current) >= self.max_cardinality:
            raise CardinalityExceeded(
                f"Metric {metric_name} has reached cardinality limit "
                f"({self.max_cardinality})"
            )

        current.add(label_key)
        return True

class RateLimitedExporter:
    """Rate-limited metrics endpoint."""

    def __init__(self, scrapes_per_minute: int = 60):
        self.rate_limit = scrapes_per_minute
        self.scrape_times = defaultdict(list)

    def allow_scrape(self, client_ip: str) -> bool:
        """Check if scrape is allowed for client."""
        now = time.time()
        minute_ago = now - 60

        # Clean old entries
        self.scrape_times[client_ip] = [
            t for t in self.scrape_times[client_ip] if t > minute_ago
        ]

        if len(self.scrape_times[client_ip]) >= self.rate_limit:
            return False

        self.scrape_times[client_ip].append(now)
        return True
```

## Security Controls

### Endpoint Security

```python
from functools import wraps
from flask import request, Response

class MetricsEndpointSecurity:
    """Security controls for metrics endpoints."""

    def __init__(self, config):
        self.allowed_ips = config.get('metrics_allowed_ips', ['127.0.0.1'])
        self.auth_token = config.get('metrics_auth_token')
        self.rate_limiter = RateLimitedExporter()

    def require_auth(self, f):
        """Decorator to require authentication for metrics endpoint."""
        @wraps(f)
        def decorated(*args, **kwargs):
            # Check IP allowlist
            if request.remote_addr not in self.allowed_ips:
                return Response("Forbidden", status=403)

            # Check auth token if configured
            if self.auth_token:
                provided_token = request.headers.get('Authorization', '')
                if not self._verify_token(provided_token):
                    return Response("Unauthorized", status=401)

            # Check rate limit
            if not self.rate_limiter.allow_scrape(request.remote_addr):
                return Response("Rate limited", status=429)

            return f(*args, **kwargs)
        return decorated

    def _verify_token(self, provided: str) -> bool:
        """Verify authentication token."""
        expected = f"Bearer {self.auth_token}"
        return secrets.compare_digest(provided, expected)
```

### Label Sanitization

```python
class LabelSanitizer:
    """Sanitize metric labels to prevent injection."""

    # Characters allowed in label values
    ALLOWED_CHARS = set(
        'abcdefghijklmnopqrstuvwxyz'
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        '0123456789'
        '-_./:'
    )

    def sanitize(self, labels: Dict[str, str]) -> Dict[str, str]:
        """Sanitize all label values."""
        return {k: self._sanitize_value(v) for k, v in labels.items()}

    def _sanitize_value(self, value: str) -> str:
        """Sanitize individual label value."""
        # Replace disallowed characters
        sanitized = ''.join(
            c if c in self.ALLOWED_CHARS else '_'
            for c in value
        )
        # Truncate to max length
        return sanitized[:256]
```

### Secure Configuration

```python
# Example secure metrics configuration
from codomyrmex.metrics import MetricsConfig

secure_config = MetricsConfig(
    # Bind to internal interface only
    host="127.0.0.1",
    port=9090,

    # Enable authentication
    auth_enabled=True,
    auth_token_env="METRICS_AUTH_TOKEN",

    # IP allowlist
    allowed_ips=["10.0.0.0/8", "172.16.0.0/12"],

    # Rate limiting
    scrapes_per_minute=60,

    # Cardinality limits
    max_metrics=10000,
    max_cardinality_per_metric=500,
    max_label_name_length=128,
    max_label_value_length=256,

    # TLS (recommended for non-localhost)
    tls_enabled=True,
    tls_cert_path="/path/to/cert.pem",
    tls_key_path="/path/to/key.pem"
)
```

## Secure Usage Guidelines

### Do's

1. **Use Low-Cardinality Labels**
   ```python
   # GOOD: Fixed set of values
   metrics.counter(
       "http_requests_total",
       labels={"method": "GET", "status": "200", "endpoint": "/api/users"}
   )
   ```

2. **Protect Metrics Endpoints**
   ```python
   # Bind to internal interface
   exporter = PrometheusExporter(host="127.0.0.1", port=9090)

   # Or use authentication
   exporter = PrometheusExporter(
       host="0.0.0.0",
       port=9090,
       auth_token=os.environ["METRICS_TOKEN"]
   )
   ```

3. **Implement Cardinality Limits**
   ```python
   metrics = Metrics(
       max_cardinality=1000,
       on_cardinality_exceeded="drop"  # or "aggregate"
   )
   ```

4. **Use Histograms for Sensitive Values**
   ```python
   # Instead of exact values, use buckets
   metrics.histogram(
       "request_duration_seconds",
       buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
   ).observe(duration)
   ```

5. **Audit Metric Configurations**
   ```python
   def audit_metrics():
       """Audit all registered metrics for security issues."""
       for metric in metrics.get_all():
           check_for_pii(metric.labels)
           check_cardinality(metric)
           log_metric_registration(metric)
   ```

### Don'ts

1. **Never Include PII in Labels**
   ```python
   # BAD: User ID in label
   metrics.counter("user_actions", labels={"user_id": user.id})

   # GOOD: Use aggregated metrics
   metrics.counter("user_actions", labels={"action_type": "login"})
   ```

2. **Avoid Dynamic Label Values**
   ```python
   # BAD: User-generated content in labels
   metrics.counter("search_queries", labels={"query": user_query})

   # GOOD: Use query categories or hashes
   metrics.counter("search_queries", labels={"category": categorize(user_query)})
   ```

3. **Don't Expose Endpoints Publicly**
   ```python
   # BAD: Publicly accessible metrics
   exporter = PrometheusExporter(host="0.0.0.0", port=9090)

   # GOOD: Internal only with auth
   exporter = PrometheusExporter(
       host="127.0.0.1",
       port=9090
   )
   ```

4. **Avoid Exact Sensitive Values**
   ```python
   # BAD: Exact transaction amounts
   metrics.gauge("transaction_amount", value=transaction.amount)

   # GOOD: Bucketed amounts
   metrics.histogram("transaction_amount_bucket").observe(
       get_bucket(transaction.amount)
   )
   ```

5. **Don't Disable Rate Limiting in Production**
   ```python
   # BAD: No rate limiting
   exporter = PrometheusExporter(rate_limit=None)

   # GOOD: Appropriate rate limits
   exporter = PrometheusExporter(rate_limit=60)  # 60 scrapes/minute
   ```

## Known Vulnerabilities

### CVE Registry

No known CVEs at this time. This section will be updated as vulnerabilities are discovered and patched.

### Security Advisories

| Date | Severity | Description | Resolution |
|------|----------|-------------|------------|
| - | - | No current advisories | - |

### Deprecated Features

- **Unauthenticated Endpoints**: Always use authentication for production deployments
- **Unlimited Cardinality**: Set explicit cardinality limits to prevent DoS
- **Public Metric Binding**: Bind to localhost or use network policies

## Security Testing

### Automated Security Tests

```python
import pytest
from codomyrmex.metrics import Metrics, PrometheusExporter

class TestMetricsSecurity:

    def test_label_injection_prevention(self):
        """Verify malicious labels are sanitized."""
        metrics = Metrics(sanitize_labels=True)

        malicious_labels = {
            "status": "200\ninjected_metric 1",  # Newline injection
            "user": "admin\\nroot_metric 1"      # Escape sequence
        }

        counter = metrics.counter("test_counter", labels=malicious_labels)
        # Verify sanitization
        for value in counter.labels.values():
            assert '\n' not in value
            assert '\\n' not in value

    def test_cardinality_limits(self):
        """Verify cardinality limits are enforced."""
        metrics = Metrics(max_cardinality=10)

        counter = metrics.counter("high_cardinality")
        for i in range(20):
            if i < 10:
                counter.inc(labels={"unique_id": str(i)})
            else:
                with pytest.raises(CardinalityExceeded):
                    counter.inc(labels={"unique_id": str(i)})

    def test_rate_limiting(self):
        """Verify endpoint rate limiting."""
        exporter = PrometheusExporter(rate_limit=5)

        for i in range(10):
            if i < 5:
                assert exporter.can_scrape("127.0.0.1")
            else:
                assert not exporter.can_scrape("127.0.0.1")

    def test_authentication_required(self):
        """Verify authentication enforcement."""
        exporter = PrometheusExporter(auth_token="secret")
        client = exporter.test_client()

        # Without auth
        response = client.get("/metrics")
        assert response.status_code == 401

        # With wrong auth
        response = client.get(
            "/metrics",
            headers={"Authorization": "Bearer wrong"}
        )
        assert response.status_code == 401

        # With correct auth
        response = client.get(
            "/metrics",
            headers={"Authorization": "Bearer secret"}
        )
        assert response.status_code == 200

    def test_no_pii_in_default_labels(self):
        """Verify no PII in default metric labels."""
        metrics = Metrics()

        # Check common metric labels
        for metric in metrics.get_registered():
            for label_name in metric.label_names:
                assert 'user_id' not in label_name.lower()
                assert 'email' not in label_name.lower()
                assert 'session' not in label_name.lower()
```

### Penetration Testing Checklist

- [ ] Test metric endpoint authentication
- [ ] Test rate limiting effectiveness
- [ ] Verify cardinality limits prevent DoS
- [ ] Test label injection attacks
- [ ] Verify no PII in metric data
- [ ] Test IP allowlist enforcement
- [ ] Verify TLS configuration (if applicable)
- [ ] Test metric scraping performance under load

### Security Scanning

```bash
# Static analysis
bandit -r src/codomyrmex/metrics/

# Dependency vulnerabilities
safety check

# Check for hardcoded secrets
detect-secrets scan src/codomyrmex/metrics/
```

## Incident Response

### Reporting a Vulnerability

If you discover a security vulnerability within this module, please report it to us as soon as possible.
We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email security@codomyrmex.dev with the subject line: "SECURITY Vulnerability Report: Metrics Module - [Brief Description]".

Please include the following information in your report:

- A description of the vulnerability and its potential impact.
- Steps to reproduce the vulnerability, including any specific configurations or conditions required.
- Any proof-of-concept code or examples.
- The version(s) of the module affected.
- Your name and contact information (optional).

We aim to acknowledge receipt of your vulnerability report within 2-3 business days and will work with you to understand and remediate the issue.

### Response Procedures

#### Metric Injection Incident

1. **Immediate**: Disable metric ingestion from untrusted sources
2. **Short-term**: Audit injected metrics and remove malicious data
3. **Investigation**: Identify injection vector and affected metrics
4. **Remediation**: Implement stricter validation, redeploy
5. **Post-incident**: Review alerting rules that may have been affected

#### Data Exposure Incident

1. **Immediate**: Restrict access to metrics endpoints
2. **Short-term**: Audit exposed metric data for sensitive information
3. **Investigation**: Determine scope and duration of exposure
4. **Notification**: Alert affected parties if PII was exposed
5. **Remediation**: Remove sensitive labels, implement data minimization

#### Denial of Service Incident

1. **Immediate**: Enable strict rate limiting, block attack sources
2. **Short-term**: Increase cardinality limits temporarily if needed
3. **Investigation**: Identify attack pattern and source
4. **Remediation**: Tune rate limits and cardinality controls
5. **Post-incident**: Review capacity planning for metrics infrastructure

### Security Updates

Security patches and updates for this module will be documented in the module changelog and released as part of regular version updates. Critical vulnerabilities may warrant out-of-band releases.

## Scope

This security policy applies only to the `Metrics` module within the Codomyrmex project. For project-wide security concerns, please refer to the main project's security policy or contact the core project maintainers.

Thank you for helping keep Codomyrmex and the Metrics module secure.
