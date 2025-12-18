# Configuration Templates and Examples

This directory contains configuration templates, examples, and setup guides for various Codomyrmex deployment scenarios.

## Directory Structure

```
config/
├── templates/          # Configuration templates for different environments
├── examples/           # Example configurations for reference
└── README.md           # This file
```

## Templates

### Environment Templates

-   **development.env** - Development environment configuration
-   **production.env** - Production environment configuration
-   **testing.env** - Testing environment configuration

## Examples

### Configuration Examples

-   **docker-compose.yml** - Docker Compose setup for local development
-   **project-template-custom.json** - Custom project template configuration
-   **resources-custom.json** - Custom resource allocation configuration
-   **workflow-basic.json** - Basic workflow configuration example
-   **workflow-with-dependencies.json** - Workflow with step dependencies

## Usage

1. **Copy templates** to your project root or configuration directory
2. **Customize** the configurations for your specific environment
3. **Reference examples** for best practices and implementation patterns

## Environment Variables

Key environment variables used across configurations:

-   `CODOMYRMEX_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
-   `CODOMYRMEX_LOG_FILE` - Log file path
-   `OPENAI_API_KEY` - OpenAI API key for AI features
-   `ANTHROPIC_API_KEY` - Anthropic API key for AI features
-   `GOOGLE_API_KEY` - Google API key for AI features
-   `CODOMYRMEX_DEBUG` - Enable debug mode (true/false)

## Contributing

When adding new configuration templates:

1. Follow the existing naming conventions
2. Include clear documentation and comments
3. Test configurations in the target environment
4. Update this README with new additions

## Example Configurations

Example configurations are available in `config/examples/`:

- `workflow-basic.json` - Basic workflow configuration example
- `workflow-with-dependencies.json` - Workflow with step dependencies
- `project-template-custom.json` - Custom project template example
- `resources-custom.json` - Custom resource configuration example

## Configuration Documentation

For detailed configuration documentation, see:

- [Workflow Configuration Schema](../docs/project_orchestration/workflow-configuration-schema.md) - Workflow JSON schema and validation
- [Project Template Schema](../docs/project_orchestration/project-template-schema.md) - Project template structure
- [Resource Configuration](../docs/project_orchestration/resource-configuration.md) - Resource setup and allocation
- [Config-Driven Operations](../docs/project_orchestration/config-driven-operations.md) - Complete config-driven guide
