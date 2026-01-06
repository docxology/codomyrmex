# Codomyrmex Agents — config/templates

## Signposting
- **Parent**: [Config](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This directory contains reusable configuration templates and environment scaffolding for the Codomyrmex system. Templates provide standardized starting points for different deployment scenarios and can be customized for specific use cases.

## Configuration Templates

### Development Environment (`development.env`)
**Purpose**: Local development environment configuration
**Key Components**:
- Debug logging configuration
- Local service endpoints
- Development database connections
- Relaxed security settings for development

**Key Functions**:
```bash
# Environment identification
CODOMYRMEX_ENV=development
CODOMYRMEX_DEBUG=true

# Service configuration
CODOMYRMEX_API_HOST=localhost
CODOMYRMEX_API_PORT=8080
CODOMYRMEX_WORKER_COUNT=2

# Database configuration
CODOMYRMEX_DB_HOST=localhost
CODOMYRMEX_DB_PORT=5432
CODOMYRMEX_DB_NAME=codomyrmex_dev

# AI/ML configuration
CODOMYRMEX_OPENAI_API_KEY=your_dev_key_here
CODOMYRMEX_OLLAMA_HOST=http://localhost:11434

# Logging configuration
CODOMYRMEX_LOG_LEVEL=DEBUG
CODOMYRMEX_LOG_FILE=logs/development.log
```

**Usage Function**: `load_development_config() -> dict`
- Loads environment variables for development
- Sets debug flags and local endpoints
- Returns configuration dictionary for application use

### Production Environment (`production.env`)
**Purpose**: Production deployment environment configuration
**Key Components**:
- Optimized performance settings
- Production service endpoints
- Secure database connections
- Strict security configurations
- Monitoring and alerting setup

**Key Functions**:
```bash
# Environment identification
CODOMYRMEX_ENV=production
CODOMYRMEX_DEBUG=false

# Service configuration
CODOMYRMEX_API_HOST=api.codomyrmex.com
CODOMYRMEX_API_PORT=443
CODOMYRMEX_WORKER_COUNT=10

# Database configuration
CODOMYRMEX_DB_HOST=prod-db.codomyrmex.com
CODOMYRMEX_DB_PORT=5432
CODOMYRMEX_DB_NAME=codomyrmex_prod
CODOMYRMEX_DB_SSL=true

# AI/ML configuration
CODOMYRMEX_OPENAI_API_KEY=${OPENAI_API_KEY}  # From secrets management
CODOMYRMEX_OLLAMA_HOST=http://ollama-service:11434

# Security configuration
CODOMYRMEX_SECRET_KEY=${SECRET_KEY}
CODOMYRMEX_JWT_SECRET=${JWT_SECRET}
CODOMYRMEX_CORS_ORIGINS=https://codomyrmex.com

# Monitoring configuration
CODOMYRMEX_METRICS_ENABLED=true
CODOMYRMEX_METRICS_ENDPOINT=/metrics
CODOMYRMEX_HEALTH_CHECK_INTERVAL=30

# Logging configuration
CODOMYRMEX_LOG_LEVEL=INFO
CODOMYRMEX_LOG_FILE=/var/log/codomyrmex/production.log
CODOMYRMEX_LOG_FORMAT=json
```

**Usage Function**: `load_production_config() -> dict`
- Loads environment variables for production
- Validates required production settings
- Applies security hardening
- Returns configuration dictionary for application use

## Template System

### Template Variables
Templates support variable substitution using the following patterns:
- `${VARIABLE_NAME}` - Required environment variables (will fail if missing)
- `${VARIABLE_NAME:-default}` - Optional with default value
- `{{template_var}}` - Template-specific variables replaced during rendering

### Template Rendering Functions
```python
def render_template(template_path: str, variables: dict) -> str:
    """Render a configuration template with variable substitution."""
    pass

def validate_template_config(config: dict) -> bool:
    """Validate that rendered template meets requirements."""
    pass

def apply_environment_overrides(base_config: dict, env_overrides: dict) -> dict:
    """Apply environment-specific overrides to base configuration."""
    pass
```

## Active Components
- `README.md` – Directory documentation
- `development.env` – Development environment template (function: load_development_config() -> dict)
- `production.env` – Production environment template (function: load_production_config() -> dict)


### Additional Files
- `SPEC.md` – Spec Md

## Operating Contracts

### Template Maintenance
1. **Version Compatibility** - Keep templates compatible with current Codomyrmex versions
2. **Security Updates** - Regularly update security configurations and best practices
3. **Documentation Sync** - Update templates when new configuration options are added
4. **Testing** - Test templates in different environments before updates

### Template Standards
- Use descriptive variable names with CODOMYRMEX_ prefix
- Include helpful comments for each configuration section
- Provide sensible defaults where appropriate
- Support both required and optional configuration variables
- Include validation checks for critical configuration values

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [config](../README.md)
- **Parent AGENTS**: [../AGENTS.md](../AGENTS.md)
- **Repository Root**: [../../README.md](../../README.md)