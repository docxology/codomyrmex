"""Unit tests for the dependency injection MCP tools."""

from codomyrmex.dependency_injection import inject, injectable
from codomyrmex.dependency_injection.mcp_tools import (
    di_get_inject_metadata,
    di_get_injectable_metadata,
)


@injectable(scope="singleton", auto_register=True, tags=("test", "dummy"))
class DummyInjectableService:
    """A dummy service for testing."""

    @inject
    def __init__(self, some_dependency: str) -> None:
        self.some_dependency = some_dependency


class DummyPlainService:
    """A plain service without decorators."""

    def __init__(self, some_dependency: str) -> None:
        self.some_dependency = some_dependency


def test_di_get_injectable_metadata_success() -> None:
    """Test retrieving injectable metadata for a decorated class."""
    # Build fully qualified name
    class_name = (
        f"{DummyInjectableService.__module__}.{DummyInjectableService.__qualname__}"
    )

    result = di_get_injectable_metadata(class_name)

    assert result is not None
    assert "error" not in result
    assert result["scope"] == "singleton"
    assert result["auto_register"] is True
    assert set(result["tags"]) == {"test", "dummy"}


def test_di_get_injectable_metadata_not_decorated() -> None:
    """Test retrieving injectable metadata for an undecorated class."""
    class_name = f"{DummyPlainService.__module__}.{DummyPlainService.__qualname__}"

    result = di_get_injectable_metadata(class_name)

    assert result is None


def test_di_get_injectable_metadata_not_found() -> None:
    """Test retrieving injectable metadata for a non-existent class."""
    class_name = (
        "codomyrmex.tests.unit.dependency_injection.test_mcp_tools.NonExistentClass"
    )

    result = di_get_injectable_metadata(class_name)

    assert result is not None
    assert "error" in result
    assert "Could not resolve attribute path" in result["error"]


def test_di_get_injectable_metadata_invalid_name() -> None:
    """Test retrieving injectable metadata with an invalid name."""
    result = di_get_injectable_metadata("NotFullyQualified")

    assert result is not None
    assert "error" in result
    assert "is not a fully qualified name" in result["error"]


def test_di_get_injectable_metadata_not_class() -> None:
    """Test retrieving injectable metadata for a non-class object."""
    class_name = f"{test_di_get_injectable_metadata_success.__module__}.{test_di_get_injectable_metadata_success.__qualname__}"

    result = di_get_injectable_metadata(class_name)

    assert result is not None
    assert "error" in result
    assert "is not a class" in result["error"]


def test_di_get_inject_metadata_success() -> None:
    """Test retrieving inject metadata for a decorated method."""
    method_name = f"{DummyInjectableService.__module__}.{DummyInjectableService.__qualname__}.__init__"

    result = di_get_inject_metadata(method_name)

    assert result is not None
    assert "error" not in result
    assert "params" in result
    assert result["resolve_all"] is True
    assert "injectable_params" in result
    assert "some_dependency" in result["injectable_params"]
    assert result["injectable_params"]["some_dependency"] == "str"


def test_di_get_inject_metadata_not_decorated() -> None:
    """Test retrieving inject metadata for an undecorated method."""
    method_name = (
        f"{DummyPlainService.__module__}.{DummyPlainService.__qualname__}.__init__"
    )

    result = di_get_inject_metadata(method_name)

    assert result is None


def test_di_get_inject_metadata_not_found() -> None:
    """Test retrieving inject metadata for a non-existent method."""
    method_name = "codomyrmex.tests.unit.dependency_injection.test_mcp_tools.DummyInjectableService.non_existent_method"

    result = di_get_inject_metadata(method_name)

    assert result is not None
    assert "error" in result
    assert "Could not resolve attribute path" in result["error"]


def test_di_get_inject_metadata_not_callable() -> None:
    """Test retrieving inject metadata for a non-callable attribute."""
    # Let's attach a dummy attribute to the service class
    DummyInjectableService.dummy_attr = "some_value"
    attr_name = f"{DummyInjectableService.__module__}.{DummyInjectableService.__qualname__}.dummy_attr"

    result = di_get_inject_metadata(attr_name)

    assert result is not None
    assert "error" in result
    assert "is not callable" in result["error"]
