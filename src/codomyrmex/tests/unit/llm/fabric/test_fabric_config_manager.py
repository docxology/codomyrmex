import os
import shutil
import tempfile

import pytest

from codomyrmex.llm.fabric.fabric_config_manager import FabricConfigManager, FabricPattern


@pytest.fixture
def temp_config_dir():
    """Fixture to provide a temporary directory for storing the config."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_fabric_config_manager_load_and_save(temp_config_dir):
    """Test loading, saving, and persisting Fabric config naturally."""
    config_path = os.path.join(temp_config_dir, "config.json")

    # Init first time
    manager = FabricConfigManager(config_path=config_path)

    # Assert defaults
    assert manager.config.default_model == "gpt-4"
    assert manager.config.api_key is None

    # Modify and save
    manager.config.api_key = "sk-test-key"
    manager.config.default_model = "claude-3-opus"
    manager.save_config()

    assert os.path.exists(config_path)

    # Load second time to verify persistence
    manager2 = FabricConfigManager(config_path=config_path)
    assert manager2.config.api_key == "sk-test-key"
    assert manager2.config.default_model == "claude-3-opus"


def test_fabric_config_manager_patterns(temp_config_dir):
    """Test adding and retrieving patterns naturally."""
    config_path = os.path.join(temp_config_dir, "config.json")
    manager = FabricConfigManager(config_path=config_path)

    pattern = FabricPattern(
        name="test_pattern",
        description="A test pattern",
        system_prompt="You are a helpful assistant.",
        user_prompt_template="Help me with {task}"
    )

    manager.add_pattern(pattern)
    assert manager.get_pattern("test_pattern") is not None
    assert "test_pattern" in manager.list_patterns()
    assert manager.config.custom_patterns["test_pattern"].system_prompt == "You are a helpful assistant."
