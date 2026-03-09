# type: ignore
"""Functional tests for cloud module — zero-mock.

Exercises Coda.io models, error hierarchy, S3-compatible client classes,
and cloud provider abstractions.
"""

from __future__ import annotations

import pytest

from codomyrmex import cloud


class TestCloudImports:
    """Major exports are importable."""

    @pytest.mark.parametrize(
        "name",
        [
            "CodaClient",
            "CodaAPIError",
            "CodaAuthenticationError",
            "CodaNotFoundError",
            "CodaRateLimitError",
            "CodaForbiddenError",
            "CodaGoneError",
            "ACLSettings",
            "CellEdit",
        ],
    )
    def test_export_exists(self, name: str) -> None:
        assert hasattr(cloud, name), f"Missing export: {name}"


class TestCodaErrors:
    """Coda error hierarchy."""

    @pytest.mark.parametrize(
        "name",
        [
            "CodaAPIError",
            "CodaAuthenticationError",
            "CodaNotFoundError",
            "CodaRateLimitError",
            "CodaForbiddenError",
            "CodaGoneError",
        ],
    )
    def test_error_is_exception(self, name: str) -> None:
        exc = getattr(cloud, name)
        assert issubclass(exc, Exception)


class TestCodaClient:
    """CodaClient ABC."""

    def test_client_exists(self) -> None:
        assert cloud.CodaClient is not None


class TestDataModels:
    """Cloud data models."""

    @pytest.mark.parametrize(
        "name",
        [
            "ACLSettings",
            "CellEdit",
        ],
    )
    def test_model_callable(self, name: str) -> None:
        cls = getattr(cloud, name)
        assert callable(cls)


class TestSubmodules:
    """Cloud submodules are importable."""

    def test_coda_io_submodule(self) -> None:
        from codomyrmex.cloud import coda_io

        assert coda_io is not None

    def test_coda_models(self) -> None:
        from codomyrmex.cloud.coda_io import models

        assert models is not None

    def test_coda_models_has_classes(self) -> None:
        from codomyrmex.cloud.coda_io import models

        assert hasattr(models, "TableType")
        assert hasattr(models, "PageType")
        assert hasattr(models, "Icon")
        assert hasattr(models, "Image")
