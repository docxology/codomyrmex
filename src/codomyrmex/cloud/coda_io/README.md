# cloud/coda_io

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Coda.io API client submodule. Provides a comprehensive Python client for the Coda.io REST API v1, enabling programmatic access to Coda docs, pages, tables, rows, formulas, controls, and permissions. Includes typed data models for all API resources and a structured exception hierarchy for error handling.

## Key Exports

### Client

- **`CodaClient`** -- Main API client; initialized with `api_token`; provides methods for docs, pages, tables, rows, and permissions

### Core Resource Models

- **`Doc`** / **`DocList`** -- Coda document and paginated list
- **`Page`** / **`PageList`** -- Document page and paginated list
- **`PageReference`** / **`PageContentItem`** -- Page reference and content item
- **`Table`** / **`TableList`** -- Table and paginated list
- **`TableReference`** -- Table reference
- **`Column`** / **`ColumnList`** -- Table column and paginated list
- **`Row`** / **`RowList`** -- Table row and paginated list
- **`RowEdit`** / **`CellEdit`** -- Row and cell edit operations
- **`Formula`** / **`FormulaList`** -- Document formula and paginated list
- **`Control`** / **`ControlList`** -- Document control and paginated list

### Permission Models

- **`Permission`** / **`PermissionList`** -- Permission entry and paginated list
- **`SharingMetadata`** -- Document sharing metadata
- **`ACLSettings`** -- Access control list settings
- **`Principal`** -- Permission principal (user, group, etc.)

### Reference Models

- **`WorkspaceReference`** / **`FolderReference`** -- Workspace and folder references
- **`Icon`** / **`DocSize`** -- Document icon and size metadata

### User and Mutation Models

- **`User`** -- Coda user information
- **`MutationStatus`** -- Status of a mutation operation
- **`InsertRowsResult`** -- Result of a row insertion operation

### Exceptions

- **`CodaAPIError`** -- Base Coda API exception
- **`CodaAuthenticationError`** -- 401 authentication failure
- **`CodaForbiddenError`** -- 403 forbidden access
- **`CodaNotFoundError`** -- 404 resource not found
- **`CodaRateLimitError`** -- 429 rate limit exceeded
- **`CodaValidationError`** -- 400 validation failure
- **`CodaGoneError`** -- 410 resource gone

## Directory Contents

- `__init__.py` - Package init; re-exports client, models, and exceptions
- `client.py` - CodaClient implementation with REST API methods
- `models.py` - Typed dataclass models for all Coda API resources
- `exceptions.py` - Exception hierarchy for Coda API errors
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [cloud](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
