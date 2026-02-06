"""Tests for the skills discovery submodule."""

import types

import pytest

from codomyrmex.skills.discovery import (
    DEFAULT_REGISTRY,
    FunctionSkill,
    ParameterSchema,
    SkillCategory,
    SkillDiscoverer,
    SkillMetadata,
    SkillRegistry,
    get_skill,
    register_skill,
    skill,
)


@pytest.mark.unit
def test_skill_category_enum():
    """Test all enum values exist."""
    assert SkillCategory.CODE.value == "code"
    assert SkillCategory.DATA.value == "data"
    assert SkillCategory.WEB.value == "web"
    assert SkillCategory.FILE.value == "file"
    assert SkillCategory.SYSTEM.value == "system"
    assert SkillCategory.COMMUNICATION.value == "communication"
    assert SkillCategory.REASONING.value == "reasoning"
    assert SkillCategory.UTILITY.value == "utility"


@pytest.mark.unit
def test_parameter_schema_to_dict():
    """Test ParameterSchema serialization."""
    param = ParameterSchema(
        name="query",
        param_type="string",
        description="Search query",
        required=True,
        enum_values=["a", "b"],
    )
    d = param.to_dict()
    assert d["name"] == "query"
    assert d["type"] == "string"
    assert d["required"] is True
    assert d["enum"] == ["a", "b"]


@pytest.mark.unit
def test_skill_metadata_to_dict():
    """Test SkillMetadata serialization."""
    meta = SkillMetadata(
        id="test-123",
        name="test_skill",
        description="A test skill",
        version="1.0.0",
        category=SkillCategory.UTILITY,
        tags=["test"],
    )
    d = meta.to_dict()
    assert d["id"] == "test-123"
    assert d["name"] == "test_skill"
    assert d["category"] == "utility"
    assert d["tags"] == ["test"]
    assert d["enabled"] is True


@pytest.mark.unit
def test_skill_metadata_to_json_schema():
    """Test JSON schema generation."""
    meta = SkillMetadata(
        id="test-123",
        name="test_skill",
        description="A test skill",
        parameters=[
            ParameterSchema(name="x", param_type="integer", description="An int", required=True),
            ParameterSchema(name="y", param_type="string", description="A str", required=False),
        ],
    )
    schema = meta.to_json_schema()
    assert schema["name"] == "test_skill"
    assert "x" in schema["parameters"]["properties"]
    assert "x" in schema["parameters"]["required"]
    assert "y" not in schema["parameters"]["required"]


@pytest.mark.unit
def test_function_skill_creation():
    """Test wrapping a function as a FunctionSkill."""
    def my_func(x: int, y: str = "hello") -> str:
        """My function."""
        return f"{y}: {x}"

    fs = FunctionSkill(my_func)
    assert fs.metadata.name == "my_func"
    assert fs.metadata.description == "My function."
    assert len(fs.metadata.parameters) == 2


@pytest.mark.unit
def test_function_skill_metadata_inference():
    """Test auto-inference from function signature."""
    def add(a: int, b: float = 1.0) -> float:
        """Add two numbers."""
        return a + b

    fs = FunctionSkill(add)
    param_names = [p.name for p in fs.metadata.parameters]
    assert "a" in param_names
    assert "b" in param_names

    a_param = next(p for p in fs.metadata.parameters if p.name == "a")
    assert a_param.param_type == "integer"
    assert a_param.required is True

    b_param = next(p for p in fs.metadata.parameters if p.name == "b")
    assert b_param.param_type == "number"
    assert b_param.required is False
    assert b_param.default == 1.0


@pytest.mark.unit
def test_function_skill_execute():
    """Test that execution delegates to the wrapped function."""
    def multiply(x: int, y: int) -> int:
        return x * y

    fs = FunctionSkill(multiply)
    result = fs.execute(x=3, y=4)
    assert result == 12


@pytest.mark.unit
def test_skill_validate_params():
    """Test parameter validation."""
    def my_func(required_param: str):
        """Needs a param."""
        return required_param

    fs = FunctionSkill(my_func)
    errors = fs.validate_params()
    assert len(errors) == 1
    assert "required_param" in errors[0]

    errors = fs.validate_params(required_param="ok")
    assert len(errors) == 0


@pytest.mark.unit
def test_registry_register_unregister():
    """Test register and unregister."""
    registry = SkillRegistry()

    def my_func():
        """Test."""
        pass

    fs = FunctionSkill(my_func)
    registry.register(fs)
    assert registry.get(fs.metadata.id) is fs

    registry.unregister(fs.metadata.id)
    assert registry.get(fs.metadata.id) is None


@pytest.mark.unit
def test_registry_search_by_query():
    """Test text search."""
    registry = SkillRegistry()

    def hello_world():
        """Says hello to the world."""
        return "hello"

    def goodbye_world():
        """Says goodbye."""
        return "bye"

    fs1 = FunctionSkill(hello_world)
    fs2 = FunctionSkill(goodbye_world)
    registry.register(fs1)
    registry.register(fs2)

    results = registry.search(query="hello")
    assert len(results) == 1
    assert results[0].metadata.name == "hello_world"


@pytest.mark.unit
def test_registry_search_by_category():
    """Test category filter."""
    registry = SkillRegistry()

    meta1 = SkillMetadata(id="s1", name="skill1", description="Skill 1", category=SkillCategory.CODE)
    meta2 = SkillMetadata(id="s2", name="skill2", description="Skill 2", category=SkillCategory.WEB)

    def f1():
        return 1

    def f2():
        return 2

    fs1 = FunctionSkill(f1, metadata=meta1)
    fs2 = FunctionSkill(f2, metadata=meta2)
    registry.register(fs1)
    registry.register(fs2)

    results = registry.search(category=SkillCategory.CODE)
    assert len(results) == 1
    assert results[0].metadata.id == "s1"


@pytest.mark.unit
def test_registry_search_by_tags():
    """Test tag filter."""
    registry = SkillRegistry()

    meta = SkillMetadata(id="tagged", name="tagged_skill", description="Tagged", tags=["python", "ai"])

    def f():
        return True

    fs = FunctionSkill(f, metadata=meta)
    registry.register(fs)

    results = registry.search(tags=["python"])
    assert len(results) == 1
    assert results[0].metadata.id == "tagged"

    results = registry.search(tags=["nonexistent"])
    assert len(results) == 0


@pytest.mark.unit
def test_registry_execute():
    """Test execute via registry."""
    registry = SkillRegistry()

    def double(x: int) -> int:
        """Double a number."""
        return x * 2

    fs = FunctionSkill(double)
    registry.register(fs)

    result = registry.execute(fs.metadata.id, x=5)
    assert result == 10


@pytest.mark.unit
def test_skill_decorator():
    """Test @skill decorator creates FunctionSkill."""
    registry = SkillRegistry()

    @skill(name="greet", description="Greet someone", tags=["demo"], registry=registry)
    def greet_func(name: str) -> str:
        """Say hi."""
        return f"Hello, {name}!"

    # The decorator returns a FunctionSkill
    assert isinstance(greet_func, FunctionSkill)
    assert greet_func.metadata.name == "greet"
    assert greet_func.metadata.description == "Greet someone"
    assert "demo" in greet_func.metadata.tags

    # It should be registered
    found = registry.get(greet_func.metadata.id)
    assert found is greet_func


@pytest.mark.unit
def test_discoverer_from_module():
    """Test module discovery."""
    registry = SkillRegistry()
    discoverer = SkillDiscoverer(registry)

    # Create a mock module with a FunctionSkill
    mock_module = types.ModuleType("mock_skills")

    def helper():
        """A helper skill."""
        return 42

    fs = FunctionSkill(helper)
    mock_module.my_skill = fs

    discovered = discoverer.discover_from_module(mock_module)
    assert len(discovered) >= 1
    assert registry.get(fs.metadata.id) is not None


@pytest.mark.unit
def test_default_registry():
    """Test global registry functions."""
    def unique_test_func_12345():
        """Unique for testing."""
        return "unique"

    fs = FunctionSkill(unique_test_func_12345)
    register_skill(fs)

    found = get_skill(fs.metadata.id)
    assert found is fs

    # Clean up
    DEFAULT_REGISTRY.unregister(fs.metadata.id)
