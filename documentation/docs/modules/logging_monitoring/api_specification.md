---
sidebar_label: 'API Specification'
title: 'Logging & Monitoring - API Specification'
---

# Logging & Monitoring - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the Logging & Monitoring module. The primary purpose of this API is to provide a centralized and configurable way for other modules within the Codomyrmex project to perform logging.

## Endpoints / Functions / Interfaces

### Function 1: `setup_logging()`

- **Description**: Initializes and configures the logging system for the entire Codomyrmex application. This function should be called once, typically at the application's entry point. It configures aspects like log level, log format, and log output destinations (console, file) based on environment variables or sensible defaults.
- **Module Path**: `from codomyrmex.logging_monitoring import setup_logging`
- **Parameters/Arguments**:
    - This function currently takes no direct arguments. It reads its configuration from environment variables:
        - `CODOMYRMEX_LOG_LEVEL` (str, optional): Sets the logging threshold. Examples: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL". Defaults to "INFO".
        - `CODOMYRMEX_LOG_FILE` (str, optional): Path to a file where logs should be written. If not provided or empty, logs are only sent to the console. Example: `logs/app.log`.
        - `CODOMYRMEX_LOG_FORMAT` (str, optional): A Python logging format string or the keyword "DETAILED". Defaults to `"%(asctime)s - %(name)s - %(levelname)s - %(message)s"`. "DETAILED" uses `"%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"`.
- **Returns**: None. This function configures the logging system as a side effect.
- **Idempotency**: The function is designed to be idempotent; subsequent calls after the first successful configuration will have no further effect (due to `force=True` in `basicConfig` potentially reconfiguring, this relies on the internal implementation ensuring true idempotency or harmless reconfiguration).

### Function 2: `get_logger(name: str)`

- **Description**: Retrieves a `logging.Logger` instance, configured according to the settings applied by `setup_logging()`. This is the primary way other modules should obtain a logger to emit messages.
- **Module Path**: `from codomyrmex.logging_monitoring import get_logger`
- **Parameters/Arguments**:
    - `name` (str): The name for the logger. It is highly recommended to use the `__name__` special variable of the calling module for this argument (e.g., `logger = get_logger(__name__)`). This helps in identifying the source of log messages.
- **Returns**:
    - `logging.Logger`: An instance of a Python logger, ready for use.

## Data Models

(No specific complex data models are exposed by this logging API beyond standard Python types and `logging.Logger` objects.)

## Authentication & Authorization

(Not applicable for this internal logging module.)

## Rate Limiting

(Not applicable for this internal logging module.)

## Versioning

(This module follows the general versioning strategy of the Codomyrmex project. API stability is aimed for, with changes documented in the [CHANGELOG.md](./changelog.md).) 