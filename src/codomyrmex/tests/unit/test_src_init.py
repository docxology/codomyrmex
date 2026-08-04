import pytest
from src import get_template_info

def test_get_template_info():
    info = get_template_info()
    assert isinstance(info, dict)
    assert info["name"] == "module_template"
    assert info["description"] == "Project templates and boilerplate code"
    assert info["location"] == "codomyrmex/module_template/"
    assert info["components"] == ["AGENTS.md", "README.md", "SPEC.md", "docs/"]
