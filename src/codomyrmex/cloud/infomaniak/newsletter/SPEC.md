# Newsletter -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

REST client for the Infomaniak Newsletter API (`https://api.infomaniak.com/1/newsletters/{id}/...`). Provides full campaign lifecycle management, mailing list operations, and contact management with OAuth2 Bearer token authentication.

## Architecture

Single client class (`InfomaniakNewsletterClient`) inheriting from `InfomaniakRESTBase`. Internal helpers (`_get`, `_post`, `_put`, `_delete`) handle HTTP, response unwrapping (`data` key extraction), and error classification.

## Key Classes

### `InfomaniakNewsletterClient`

#### Campaigns

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_campaigns` | -- | `list[dict]` | List all campaigns |
| `get_campaign` | `campaign_id: str` | `dict \| None` | Get campaign details |
| `create_campaign` | `subject: str, sender_email: str, sender_name: str, content_html: str, mailing_list_id: str` | `dict \| None` | Create a new campaign |
| `update_campaign` | `campaign_id: str, **kwargs` | `dict \| None` | Update campaign fields |
| `delete_campaign` | `campaign_id: str` | `bool` | Delete a campaign |
| `send_test` | `campaign_id: str, email: str` | `bool` | Send test email |
| `send_campaign` | `campaign_id: str` | `bool` | Send immediately |
| `schedule_campaign` | `campaign_id: str, send_at: str` | `bool` | Schedule for ISO 8601 datetime |
| `unschedule_campaign` | `campaign_id: str` | `bool` | Cancel scheduled send |
| `get_campaign_statistics` | `campaign_id: str` | `dict \| None` | Opens, clicks, bounces |

#### Mailing Lists

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_mailing_lists` | -- | `list[dict]` | List all mailing lists |
| `get_mailing_list` | `list_id: str` | `dict \| None` | Get list details |
| `create_mailing_list` | `name: str` | `dict \| None` | Create a mailing list |
| `update_mailing_list` | `list_id: str, **kwargs` | `dict \| None` | Update list fields |
| `delete_mailing_list` | `list_id: str` | `bool` | Delete a mailing list |
| `get_list_contacts` | `list_id: str` | `list[dict]` | Get contacts in a list |
| `import_contacts` | `list_id: str, contacts: list[dict]` | `dict \| None` | Bulk import contacts |
| `manage_contact` | `list_id: str, contact_id: str, action: str` | `bool` | Subscribe or unsubscribe contact |

#### Contacts

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `get_contact` | `contact_id: str` | `dict \| None` | Get contact details |
| `update_contact` | `contact_id: str, **kwargs` | `dict \| None` | Update contact fields |
| `delete_contact` | `contact_id: str` | `bool` | Delete a contact |

#### Utility

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `get_task_status` | `task_id: str` | `dict \| None` | Check async task status |
| `get_credits` | -- | `dict \| None` | Newsletter credit balance |
| `validate_connection` | -- | `bool` | Health check via credits endpoint |

## Dependencies

- **Internal**: `codomyrmex.cloud.infomaniak.base.InfomaniakRESTBase`, `codomyrmex.cloud.infomaniak.exceptions`
- **External**: `requests`

## Constraints

- `manage_contact()` only accepts `"subscribe"` or `"unsubscribe"`; raises `ValueError` otherwise.
- API responses are unwrapped: the client extracts `data` key from JSON responses automatically.
- Returns `None` on HTTP errors for GET/POST/PUT; returns `False` for DELETE failures.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- All HTTP errors are classified via `classify_http_error()` into `InfomaniakCloudError` subtypes.
- Errors are logged at `ERROR` level with operation context before returning `None`/`False`.
- `from_env()` raises `ValueError` if required env vars are missing.
