# agents/openfang — API Specification

## Module: `codomyrmex.agents.openfang`

### `HAS_OPENFANG: bool`

Module-level flag. `True` if the openfang binary is found on PATH at import time.

---

## Class: `OpenFangConfig`

```python
@dataclass
class OpenFangConfig:
    command: str          # OPENFANG_COMMAND env var, default "openfang"
    timeout: int          # OPENFANG_TIMEOUT env var, default 120
    gateway_url: str      # OPENFANG_GATEWAY_URL env var, default "ws://localhost:3000"
    vendor_dir: str       # Computed from module __file__, no env var
    install_dir: str      # OPENFANG_INSTALL_DIR env var, default "/usr/local/bin"

    @property
    def vendor_path(self) -> Path: ...
    @property
    def is_submodule_initialized(self) -> bool: ...
    @property
    def cargo_binary(self) -> Path: ...
```

### `get_config() -> OpenFangConfig`

Return a fresh `OpenFangConfig` from the current environment.

---

## Class: `OpenFangRunner`

```python
class OpenFangRunner:
    def __init__(self, timeout: int | None = None, config: OpenFangConfig | None = None) -> None:
        """Raise OpenFangNotInstalledError if binary not found."""

    def execute(self, prompt: str) -> dict[str, str]:
        """Run openfang agent --message <prompt>."""

    def stream(self, prompt: str) -> Iterator[str]:
        """Stream agent output line by line."""

    def hands_list(self) -> dict[str, str]:
        """Run openfang hands list."""

    def hands_run(self, hand_name: str, config_path: str = "") -> dict[str, str]:
        """Run openfang hands run <hand_name>."""

    def send_message(self, channel: str, target: str, message: str) -> dict[str, str]:
        """Run openfang message send --channel --to --message."""

    def gateway_action(self, action: str) -> dict[str, str]:
        """Run openfang gateway <start|stop|status>."""

    def doctor(self) -> dict[str, str]:
        """Run openfang doctor."""

    def version(self) -> dict[str, str]:
        """Run openfang --version."""
```

All methods return `{"stdout": str, "stderr": str, "returncode": str}`.
Raise `OpenFangTimeoutError` on timeout.

### `get_openfang_version() -> str`

Return the openfang version string, or `""` if not installed.

---

## Class: `Hand`

```python
@dataclass
class Hand:
    name: str
    description: str = ""
    schedule: str = ""
    enabled: bool = True
    tags: list[str] = field(default_factory=list)
```

## Class: `HandsManager`

```python
class HandsManager:
    @staticmethod
    def parse_list_output(raw_output: str) -> list[Hand]:
        """Parse `openfang hands list` text output into Hand objects."""
```

---

## Update Functions

```python
def update_submodule(vendor_dir: str = "", timeout: int = 300) -> dict[str, str]: ...
def build_from_source(vendor_dir: str = "", timeout: int = 600) -> dict[str, str]: ...
def install_binary(vendor_dir: str = "", install_dir: str = "") -> dict[str, str]: ...
def build_and_install(vendor_dir: str = "", install_dir: str = "") -> dict[str, str]: ...
def get_upstream_version(vendor_dir: str = "") -> str: ...
```

All return `{"status": "success"|"error", ...}`.

---

## Exceptions

```python
class OpenFangError(Exception): ...
class OpenFangNotInstalledError(OpenFangError): ...
class OpenFangTimeoutError(OpenFangError): ...
class OpenFangBuildError(OpenFangError): ...
class OpenFangConfigError(OpenFangError): ...
```
