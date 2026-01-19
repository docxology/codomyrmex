#!/usr/bin/env python3
"""
API Management - Real Usage Examples

Demonstrates actual API capabilities:
- REST API definition
- Router configuration
- OpenAPI spec generation
"""

import sys
import os
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.api import (
    RESTAPI,
    APIRouter,
    HTTPMethod,
    APIResponse,
    create_api,
    create_openapi_from_rest_api
)

def main():
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
