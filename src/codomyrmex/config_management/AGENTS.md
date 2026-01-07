# Codomyrmex Agents — src/codomyrmex/config_management

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Configuration management, validation, and deployment capabilities. Provides centralized management of application configuration and secrets with multi-source loading (files, environment, secrets), configuration validation with JSON schemas, environment-specific configurations, configuration merging and overriding, hot-reload capabilities, secure secret management, configuration deployment, and configuration monitoring.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `config_deployer.py` – Configuration deployment
- `config_loader.py` – Configuration loading and management
- `config_migrator.py` – Configuration migration
- `config_monitor.py` – Configuration monitoring and auditing
- `config_validator.py` – Configuration validation
- `secret_manager.py` – Secure secret management

## Key Classes and Functions

### ConfigurationManager (`config_loader.py`)
- `ConfigurationManager(config_dir: Optional[str] = None)` – Comprehensive configuration manager
- `load_configuration(name: str, sources: Optional[list[str]] = None, schema_path: Optional[str] = None) -> Configuration` – Load and merge configuration from multiple sources
- `validate_configuration(config: Union[Dict, Configuration], schema: Optional[ConfigSchema] = None, **kwargs) -> Dict` – Validate configuration against schemas
- `get_configuration(name: str) -> Optional[Configuration]` – Get loaded configuration
- `reload_configuration(name: str) -> Configuration` – Reload configuration

### Configuration (`config_loader.py`)
- `Configuration` (dataclass) – Configuration object with validation and metadata:
  - `name: str` – Configuration name
  - `data: dict[str, Any]` – Configuration data
  - `schema: Optional[ConfigSchema]` – Validation schema
  - `metadata: dict[str, Any]` – Configuration metadata
  - `to_dict() -> dict` – Convert to dictionary

### ConfigSchema (`config_loader.py`)
- `ConfigSchema` (dataclass) – JSON schema for configuration validation
- `validate(config: dict[str, Any]) -> list[str]` – Validate configuration against schema

### ConfigurationDeployer (`config_deployer.py`)
- `ConfigurationDeployer()` – Configuration deployment management
- `deploy_configuration(config: Configuration, target: str, environment: str, **kwargs) -> ConfigDeployment` – Deploy configuration to target environments
- `ConfigDeployment` (dataclass) – Configuration deployment tracking

### ConfigurationMonitor (`config_monitor.py`)
- `ConfigurationMonitor()` – Configuration monitoring and auditing
- `monitor_config_changes(config_name: str) -> Iterator[ConfigChange]` – Track configuration changes and drift
- `audit_configuration(config_name: str) -> ConfigAudit` – Audit configuration compliance and security
- `ConfigAudit` (dataclass) – Configuration audit and compliance results

### SecretManager (`secret_manager.py`)
- `SecretManager()` – Secure secret storage and retrieval
- `encrypt_configuration(config: Configuration) -> str` – Encrypt configuration
- `manage_secrets(operation: str, secret_path: str, value: Optional[str] = None, **kwargs) -> Dict` – Secure secret management and rotation

### Module Functions (`__init__.py`)
- `load_configuration(config_paths: List[str], environment: str = "development", overrides: Optional[Dict] = None, **kwargs) -> Configuration` – Load and merge configuration
- `validate_configuration(config: Union[Dict, Configuration], schema: Optional[ConfigSchema] = None, **kwargs) -> Dict` – Validate configuration
- `deploy_configuration(config: Configuration, target: str, environment: str, **kwargs) -> ConfigDeployment` – Deploy configuration
- `monitor_config_changes(config_name: str) -> Iterator[ConfigChange]` – Monitor configuration changes

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation