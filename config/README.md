# config

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

The config directory contains configuration templates, examples, and environment setups that enable consistent deployment and operation of Codomyrmex across different environments. These configurations ensure reliable, secure, and optimized system operation.

## Configuration Types

### Environment Configurations
Templates for different deployment environments:
- **Development**: Local development setup with debugging enabled
- **Staging**: Pre-production testing environment
- **Production**: Optimized production deployment

### Resource Configurations
Resource allocation and scaling parameters:
- **CPU/Memory limits**: Container and system resource constraints
- **Storage allocation**: Database and file system configurations
- **Network settings**: Service discovery and communication

### Workflow Configurations
Orchestration and automation setups:
- **Build pipelines**: CI/CD workflow definitions
- **Deployment processes**: Release and rollback procedures
- **Monitoring setups**: Observability and alerting configurations

## Getting Started

### Using Configuration Templates

```bash
# Copy a template for customization
cp templates/development.env my-development.env

# Edit for your environment
# Add your API keys, database URLs, etc.

# Validate configuration
python scripts/config_management/validate.py my-development.env
```

### Example Configurations

Explore complete working examples:

```bash
# Basic workflow configuration
cat examples/workflow-basic.json

# Docker Compose setup
cat examples/docker-compose.yml

# Custom project template
cat examples/project-template-custom.json
```

## Directory Contents

### Core Configuration Files
- `README.md` – This documentation
- `resources.json` – Base resource configuration template

### Configuration Examples (`examples/`)
Complete working configurations for different scenarios:
- `docker-compose.yml` – Container orchestration setup
- `project-template-custom.json` – Custom project scaffolding
- `resources-custom.json` – Advanced resource allocation
- `workflow-basic.json` – Simple workflow orchestration
- `workflow-with-dependencies.json` – Complex dependency management

### Configuration Templates (`templates/`)
Reusable starting points for customization:
- `development.env` – Development environment variables
- `production.env` – Production environment variables

## Configuration Standards

### File Formats

**Environment Variables (.env)**
```bash
# Application settings
APP_NAME=codomyrmex
DEBUG=true

# Database configuration
DATABASE_URL=postgresql://localhost/codomyrmex

# API keys (never commit actual keys)
OPENAI_API_KEY=your-key-here
```

**JSON Configurations**
```json
{
  "environment": "production",
  "services": {
    "api": {
      "port": 8080,
      "replicas": 3,
      "resources": {
        "cpu": "500m",
        "memory": "1Gi"
      }
    }
  }
}
```

### Security Practices

- **Never commit secrets** - Use environment variables or secure vaults
- **Validate configurations** - Always test configurations before deployment
- **Document sensitive settings** - Clearly mark security-related configurations
- **Use secure defaults** - Configurations should be secure out-of-the-box

## Validation and Testing

### Configuration Validation

```bash
# Validate a configuration file
python scripts/config_management/validate.py config.json

# Check environment setup
python scripts/environment_setup/validate.py

# Test resource allocations
python scripts/config_management/test_resources.py
```

### Common Validation Checks

- **Schema compliance** - JSON configurations match expected structure
- **Environment compatibility** - Settings work across target platforms
- **Resource availability** - Allocated resources are available
- **Security policies** - Configurations meet security requirements

## Usage Examples

### Development Environment Setup

```bash
# 1. Copy development template
cp templates/development.env .env

# 2. Edit with your settings
# APP_DEBUG=true
# DATABASE_URL=sqlite:///dev.db

# 3. Validate and start
python scripts/config_management/validate.py .env
codomyrmex --config .env
```

### Production Deployment

```bash
# 1. Use production template
cp templates/production.env production.env

# 2. Configure production settings
# DATABASE_URL=postgresql://prod-server/codomyrmex
# REDIS_URL=redis://prod-cache:6379

# 3. Validate production config
python scripts/config_management/validate.py production.env

# 4. Deploy with configuration
docker-compose -f examples/docker-compose.yml up -d
```

### Workflow Configuration

```json
{
  "name": "data-processing-pipeline",
  "steps": [
    {
      "name": "data-ingestion",
      "module": "data_visualization",
      "config": {
        "input_format": "csv",
        "validation_rules": ["not_null", "valid_range"]
      }
    },
    {
      "name": "processing",
      "module": "pattern_matching",
      "dependencies": ["data-ingestion"]
    }
  ]
}
```

## Troubleshooting

### Common Configuration Issues

**Validation Errors**
- Check JSON syntax with a validator
- Ensure all required fields are present
- Verify environment variable references

**Environment Problems**
- Confirm environment variables are set
- Check file permissions and paths
- Validate network connectivity for external services

**Resource Issues**
- Monitor system resources during deployment
- Adjust resource limits based on workload
- Consider horizontal scaling for high load

### Debug Mode

```bash
# Enable verbose configuration logging
export CODOMYRMEX_DEBUG_CONFIG=true

# Validate with detailed output
python scripts/config_management/validate.py --verbose config.json

# Test configuration in isolation
python scripts/config_management/test_config.py --interactive
```

## Navigation

### Quick Start
- **Basic Example**: [examples/workflow-basic.json](examples/workflow-basic.json) - Simple configuration
- **Docker Setup**: [examples/docker-compose.yml](examples/docker-compose.yml) - Container deployment
- **Templates**: [templates/](templates/) - Reusable starting points

### Advanced Usage
- **Validation Tools**: [scripts/config_management/](../../scripts/config_management/) - Configuration management utilities
- **Environment Setup**: [docs/development/environment-setup.md](../../docs/development/environment-setup.md)
- **Project Orchestration**: [docs/project_orchestration/config-driven-operations.md](../../docs/project_orchestration/config-driven-operations.md)

### Related Documentation
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Contributing**: [docs/project/contributing.md](../../docs/project/contributing.md)
- **Security**: [SECURITY.md](../../../SECURITY.md)

## Contributing

When adding configurations:

1. **Follow Standards** - Adhere to established naming and structure conventions
2. **Include Examples** - Provide working examples for common use cases
3. **Add Validation** - Ensure configurations can be validated automatically
4. **Document Thoroughly** - Explain all configuration options and their effects
5. **Test Across Environments** - Validate configurations work in different setups

### Configuration Template

```json
{
  "metadata": {
    "version": "1.0",
    "description": "Configuration template for [purpose]",
    "environments": ["development", "production"]
  },
  "configuration": {
    // Actual configuration settings
  },
  "validation": {
    "required_fields": ["field1", "field2"],
    "field_types": {
      "field1": "string",
      "field2": "integer"
    }
  }
}
```
