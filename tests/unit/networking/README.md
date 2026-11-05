# networking

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

## Overview

Validation coverage, fixtures, and regression checks for Networking.

## Directory Contents

- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `conftest.py` – Explicit temporary trust and live SSH fixtures
- `test_ssh_trust_isolation.py` – Real Paramiko trust-store and rejection controls
- `__init__.py` – File
- `test_mcp_tools_networking.py` – File
- `test_networking.py` – File
- `test_networking_core.py` – File
- `test_networking_exceptions.py` – File
- `test_networking_expansion.py` – File
- `test_networking_reliability.py` – File
- `test_response_error.py` – File
- `test_websocket_client.py` – File

## Navigation

- **Parent Directory**: [unit](../README.md)
- **Project Root**: ../../../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)

## SSH isolation

Default tests use an explicit temporary `known_hosts_file`, real local Paramiko objects, and `RejectPolicy`; they do not discover operator SSH keys, load personal trust stores, or probe a daemon during collection.

Credentialed SSH execution requires `CODOMYRMEX_RUN_LIVE_SSH_TESTS=1` plus explicit `CODOMYRMEX_TEST_SSH_KEY`, `CODOMYRMEX_TEST_SSH_KNOWN_HOSTS`, and `CODOMYRMEX_TEST_SSH_USER`. Optional `CODOMYRMEX_TEST_SSH_HOST` and `CODOMYRMEX_TEST_SSH_PORT` select the authorized endpoint (defaults: localhost, 22). Missing configuration fails an opted-in test; ordinary runs skip only the two live account tests.

## Public-only HTTP policy

`test_http_public_policy.py` checks public/non-public and IPv6 transition address
classification, complete mixed DNS-answer rejection, real localhost resolution in
HTTP and HTTPS connectors, URL/Host restrictions, proxy controls, and TLS verification
requirements. Real loopback servers verify default local access and protected-mode
rejection without contact. It uses no external requests or patched network methods.
