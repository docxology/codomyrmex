# Codomyrmex Agents — src/codomyrmex/cloud/coda_io

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides a comprehensive Python client for the Coda.io REST API v1, enabling programmatic access to Coda docs, pages, tables, rows, formulas, and controls with full support for permissions and sharing management.

## Active Components

- `client.py` - Main CodaClient API client
- `models.py` - Data models for Coda resources
- `exceptions.py` - Custom exception classes
- `__init__.py` - Module exports
- `SPEC.md` - Module specification
- `README.md` - Module documentation

## Key Classes and Functions

### client.py
- **`CodaClient`** - Main API client
  - `__init__(api_token)` - Initialize with Coda API token
  - `list_docs()` - Lists user's Coda documents
  - `get_doc(doc_id)` - Gets document details
  - `list_pages(doc_id)` - Lists pages in a doc
  - `get_table(doc_id, table_id)` - Gets table metadata
  - `list_rows(doc_id, table_id)` - Lists table rows
  - `insert_rows(doc_id, table_id, rows)` - Inserts new rows
  - `update_row(doc_id, table_id, row_id, values)` - Updates row
  - `delete_row(doc_id, table_id, row_id)` - Deletes row

### models.py
- **`Doc`**, **`DocList`** - Document models
- **`Page`**, **`PageList`**, **`PageReference`**, **`PageContentItem`** - Page models
- **`Table`**, **`TableList`**, **`TableReference`** - Table models
- **`Column`**, **`ColumnList`** - Column models
- **`Row`**, **`RowList`**, **`RowEdit`**, **`CellEdit`** - Row models
- **`Formula`**, **`FormulaList`** - Formula models
- **`Control`**, **`ControlList`** - Control models
- **`Permission`**, **`PermissionList`**, **`SharingMetadata`**, **`ACLSettings`**, **`Principal`** - Permission models
- **`WorkspaceReference`**, **`FolderReference`**, **`Icon`**, **`DocSize`** - Reference models
- **`User`** - User model
- **`MutationStatus`**, **`InsertRowsResult`** - Mutation result models

### exceptions.py
- **`CodaAPIError`** - Base exception for API errors
- **`CodaAuthenticationError`** - 401 authentication failures
- **`CodaForbiddenError`** - 403 permission denied
- **`CodaNotFoundError`** - 404 resource not found
- **`CodaRateLimitError`** - 429 rate limit exceeded
- **`CodaValidationError`** - 400 validation errors
- **`CodaGoneError`** - 410 resource deleted

## Operating Contracts

- API token required for all operations
- Rate limiting handled with automatic retry
- Pagination handled transparently for list operations
- All responses validated against model schemas
- Mutations return status for async operations

## Signposting

- **Dependencies**: Requires `requests` for HTTP, `pydantic` for models
- **Parent Directory**: [cloud](../README.md) - Parent module documentation
- **Related Modules**:
  - `google/` - Google Cloud integrations
  - `aws/` - AWS integrations
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
