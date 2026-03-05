# cloud/google_workspace

Direct Google Workspace SDK clients using `google-api-python-client`. Typed Python wrappers for Drive, Gmail, Calendar, Sheets, Docs, and Chat APIs.

## Installation

```bash
uv sync --extra google_workspace
```

## Authentication

Uses service account credentials. Set one of:
- `GWS_SERVICE_ACCOUNT_FILE` — path to service account JSON key file
- `GOOGLE_APPLICATION_CREDENTIALS` — same, standard Google env var

## Quick Start

```python
from codomyrmex.cloud.google_workspace import GoogleDriveClient

client = GoogleDriveClient.from_env()
files = client.list_files(query="name contains 'report'", page_size=10)
for f in files:
    print(f["name"])
```

## Available Clients

| Client | API | Version |
|--------|-----|---------|
| `GoogleDriveClient` | Drive | v3 |
| `GoogleGmailClient` | Gmail | v1 |
| `GoogleCalendarClient` | Calendar | v3 |
| `GoogleSheetsClient` | Sheets | v4 |
| `GoogleDocsClient` | Docs | v1 |
| `GoogleChatClient` | Chat | v1 |

## Context Manager

```python
with GoogleDriveClient.from_env() as client:
    files = client.list_files()
```
