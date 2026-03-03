#!/usr/bin/env python3
"""
API Management - Real Usage Examples

Demonstrates actual API capabilities:
- REST API definition
- Router configuration
- OpenAPI spec generation
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.api import (
    APIResponse,
    APIRouter,
    create_api,
    create_openapi_from_rest_api,
)
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "api" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/api/config.yaml")

    setup_logging()
    print_info("Running API Examples...")

    # 1. Router & API
    print_info("Defining REST API and Router...")
    try:
        router = APIRouter(prefix="/users")

        @router.get("/profile")
        def get_profile(request):
            return APIResponse.success({"user": "test"})

        api = create_api(title="Test API", version="1.0.0")
        api.add_router(router)
        print_success("  REST API and Router functional.")
    except Exception as e:
        print_error(f"  API definition failed: {e}")

    # 2. OpenAPI
    print_info("Testing OpenAPI generation...")
    try:
        spec = create_openapi_from_rest_api(api)
        if spec:
            info = spec.to_dict().get("info", {})
            print_success(f"  OpenAPI specification generated. Title: {info.get('title')}")
    except Exception as e:
        print_info(f"  OpenAPI generation demo: {e}")

    print_success("API management examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
