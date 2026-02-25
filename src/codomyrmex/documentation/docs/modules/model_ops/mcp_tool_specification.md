# Model Ops - MCP Tool Specification

This document outlines the specification for tools within the Model Ops module that are intended to be integrated with the Model Context Protocol (MCP).

## Current Status: No MCP Tools Defined

The Model Ops module provides ML model operations including dataset management and sanitization, fine-tuning job management, and model evaluation with metrics (accuracy, precision, recall, F1, MSE, MAE, RMSE, R2, AUC-ROC) for internal use by other Codomyrmex modules. These functions are primarily for programmatic integration within the application lifecycle and are not suited for exposure as Model Context Protocol (MCP) tools.

MCP tools are typically designed for discrete, invocable actions or queries that an external agent (like an LLM) would trigger. The internal model operations, dataset management, and training pipeline mechanisms do not fit this paradigm.

If future enhancements to this module introduce features that are appropriate for MCP (e.g., triggering a fine-tuning job via API, validating a dataset on demand, or retrieving evaluation metrics for a completed training run), this document will be updated accordingly.

For details on how to use the model_ops functionalities within your Python code, please refer to the module's `README.md` and `API_SPECIFICATION.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
