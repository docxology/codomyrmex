# Secret Management Configuration Example

## Overview

This example demonstrates secure handling of sensitive data, API keys, passwords, and other secrets in Codomyrmex configurations. It shows best practices for secret storage, access control, rotation, and compliance.

## Key Security Concepts

### 1. Environment Variables for Secrets

**✅ Always use environment variables:**
```bash
# Set secrets as environment variables
export OPENAI_API_KEY="sk-your-actual-key-here"
export DB_PASSWORD="your-secure-password"
export GITHUB_TOKEN="ghp_your_token_here"

# Never hardcode in files
# ❌ WRONG
secrets:
  openai_api_key: "sk-your-key-here"
```

**✅ Use configuration references:**
```yaml
secrets:
  openai_api_key: "${OPENAI_API_KEY}"
  database_password: "${DB_PASSWORD}"
  github_token: "${GITHUB_TOKEN}"
```

### 2. Secret Validation

**✅ Validate secret formats:**
```yaml
secret_validation:
  format_validation:
    api_keys:
      pattern: "^[a-zA-Z0-9_-]{20,}$"
      description: "API keys should be at least 20 characters"
    passwords:
      pattern: "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{12,}$"
      description: "Strong password requirements"
```

### 3. Access Control

**✅ Implement role-based access:**
```yaml
access_control:
  roles:
    developer:
      permissions:
        - read: ["openai_api_key", "github_token"]
        - write: []  # Developers can't write secrets
    admin:
      permissions:
        - read: ["*"]
        - write: ["*"]  # Admins can do everything
```

## Secret Types Covered

### API Keys and Tokens

```yaml
secrets:
  # AI Service Keys
  openai_api_key: "${OPENAI_API_KEY}"
  anthropic_api_key: "${ANTHROPIC_API_KEY}"

  # Version Control
  github_token: "${GITHUB_TOKEN}"

  # Communication
  slack_webhook: "${SLACK_WEBHOOK_URL}"
```

### Database Credentials

```yaml
secrets:
  database_password: "${DB_PASSWORD}"
  redis_password: "${REDIS_PASSWORD}"
  mongodb_uri: "${MONGODB_URI}"
```

### Cloud Service Credentials

```yaml
secrets:
  # AWS
  aws_access_key: "${AWS_ACCESS_KEY_ID}"
  aws_secret_key: "${AWS_SECRET_ACCESS_KEY}"

  # Azure
  azure_client_id: "${AZURE_CLIENT_ID}"
  azure_client_secret: "${AZURE_CLIENT_SECRET}"

  # GCP
  gcp_service_account_key: "${GCP_SERVICE_ACCOUNT_KEY}"
```

## Secret Storage Methods

### 1. Environment Variables (Recommended)

**Best for**: Containerized applications, CI/CD pipelines

```bash
# docker-compose.yml
services:
  app:
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DB_PASSWORD=${DB_PASSWORD}

# Kubernetes
env:
- name: OPENAI_API_KEY
  valueFrom:
    secretKeyRef:
      name: codomyrmex-secrets
      key: openai-api-key
```

### 2. Cloud Secret Managers

**AWS Secrets Manager:**
```yaml
secret_storage:
  backup:
    - type: "aws_secrets_manager"
      region: "${AWS_REGION}"
      enabled: "${USE_AWS_SECRETS:true}"
```

**Azure Key Vault:**
```yaml
secret_storage:
  backup:
    - type: "azure_key_vault"
      vault_url: "${AZURE_VAULT_URL}"
      enabled: "${USE_AZURE_VAULT:false}"
```

### 3. HashiCorp Vault

```yaml
integrations:
  vault:
    enabled: false
    address: "${VAULT_ADDR}"
    token: "${VAULT_TOKEN}"
    path: "secret/codomyrmex"
```

## Secret Rotation

### Automatic Rotation

```yaml
secret_rotation:
  enabled: true
  rotation_schedule:
    api_keys: "90_days"
    database_passwords: "60_days"
    service_account_keys: "365_days"
```

### Manual Rotation Process

1. **Generate new secret**
2. **Update applications**
3. **Test with new secret**
4. **Revoke old secret**
5. **Monitor for issues**

### Rotation Notifications

```yaml
notifications:
  enabled: true
  channels:
    - email
    - slack
  advance_notice_days: 7
```

## Encryption and Security

### Data Encryption

```yaml
encryption:
  data_encryption:
    algorithm: "AES-256-GCM"
    key_rotation: "30_days"

  secret_encryption:
    enabled: true
    algorithm: "AES-256"
    key_source: "aws_kms"
```

### Transit Encryption

```yaml
transit_encryption:
  enabled: true
  tls_version: "1.3"
  certificate_validation: true
```

## Audit and Compliance

### Audit Logging

```yaml
audit:
  audit_logging:
    enabled: true
    audit_events:
      - "secret_access"
      - "secret_rotation"
      - "secret_creation"
      - "secret_deletion"
      - "access_denied"
```

### Compliance Settings

```yaml
compliance:
  gdpr_compliant: true
  hipaa_compliant: false
  soc2_compliant: true

  retention_periods:
    audit_logs: "7_years"
    secret_versions: "2_years"
    access_logs: "2_years"
```

## Development and Testing

### Mock Secrets

**✅ Use mock secrets for development:**
```yaml
development:
  mock_secrets:
    enabled: "${USE_MOCK_SECRETS:false}"
    mock_values:
      openai_api_key: "sk-mock-key-1234567890abcdef"
      github_token: "ghp_mock_token_1234567890abcdef"
```

### Log Masking

**✅ Mask secrets in logs:**
```yaml
log_masking:
  enabled: true
  mask_patterns:
    - pattern: "(api_key|token|password|secret)[\"']?:\\s*[\"']([^\"']+)[\"']"
      replacement: "\\1\": \"***MASKED***\""
```

## Monitoring and Alerting

### Health Checks

```yaml
monitoring:
  health_checks:
    enabled: true
    checks:
      - name: "secret_expiration"
        threshold: "30_days"
        alert: true
      - name: "secret_rotation_overdue"
        threshold: "7_days_past_due"
        alert: true
```

### Alert Configuration

```yaml
alerts:
  channels:
    - email
    - slack
    - pager_duty
  escalation:
    - delay: 0
      channels: ["email"]
    - delay: 3600
      channels: ["slack"]
```

## Implementation Examples

### Loading Secrets Securely

```python
import os
from typing import Dict, Any

def load_secrets() -> Dict[str, str]:
    """Load secrets from environment variables."""
    required_secrets = [
        'OPENAI_API_KEY',
        'DB_PASSWORD',
        'GITHUB_TOKEN'
    ]

    secrets = {}
    missing_secrets = []

    for secret_name in required_secrets:
        secret_value = os.environ.get(secret_name)
        if secret_value:
            secrets[secret_name] = secret_value
        else:
            missing_secrets.append(secret_name)

    if missing_secrets:
        raise RuntimeError(f"Missing required secrets: {', '.join(missing_secrets)}")

    return secrets

def validate_secret_format(secret_name: str, secret_value: str) -> bool:
    """Validate secret format."""
    patterns = {
        'OPENAI_API_KEY': r'^sk-[a-zA-Z0-9_-]{48,}$',
        'GITHUB_TOKEN': r'^ghp_[a-zA-Z0-9_-]{36,}$',
        'DB_PASSWORD': r'^.{12,}$'
    }

    if secret_name in patterns:
        import re
        return bool(re.match(patterns[secret_name], secret_value))

    return True  # Unknown secret type, assume valid
```

### Secret Rotation Handler

```python
import boto3
from datetime import datetime, timedelta

def rotate_secret(secret_name: str, new_value: str):
    """Rotate a secret in AWS Secrets Manager."""

    client = boto3.client('secretsmanager')

    # Update the secret
    client.update_secret(
        SecretId=secret_name,
        SecretString=json.dumps({"value": new_value})
    )

    # Tag with rotation date
    client.tag_resource(
        SecretId=secret_name,
        Tags=[
            {
                'Key': 'LastRotated',
                'Value': datetime.utcnow().isoformat()
            }
        ]
    )

    logger.info(f"Rotated secret: {secret_name}")

def check_secret_expiration(secret_name: str) -> int:
    """Check days until secret expires."""

    client = boto3.client('secretsmanager')

    # Get secret tags
    response = client.describe_secret(SecretId=secret_name)

    for tag in response.get('Tags', []):
        if tag['Key'] == 'LastRotated':
            last_rotated = datetime.fromisoformat(tag['Value'])
            days_since_rotation = (datetime.utcnow() - last_rotated).days

            # Assume 90-day rotation policy
            days_until_expiration = 90 - days_since_rotation
            return max(0, days_until_expiration)

    return 90  # Default assumption
```

## Best Practices

### General Rules

1. **Never commit secrets** to version control
2. **Use environment variables** for secrets in production
3. **Rotate secrets regularly** (every 30-90 days)
4. **Implement principle of least privilege**
5. **Audit all secret access**
6. **Use strong encryption** for secrets at rest
7. **Validate secret formats** before use

### Development Practices

1. **Use mock secrets** for local development
2. **Never hardcode secrets** in source code
3. **Use different secrets** for each environment
4. **Document secret requirements** clearly
5. **Test with invalid secrets** to ensure proper error handling

### Production Practices

1. **Use secret management services** (AWS Secrets Manager, Azure Key Vault, etc.)
2. **Enable encryption** at rest and in transit
3. **Implement automated rotation** policies
4. **Monitor secret access** and usage patterns
5. **Have disaster recovery procedures** for secret loss
6. **Implement multi-person approval** for secret changes

### Access Control Best Practices

1. **Role-based access control** (RBAC)
2. **Just-in-time access** for sensitive secrets
3. **Audit all access** to secrets
4. **Regular access reviews**
5. **Automated access revocation**

## Common Mistakes to Avoid

### ❌ Hardcoded Secrets

```python
# WRONG - Never do this
API_KEY = "sk-1234567890abcdef"

config = {
    "openai_api_key": "sk-1234567890abcdef"
}
```

### ❌ Logging Secrets

```python
# WRONG - Secrets will appear in logs
logger.info(f"Using API key: {api_key}")

# RIGHT - Mask secrets
logger.info("API key loaded successfully")
```

### ❌ Weak Passwords

```python
# WRONG - Too weak
password = "password123"

# RIGHT - Strong password
password = "Tr0ub4dor&3"  # Mixed case, numbers, symbols
```

### ❌ No Rotation Policy

```python
# WRONG - Secrets never rotated
# RIGHT - Implement rotation
secret_rotation:
  enabled: true
  schedule: "60_days"
```

## Compliance Considerations

### GDPR Compliance

- **Data minimization**: Only store necessary secrets
- **Access logging**: Log all secret access
- **Right to erasure**: Ability to revoke secrets
- **Data portability**: Export secret access logs

### HIPAA Compliance

- **Encryption**: Encrypt all secrets at rest and in transit
- **Access controls**: Strict role-based access
- **Audit trails**: Comprehensive audit logging
- **Incident response**: Procedures for secret breaches

### SOC 2 Compliance

- **Security**: Technical safeguards for secrets
- **Availability**: Redundant secret storage
- **Integrity**: Secret validation and monitoring
- **Confidentiality**: Access controls and encryption

## Tools and Integration

### Secret Management Tools

- **AWS Secrets Manager**: Cloud-native secret management
- **Azure Key Vault**: Microsoft's secret management service
- **Google Secret Manager**: GCP's secret management
- **HashiCorp Vault**: Open-source secret management
- **1Password**: Team password management
- **LastPass**: Enterprise password management

### Development Tools

- **git-secrets**: Prevents committing secrets to git
- **truffleHog**: Finds secrets in code repositories
- **detect-secrets**: Automated secret detection
- **pre-commit hooks**: Pre-commit secret scanning

### Monitoring Tools

- **Splunk**: Security information and event management
- **ELK Stack**: Log aggregation and analysis
- **Datadog**: Infrastructure monitoring
- **Prometheus**: Metrics collection and alerting

---

**Status**: Security Configuration Example
**Last Updated**: December 2025
**Compliance**: GDPR, SOC 2, Security Best Practices
