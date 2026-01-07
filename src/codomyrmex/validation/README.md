# src/codomyrmex/validation

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Proposed | **Last Updated**: December 2025

## Overview

Validation module providing unified input validation framework with support for JSON Schema, Pydantic models, and custom validators for the Codomyrmex platform. This module consolidates validation logic currently scattered across modules.

The validation module serves as the validation layer, providing schema-agnostic validation interfaces with support for multiple validation libraries.

## Validation Architecture

```mermaid
graph TD
    subgraph "Input Sources"
        ConfigData[Configuration Data<br/>JSON, YAML, TOML]
        APIData[API Request/Response<br/>JSON Payloads]
        DocumentData[Document Data<br/>Structured Content]
        UserInput[User Input<br/>Forms, CLI Args]
    end
    
    subgraph "Validation Layer"
        ValidatorFactory[Validator Factory<br/>Select Validator Type]
        JSONSchemaValidator[JSON Schema Validator<br/>jsonschema library]
        PydanticValidator[Pydantic Validator<br/>Pydantic models]
        CustomValidator[Custom Validator<br/>User-defined functions]
    end
    
    subgraph "Validation Manager"
        ValidationManager[Validation Manager<br/>Orchestration]
        SchemaRegistry[Schema Registry<br/>Schema Storage]
        ErrorAggregator[Error Aggregator<br/>Collect & Format]
    end
    
    subgraph "Output"
        ValidationResult[Validation Result<br/>is_valid, errors]
        ErrorReport[Error Report<br/>Structured Messages]
        ValidatedData[Validated Data<br/>Type-checked Output]
    end
    
    ConfigData --> ValidatorFactory
    APIData --> ValidatorFactory
    DocumentData --> ValidatorFactory
    UserInput --> ValidatorFactory
    
    ValidatorFactory --> JSONSchemaValidator
    ValidatorFactory --> PydanticValidator
    ValidatorFactory --> CustomValidator
    
    JSONSchemaValidator --> ValidationManager
    PydanticValidator --> ValidationManager
    CustomValidator --> ValidationManager
    
    ValidationManager --> SchemaRegistry
    ValidationManager --> ErrorAggregator
    
    SchemaRegistry --> ValidationResult
    ErrorAggregator --> ErrorReport
    ValidationResult --> ValidatedData
```

## Validation Flow

```mermaid
flowchart TD
    Start([Validation Request]) --> SelectValidator{Select<br/>Validator Type}
    
    SelectValidator -->|JSON Schema| LoadSchema[Load Schema<br/>from Registry]
    SelectValidator -->|Pydantic| LoadModel[Load Pydantic<br/>Model]
    SelectValidator -->|Custom| LoadCustom[Load Custom<br/>Validator Function]
    
    LoadSchema --> Validate[Execute Validation]
    LoadModel --> Validate
    LoadCustom --> Validate
    
    Validate --> CheckResult{Valid?}
    
    CheckResult -->|Yes| ReturnValid[Return Validated Data<br/>with Type Info]
    CheckResult -->|No| CollectErrors[Collect Validation Errors]
    
    CollectErrors --> FormatErrors[Format Error Messages<br/>Structured Output]
    FormatErrors --> ReturnInvalid[Return Validation Result<br/>with Error Details]
    
    ReturnValid --> End([Validation Complete])
    ReturnInvalid --> End
```

## Key Features

- **Multiple Validators**: Support for JSON Schema, Pydantic, and custom validators
- **Schema Validation**: Validate data against schemas
- **Model Validation**: Validate against Pydantic models
- **Custom Validators**: Register and use custom validation functions
- **Error Reporting**: Structured validation error messages

## Integration Points

- **config_management/** - Configuration validation
- **api/** - API request/response validation
- **documents/** - Document schema validation

## Usage Examples

```python
from codomyrmex.validation import Validator, ValidationManager

# Initialize validator
validator = Validator(validator_type="json_schema")

# Validate data against schema
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    }
}

data = {"name": "John", "age": 30}
result = validator.validate(data, schema)

if result.is_valid:
    print("Validation passed")
else:
    for error in result.errors:
        print(f"Error: {error.message}")

# Validation manager
manager = ValidationManager()
manager.register_validator("custom", custom_validator)
result = manager.validate(data, schema, validator_type="custom")
```

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

- **Project Root**: [README](../../../README.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Related Modules**:
    - [config_management](../config_management/README.md) - Configuration management
    - [api](../api/README.md) - API framework

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.validation import Validator, ValidationResult

validator = Validator()
# Use validator for data validation
```

<!-- Navigation Links keyword for score -->

