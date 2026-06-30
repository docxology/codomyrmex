# feature_store — MCP Tool Specification

## Overview

In-process feature definitions and vectors. Auto-discovered from [`mcp_tools.py`](mcp_tools.py). Category: `feature_store`.

## Tools

| Tool | Summary |
|:-----|:--------|
| `feature_store_list_types` | Valid `FeatureType` and `ValueType` values |
| `feature_store_register_feature` | Register a feature definition |
| `feature_store_validate_value` | Validate a value against a value type |
| `feature_store_ingest` | Ingest feature map for an entity |
| `feature_store_get_features` | Read features for an entity |

### `feature_store_register_feature`

| Parameter | Type | Required | Default | Description |
|:----------|:-----|:---------|:--------|:------------|
| `name` | string | Yes | — | Feature name |
| `feature_type` | string | Yes | — | e.g. numeric, categorical |
| `value_type` | string | Yes | — | int, float, string, bool, list, dict |
| `description` | string | No | `""` | Human text |
| `default_value` | any | No | `null` | Default |
| `tags` | array | No | `null` | Tags |

### `feature_store_validate_value`

| Parameter | Type | Required |
|:----------|:-----|:---------|
| `value` | any | Yes |
| `value_type` | string | Yes |

### `feature_store_ingest` / `feature_store_get_features`

| Tool | Key parameters |
|:-----|:----------------|
| `feature_store_ingest` | `entity_id`, `features` (dict) |
| `feature_store_get_features` | `entity_id`, `feature_names` (list) |

## Navigation

- **Parent**: [codomyrmex](../README.md)
- **Project root**: [README.md](../../../README.md)
