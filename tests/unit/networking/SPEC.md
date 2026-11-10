# Networking test specification

Default networking tests validate local HTTP, URL, socket, response, and SSH object contracts with isolated resources. SSH constructors receive an explicit temporary known-hosts file. A real generated key and Paramiko host-key store verify loading only that file; a real socket-pair transport verifies that the default `RejectPolicy` rejects an unknown key without adding trust.

The two credentialed SSH execution tests require `CODOMYRMEX_RUN_LIVE_SSH_TESTS=1` and explicit key, known-hosts file, and username environment inputs documented in [README.md](README.md). Binary availability, an open localhost port, or a personal key file does not authorize a live test. Every live client is closed in a `finally` block.

Run `.venv/bin/python -m pytest -q tests/unit/networking` from the repository root. Local trust controls remain enabled with Paramiko installed; they require no daemon, account credentials, personal configuration, or network service.

## Navigation

- [README.md](README.md)
- [AGENTS.md](AGENTS.md)
- [Parent directory](../README.md)

## Public-only HTTP policy

The focused suite uses explicit address data, actual localhost DNS, real requests
objects, and isolated ephemeral loopback servers. It does not resolve public names
or contact external services. It proves classification and negative admission plus
legacy local compatibility. A successful public HTTP/TLS connection, external
redirect chain, and adversarial DNS rebinding sequence require a separately
controlled integration environment; the offline suite does not claim those results.
