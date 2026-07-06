from src import get_template_info


def test_get_template_info() -> None:
    """Test that get_template_info returns the expected dictionary."""
    expected_info = {
        "name": "module_template",
        "description": "Project templates and boilerplate code",
        "location": "codomyrmex/module_template/",
        "components": ["AGENTS.md", "README.md", "SPEC.md", "docs/"],
    }

    info = get_template_info()

    assert isinstance(info, dict)
    assert info == expected_info
    assert info["name"] == "module_template"
    assert "AGENTS.md" in info["components"]
