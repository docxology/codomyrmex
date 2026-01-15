# Cloud Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The Cloud module provides integrations with external cloud service APIs. Currently, it includes a comprehensive Coda.io REST API v1 client for document and database operations.

## Key Features

- **Coda.io Integration**: Full REST API v1 client for Coda documents
- **Document Management**: List, retrieve, and manage Coda docs
- **Table Operations**: Read and write to Coda tables (database-like functionality)
- **Page Navigation**: Access and traverse document page hierarchies
- **Permission Management**: Control sharing and access settings
- **Formula Support**: Work with Coda formulas and controls
- **Comprehensive Models**: Fully typed Pydantic models for all API entities
- **Error Handling**: Granular exception types for API error handling

## Quick Start

```python
from codomyrmex.cloud import CodaClient, CodaNotFoundError

# Initialize client
client = CodaClient(api_token="your-api-token")

# List all documents
docs = client.list_docs()
for doc in docs.items:
    print(f"{doc.name}: {doc.id}")

# Get a specific document
doc = client.get_doc("doc_id_here")

# Work with tables
tables = client.list_tables(doc.id)
rows = client.list_rows(doc.id, tables.items[0].id)

# Error handling
try:
    doc = client.get_doc("invalid_id")
except CodaNotFoundError:
    print("Document not found")
```

## Module Structure

| Directory/File | Description |
|----------------|-------------|
| `coda_io/` | Coda.io API client and models |
| `__init__.py` | Module exports and public API |
| `AGENTS.md` | Technical documentation for AI agents |
| `SPEC.md` | Functional specification |

## Coda.io Submodule

The `coda_io` submodule provides:

### Client
- `CodaClient`: Main API client class with authentication and request handling

### Models
- `Doc`, `DocList`: Document entities
- `Page`, `PageList`, `PageReference`: Page navigation
- `Table`, `TableList`, `TableReference`: Table structures
- `Column`, `ColumnList`: Column definitions
- `Row`, `RowList`, `RowEdit`, `CellEdit`: Row data and mutations
- `Formula`, `FormulaList`: Formula entities
- `Control`, `ControlList`: UI controls
- `Permission`, `PermissionList`, `SharingMetadata`, `ACLSettings`: Access control
- `User`, `WorkspaceReference`, `FolderReference`: Organization entities
- `Icon`, `DocSize`: Utility types

### Exceptions
- `CodaAPIError`: Base exception for API errors
- `CodaAuthenticationError`: Invalid or missing API token
- `CodaForbiddenError`: Insufficient permissions
- `CodaNotFoundError`: Resource not found
- `CodaRateLimitError`: API rate limit exceeded
- `CodaValidationError`: Invalid request parameters
- `CodaGoneError`: Resource has been deleted

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
