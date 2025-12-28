# Codomyrmex Agents — src/codomyrmex/environment_setup

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Foundation module providing environment validation and setup utilities for the Codomyrmex platform. This module ensures that development and runtime environments are properly configured with required dependencies, API keys, and environment variables before other modules initialize.

The environment_setup module acts as a gatekeeper, preventing runtime failures due to missing dependencies or misconfigurations.

## Module Overview

### Key Capabilities
- **Dependency Validation**: Checks for required Python packages and provides installation guidance
- **Environment Variable Management**: Validates and loads environment configurations from .env files
- **API Key Verification**: Ensures required API keys are present for external services
- **Setup Guidance**: Provides clear instructions for environment configuration
- **Early Failure Detection**: Identifies configuration issues before they cause runtime problems

### Key Features
- Comprehensive dependency checking with helpful error messages
- Environment file (.env) detection and loading
- API key validation for multiple providers (OpenAI, Anthropic, Google AI)
- Graceful error handling with actionable guidance
- Integration with Python's dotenv library for environment management

## Function Signatures

### Core Functions

```python
def is_uv_available() -> bool
```

Checks if the uv package manager is available on the system by running `uv --version`.

**Returns:** `bool` - True if uv is available and working, False otherwise

**Implementation**: Uses `subprocess.run()` to execute uv command and checks for success

```python
def is_uv_environment() -> bool
```

Determines if the current Python environment is managed by uv by checking environment variables.

**Returns:** `bool` - True if running in a uv-managed environment, False otherwise

**Checks**:
- `UV_ACTIVE` environment variable set to "1"
- `VIRTUAL_ENV` contains "uv" in the path

```python
def ensure_dependencies_installed() -> None
```

Checks for required Python packages (cased/kit, python-dotenv) and provides installation guidance if missing.

**Returns:** None (prints status messages and exits if dependencies missing)

**Dependencies Checked**:
- `kit` - cased/kit library
- `python-dotenv` - Environment variable loading

**Behavior**: Exits with `sys.exit(1)` if critical dependencies missing

```python
def check_and_setup_env_vars(repo_root_path: str) -> None
```

Validates environment configuration by checking for .env file and providing guidance for API key setup.

**Parameters:**
- `repo_root_path` (str): Path to the repository root directory

**Returns:** None (prints status and setup guidance)

**Checks**: Looks for `.env` file in repository root and provides template if missing

### Additional Functions

```python
def validate_python_version(required: str = ">=3.10") -> bool
```

Validate that the current Python version meets the specified requirements.

**Parameters:**
- `required` (str): Version requirement string (e.g., ">=3.10", "==3.11.0"). Defaults to ">=3.10"

**Returns:** `bool` - True if current Python version meets requirements, False otherwise

**Dependencies**: Requires `packaging` library for version parsing

```python
def check_package_versions() -> Dict[str, str]
```

Check installed package versions using `pkg_resources.working_set`.

**Returns:** `Dict[str, str]` - Dictionary mapping package names (lowercase) to their current versions

```python
def validate_environment_completeness() -> Dict[str, bool]
```

Perform comprehensive environment validation across multiple aspects.

**Returns:** `Dict[str, bool]` - Dictionary with validation results:
- `python_version`: Whether Python version meets requirements
- `core_dependencies`: Whether kit and dotenv are installed
- `environment_type`: Whether running in virtual environment
- `package_manager`: Whether uv is available
- `config_files`: Whether all required config files exist (pyproject.toml, requirements.txt, .env)

```python
def generate_environment_report() -> str
```

Generate a detailed, formatted environment status report with visual indicators.

**Returns:** `str` - Multi-line formatted report string with:
- Python version status (✓/✗)
- Core dependencies status
- Environment type (uv/venv/system)
- Package manager availability
- Configuration file status
- Sample of installed package versions
- Overall environment health score

**Format**: Uses Unicode box-drawing characters and emoji for visual formatting

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `env_checker.py` – Main environment validation and setup utilities

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations for environment variables
- `CHANGELOG.md` – Version history and updates

### Supporting Files
- `requirements.txt` – Module dependencies
- `docs/` – Additional documentation
- `scripts/` – Environment setup scripts
- `tests/` – Comprehensive test suite

## Operating Contracts

### Universal Environment Protocols

All environment setup within the Codomyrmex platform must:

1. **Validate Early** - Environment checks should occur before other modules initialize
2. **Provide Clear Guidance** - Error messages must include actionable steps for resolution
3. **Handle Missing Dependencies** - Gracefully handle optional vs required dependencies
4. **Secure API Keys** - Never log or expose API keys in error messages or logs
5. **Support Multiple Environments** - Work across development, staging, and production setups

### Module-Specific Guidelines

#### Dependency Management
- Check for essential dependencies first, then optional ones
- Provide installation commands for missing packages
- Use try/except blocks for optional import checks
- Maintain clear separation between required and optional dependencies

#### Environment Configuration
- Use .env files for local development configuration
- Validate environment variable presence and format
- Support environment-specific configuration overrides
- Document all required and optional environment variables

## Navigation Links

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations

### Related Modules

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation

## Agent Coordination

### Integration Points

When integrating with other modules:

1. **Initialization Order** - Ensure environment setup runs before module imports
2. **Configuration Sharing** - Coordinate environment variable requirements with other modules
3. **Error Propagation** - Handle environment setup failures gracefully in dependent modules
4. **Documentation Updates** - Update environment requirements when adding new dependencies

### Quality Gates

Before environment setup changes are accepted:

1. **Validation Tested** - All validation scenarios properly tested
2. **Error Messages Clear** - Guidance messages are actionable and helpful
3. **Security Verified** - No sensitive data exposure in error handling
4. **Cross-Platform Compatible** - Works on supported operating systems
5. **Documentation Updated** - Environment requirements clearly documented

## Version History

- **v0.1.0** (December 2025) - Initial environment validation system with dependency checking and API key management
