# CEREBRUM - MCP Tool Specification

This document outlines the specification for tools within the CEREBRUM module that are intended to be integrated with the Model Context Protocol (MCP). These tools provide case-based reasoning and Bayesian inference capabilities for cognitive modeling.

## General Considerations

- **Dependencies**: All tools require the `logging_monitoring` module. Ensure `setup_logging()` is called.
- **Initialization**: The CEREBRUM engine should be initialized before using tools. Tools may create engines internally if needed.
- **Error Handling**: Errors are logged using `logging_monitoring`. Tools return an `{'error': 'description'}` object on failure.
- **Security**: Case data and model parameters may contain sensitive information. Validate inputs and sanitize outputs.

---

## Tool: `create_cerebrum_model`

### 1. Tool Purpose and Description

Creates a new cognitive model in the CEREBRUM engine for case-based reasoning and Bayesian inference.

### 2. Invocation Name

`create_cerebrum_model`

### 3. Input Schema (Parameters)

| Parameter Name | Type     | Required | Description                                    | Example Value                    |
| :------------- | :------- | :------- | :--------------------------------------------- | :------------------------------- |
| `name`         | `string` | Yes      | Unique name for the model                      | `"code_quality_model"`           |
| `model_type`   | `string` | Yes      | Type of model (e.g., "case_based", "bayesian") | `"case_based"`                   |
| `config`        | `object` | No       | Model configuration parameters                 | `{"similarity_threshold": 0.7}` |

### 4. Output Schema (Return Value)

| Field Name | Type     | Description                          | Example Value                    |
| :--------- | :------- | :----------------------------------- | :------------------------------- |
| `status`    | `string` | Creation status: "success", "failure" | `"success"`                      |
| `model`     | `object` | Created model information            | `{"name": "code_quality_model"}` |
| `error`     | `string` | Error message if status is "failure" | `"Model already exists"`         |

### 5. Error Handling

- Model name conflicts result in "failure" status
- Invalid model types result in "failure" status
- Configuration validation errors are returned in error message

### 6. Idempotency

- **Idempotent**: No
- **Explanation**: Creating a model with the same name will fail if it already exists

### 7. Usage Examples

```json
{
  "tool_name": "create_cerebrum_model",
  "arguments": {
    "name": "code_pattern_model",
    "model_type": "case_based",
    "config": {
      "similarity_threshold": 0.8
    }
  }
}
```

### 8. Security Considerations

- Model names should be validated to prevent injection attacks
- Configuration parameters should be sanitized

---

## Tool: `add_case`

### 1. Tool Purpose and Description

Adds a case to the case base for case-based reasoning. A case consists of features (problem description), context, and optional outcome.

### 2. Invocation Name

`add_case`

### 3. Input Schema (Parameters)

| Parameter Name | Type     | Required | Description                                    | Example Value                              |
| :------------- | :------- | :------- | :--------------------------------------------- | :----------------------------------------- |
| `case_id`      | `string` | Yes      | Unique identifier for the case                 | `"case_001"`                                |
| `features`     | `object` | Yes      | Feature dictionary describing the case         | `{"complexity": 5, "language": "python"}`  |
| `context`       | `object` | No       | Additional context information                 | `{"project": "codomyrmex", "version": "1.0"}` |
| `outcome`       | `any`    | No       | Outcome or solution for this case             | `"success"`                                 |
| `metadata`      | `object` | No       | Additional metadata                           | `{"source": "manual", "confidence": 0.9}`  |

### 4. Output Schema (Return Value)

| Field Name | Type     | Description                          | Example Value           |
| :--------- | :------- | :----------------------------------- | :---------------------- |
| `status`    | `string` | Operation status: "success", "failure" | `"success"`             |
| `case_id`   | `string` | Identifier of the added case         | `"case_001"`            |
| `error`     | `string` | Error message if status is "failure" | `"Case ID already exists"` |

### 5. Error Handling

- Duplicate case IDs result in "failure" status
- Invalid features (empty or malformed) result in "failure" status
- Missing required fields result in "failure" status

### 6. Idempotency

- **Idempotent**: No
- **Explanation**: Adding the same case ID will update the existing case

### 7. Usage Examples

```json
{
  "tool_name": "add_case",
  "arguments": {
    "case_id": "code_review_001",
    "features": {
      "lines_of_code": 50,
      "complexity": 3,
      "language": "python"
    },
    "outcome": "approved",
    "metadata": {
      "reviewer": "ai_agent",
      "timestamp": "2025-01-05"
    }
  }
}
```

### 8. Security Considerations

- Case IDs should be validated to prevent injection
- Feature values should be sanitized
- Sensitive information in context/metadata should be handled carefully

---

## Tool: `reason_with_cases`

### 1. Tool Purpose and Description

Performs case-based reasoning by retrieving similar cases and generating predictions based on their outcomes.

### 2. Invocation Name

`reason_with_cases`

### 3. Input Schema (Parameters)

| Parameter Name        | Type     | Required | Description                                    | Example Value                            |
| :-------------------- | :------- | :------- | :--------------------------------------------- | :--------------------------------------- |
| `query_features`      | `object` | Yes      | Feature dictionary for the query case          | `{"complexity": 4, "language": "python"}` |
| `k`                   | `number` | No       | Number of similar cases to retrieve (default: 10) | `5`                                      |
| `threshold`           | `number` | No       | Minimum similarity threshold (default: 0.0)    | `0.7`                                    |
| `weighting_strategy`  | `string` | No       | Case weighting strategy (default: "distance")  | `"hybrid"`                                |

### 4. Output Schema (Return Value)

| Field Name       | Type     | Description                                    | Example Value                              |
| :--------------- | :------- | :--------------------------------------------- | :----------------------------------------- |
| `status`          | `string`  | Reasoning status: "success", "failure"          | `"success"`                                |
| `prediction`      | `any`     | Predicted outcome                              | `"approved"`                               |
| `confidence`      | `number`  | Confidence score in [0, 1]                     | `0.85`                                     |
| `retrieved_cases`  | `array`   | List of retrieved similar cases                | `[{"case_id": "case_001", "similarity": 0.9}]` |
| `evidence`        | `object`  | Additional evidence and metadata               | `{"num_cases": 5, "avg_similarity": 0.82}` |
| `error`           | `string`  | Error message if status is "failure"           | `"No similar cases found"`                 |

### 5. Error Handling

- Empty case base results in "failure" status
- Invalid query features result in "failure" status
- No similar cases above threshold may return low confidence prediction

### 6. Idempotency

- **Idempotent**: Yes (for same query features)
- **Explanation**: Same query features should return similar results, though case base may change

### 7. Usage Examples

```json
{
  "tool_name": "reason_with_cases",
  "arguments": {
    "query_features": {
      "complexity": 5,
      "language": "python",
      "test_coverage": 0.8
    },
    "k": 10,
    "threshold": 0.7
  }
}
```

### 8. Security Considerations

- Query features should be validated
- Retrieved cases may contain sensitive information - handle appropriately

---

## Tool: `bayesian_inference`

### 1. Tool Purpose and Description

Performs Bayesian inference on a Bayesian network given evidence to compute posterior distributions.

### 2. Invocation Name

`bayesian_inference`

### 3. Input Schema (Parameters)

| Parameter Name | Type     | Required | Description                                    | Example Value                              |
| :------------- | :------- | :------- | :--------------------------------------------- | :----------------------------------------- |
| `network_name` | `string` | Yes      | Name of the Bayesian network to use            | `"code_quality_network"`                   |
| `query`        | `object` | Yes      | Variables to query (variable -> null or value)  | `{"quality": null, "maintainability": null}` |
| `evidence`     | `object` | No       | Observed evidence (variable -> value)           | `{"complexity": "high", "tests": true}`   |
| `method`       | `string` | No       | Inference method (default: "variable_elimination") | `"mcmc"`                                  |

### 4. Output Schema (Return Value)

| Field Name | Type     | Description                                    | Example Value                              |
| :--------- | :------- | :--------------------------------------------- | :----------------------------------------- |
| `status`    | `string`  | Inference status: "success", "failure"          | `"success"`                                |
| `results`   | `object`  | Posterior distributions for query variables     | `{"quality": {"values": ["high", "low"], "probabilities": [0.7, 0.3]}}` |
| `error`     | `string`  | Error message if status is "failure"           | `"Network not found"`                      |

### 5. Error Handling

- Network not found results in "failure" status
- Invalid query variables result in "failure" status
- Inference method failures are logged and returned in error message

### 6. Idempotency

- **Idempotent**: Yes (for same query and evidence)
- **Explanation**: Same query and evidence should return same posterior distributions

### 7. Usage Examples

```json
{
  "tool_name": "bayesian_inference",
  "arguments": {
    "network_name": "code_quality_network",
    "query": {
      "quality": null
    },
    "evidence": {
      "complexity": "high",
      "test_coverage": 0.8
    }
  }
}
```

### 8. Security Considerations

- Network names should be validated
- Evidence values should be sanitized
- Large networks may have performance implications

---

## Tool: `visualize_model`

### 1. Tool Purpose and Description

Visualizes a CEREBRUM model structure (Bayesian network, case similarity, etc.) and returns visualization data or file path.

### 2. Invocation Name

`visualize_model`

### 3. Input Schema (Parameters)

| Parameter Name | Type     | Required | Description                                    | Example Value                    |
| :------------- | :------- | :------- | :--------------------------------------------- | :------------------------------- |
| `model_type`   | `string` | Yes      | Type of visualization ("network", "cases", "inference") | `"network"`                      |
| `model_name`   | `string` | Yes      | Name of the model to visualize                 | `"code_quality_network"`         |
| `output_path`  | `string` | No       | Path to save visualization (optional)          | `"/tmp/network_plot.png"`        |
| `format`       | `string` | No       | Output format ("png", "svg", "pdf")            | `"png"`                           |

### 4. Output Schema (Return Value)

| Field Name    | Type     | Description                                    | Example Value                    |
| :------------ | :------- | :--------------------------------------------- | :------------------------------- |
| `status`      | `string`  | Visualization status: "success", "failure"      | `"success"`                       |
| `output_path` | `string`  | Path to saved visualization file               | `"/tmp/network_plot.png"`        |
| `metadata`    | `object`  | Visualization metadata (dimensions, format)    | `{"width": 1200, "height": 800}` |
| `error`       | `string`  | Error message if status is "failure"           | `"Model not found"`              |

### 5. Error Handling

- Model not found results in "failure" status
- Invalid visualization type results in "failure" status
- File system errors are returned in error message

### 6. Idempotency

- **Idempotent**: Yes (for same model and parameters)
- **Explanation**: Same model should produce same visualization

### 7. Usage Examples

```json
{
  "tool_name": "visualize_model",
  "arguments": {
    "model_type": "network",
    "model_name": "code_quality_network",
    "output_path": "/tmp/network.png",
    "format": "png"
  }
}
```

### 8. Security Considerations

- Output paths should be validated to prevent path traversal
- File permissions should be set appropriately
- Large visualizations may consume significant resources

---

## Tool: `transform_model`

### 1. Tool Purpose and Description

Transforms a model through adaptation or learning based on new cases or feedback.

### 2. Invocation Name

`transform_model`

### 3. Input Schema (Parameters)

| Parameter Name      | Type     | Required | Description                                    | Example Value                              |
| :------------------ | :------- | :------- | :--------------------------------------------- | :----------------------------------------- |
| `model_name`        | `string` | Yes      | Name of the model to transform                 | `"code_quality_model"`                     |
| `transformation`    | `string` | Yes      | Type of transformation ("adapt_to_case", "learn_from_feedback") | `"adapt_to_case"`                        |
| `case_id`           | `string` | No       | Case ID for case-based adaptation              | `"case_001"`                               |
| `feedback`          | `object` | No       | Feedback dictionary for learning               | `{"outcome": "success", "error": 0.1}`    |
| `transformer_name`  | `string` | No       | Specific transformer to use (optional)         | `"adaptation"`                              |

### 4. Output Schema (Return Value)

| Field Name     | Type     | Description                                    | Example Value                    |
| :------------- | :------- | :--------------------------------------------- | :------------------------------- |
| `status`       | `string`  | Transformation status: "success", "failure"     | `"success"`                       |
| `model`         | `object`  | Transformed model information                   | `{"name": "code_quality_model_adapted"}` |
| `metadata`     | `object`  | Transformation metadata                         | `{"adaptation_rate": 0.1}`       |
| `error`         | `string`  | Error message if status is "failure"           | `"Model not found"`              |

### 5. Error Handling

- Model not found results in "failure" status
- Invalid transformation type results in "failure" status
- Missing required parameters result in "failure" status

### 6. Idempotency

- **Idempotent**: No
- **Explanation**: Transformations modify models, so repeated calls will have cumulative effects

### 7. Usage Examples

```json
{
  "tool_name": "transform_model",
  "arguments": {
    "model_name": "code_quality_model",
    "transformation": "adapt_to_case",
    "case_id": "case_001"
  }
}
```

### 8. Security Considerations

- Model names should be validated
- Transformation parameters should be sanitized
- Feedback data should be validated before applying



## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

