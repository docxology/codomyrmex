# Codomyrmex Agents — src/codomyrmex/cloud/infomaniak/newsletter

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

REST API client for Infomaniak's Newsletter service. Provides campaign management (create, send, schedule, statistics), mailing list CRUD, contact management (import, subscribe/unsubscribe), and utility endpoints (credits, async task status).

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `client.py` | `InfomaniakNewsletterClient` | Main client; extends `InfomaniakRESTBase` with OAuth2 Bearer auth |
| `client.py` | `from_env()` | Factory that reads `INFOMANIAK_NEWSLETTER_TOKEN` and `INFOMANIAK_NEWSLETTER_ID` |
| `client.py` | `from_credentials()` | Factory accepting explicit token and newsletter ID |
| `client.py` | `validate_connection()` | Health check via `get_credits()` |
| `__init__.py` | -- | Re-exports `InfomaniakNewsletterClient` |

## Operating Contracts

- Requires env vars `INFOMANIAK_NEWSLETTER_TOKEN` (OAuth2 bearer) and `INFOMANIAK_NEWSLETTER_ID` (product ID) for `from_env()`.
- All HTTP methods (`_get`, `_post`, `_put`, `_delete`) classify errors via `classify_http_error()` from `infomaniak.exceptions`.
- `manage_contact()` validates `action` against `{"subscribe", "unsubscribe"}`; raises `ValueError` for invalid actions.
- List methods (`list_campaigns`, `list_mailing_lists`, `get_list_contacts`) normalize API response shape to `list[dict]`.
- The client is a context manager (`with` statement supported via `InfomaniakRESTBase`).
- Errors must be logged via module logger before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.cloud.infomaniak.base.InfomaniakRESTBase`, `codomyrmex.cloud.infomaniak.exceptions.classify_http_error`, `requests`
- **Used by**: Any agent needing email campaign automation via Infomaniak

## Navigation

- **Parent**: [infomaniak](../README.md)
- **Root**: [Root](../../../../../README.md)
