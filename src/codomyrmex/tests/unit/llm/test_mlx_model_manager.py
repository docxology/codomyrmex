"""Comprehensive tests for MLXModelManager.

Pure-logic tests use temporary directories. Integration tests that require
mlx-lm or network access are gated behind ``mlx_available``.
"""

import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# MLX availability guard
# ---------------------------------------------------------------------------
mlx_available = importlib.util.find_spec("mlx") is not None
_skip_no_mlx = pytest.mark.skipif(not mlx_available, reason="mlx not installed")


# ===========================================================================
# 1. Helper functions — pure logic
# ===========================================================================


@pytest.mark.unit
class TestModelManagerHelpers:
    """Tests for _repo_to_dirname, _dirname_to_repo, _dir_size_bytes."""

    def test_repo_to_dirname(self):
        from codomyrmex.llm.mlx.model_manager import _repo_to_dirname

        assert _repo_to_dirname("mlx-community/Llama-3B") == "mlx-community--Llama-3B"

    def test_dirname_to_repo(self):
        from codomyrmex.llm.mlx.model_manager import _dirname_to_repo

        assert _dirname_to_repo("mlx-community--Llama-3B") == "mlx-community/Llama-3B"

    def test_roundtrip(self):
        from codomyrmex.llm.mlx.model_manager import (
            _dirname_to_repo,
            _repo_to_dirname,
        )

        original = "org/model-name-4bit"
        assert _dirname_to_repo(_repo_to_dirname(original)) == original

    def test_dir_size_bytes_empty(self):
        from codomyrmex.llm.mlx.model_manager import _dir_size_bytes

        with tempfile.TemporaryDirectory() as td:
            assert _dir_size_bytes(Path(td)) == 0

    def test_dir_size_bytes_with_files(self):
        from codomyrmex.llm.mlx.model_manager import _dir_size_bytes

        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            (p / "a.txt").write_text("hello")
            (p / "b.txt").write_text("world!")
            size = _dir_size_bytes(p)
            assert size == 5 + 6  # "hello" + "world!"

    def test_dir_size_bytes_nested(self):
        from codomyrmex.llm.mlx.model_manager import _dir_size_bytes

        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            sub = p / "sub"
            sub.mkdir()
            (sub / "file.bin").write_bytes(b"\x00" * 100)
            size = _dir_size_bytes(p)
            assert size == 100

    def test_read_config_json_missing(self):
        from codomyrmex.llm.mlx.model_manager import _read_config_json

        with tempfile.TemporaryDirectory() as td:
            assert _read_config_json(Path(td)) == {}

    def test_read_config_json_valid(self):
        from codomyrmex.llm.mlx.model_manager import _read_config_json

        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            config = {"model_type": "llama", "vocab_size": 32000}
            (p / "config.json").write_text(json.dumps(config))
            result = _read_config_json(p)
            assert result["model_type"] == "llama"
            assert result["vocab_size"] == 32000

    def test_read_config_json_invalid_json(self):
        from codomyrmex.llm.mlx.model_manager import _read_config_json

        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            (p / "config.json").write_text("{invalid json")
            assert _read_config_json(p) == {}


# ===========================================================================
# 2. MLXModelInfo dataclass
# ===========================================================================


@pytest.mark.unit
class TestMLXModelInfo:
    """MLXModelInfo construction and defaults."""

    def test_minimal_construction(self):
        from codomyrmex.llm.mlx.model_manager import MLXModelInfo

        info = MLXModelInfo(repo_id="org/model", local_path="/tmp/model")
        assert info.repo_id == "org/model"
        assert info.size_bytes == 0
        assert info.quantization is None
        assert info.model_type is None

    def test_full_construction(self):
        from codomyrmex.llm.mlx.model_manager import MLXModelInfo

        info = MLXModelInfo(
            repo_id="org/model",
            local_path="/tmp/model",
            size_bytes=4_000_000_000,
            quantization="4-bit",
            model_type="llama",
            vocab_size=32000,
            hidden_size=4096,
            num_layers=32,
            max_position_embeddings=8192,
        )
        assert info.size_bytes == 4_000_000_000
        assert info.quantization == "4-bit"
        assert info.num_layers == 32


# ===========================================================================
# 3. MLXModelManager — filesystem operations
# ===========================================================================


@pytest.mark.unit
class TestMLXModelManagerFilesystem:
    """Model manager with temp cache dir — no network."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        from codomyrmex.llm.mlx.config import MLXConfig

        self.config = MLXConfig(cache_dir=self.temp_dir)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cache_dir_created(self):
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        mgr = MLXModelManager(config=self.config)
        assert mgr.cache_dir.is_dir()

    def test_list_empty_cache(self):
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        mgr = MLXModelManager(config=self.config)
        assert mgr.list_cached_models() == []

    def test_list_with_fake_model(self):
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        # Create a fake model directory with config.json
        model_dir = Path(self.temp_dir) / "org--test-model"
        model_dir.mkdir()
        (model_dir / "config.json").write_text(
            json.dumps({"model_type": "test", "vocab_size": 100})
        )
        (model_dir / "weights.safetensors").write_bytes(b"\x00" * 1000)

        mgr = MLXModelManager(config=self.config)
        models = mgr.list_cached_models()
        assert len(models) == 1
        assert models[0].repo_id == "org/test-model"
        assert models[0].model_type == "test"
        assert models[0].size_bytes == 1000 + len(json.dumps({"model_type": "test", "vocab_size": 100}))

    def test_is_model_cached_false(self):
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        mgr = MLXModelManager(config=self.config)
        assert mgr.is_model_cached("org/nonexistent") is False

    def test_is_model_cached_true(self):
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        model_dir = Path(self.temp_dir) / "org--cached-model"
        model_dir.mkdir()

        mgr = MLXModelManager(config=self.config)
        assert mgr.is_model_cached("org/cached-model") is True

    def test_get_model_info_not_found(self):
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        mgr = MLXModelManager(config=self.config)
        assert mgr.get_model_info("org/missing") is None

    def test_get_model_info_found(self):
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        model_dir = Path(self.temp_dir) / "org--found-model"
        model_dir.mkdir()
        (model_dir / "config.json").write_text(
            json.dumps({
                "model_type": "llama",
                "hidden_size": 2048,
                "quantization_config": {"bits": 4, "group_size": 64},
            })
        )

        mgr = MLXModelManager(config=self.config)
        info = mgr.get_model_info("org/found-model")
        assert info is not None
        assert info.model_type == "llama"
        assert info.hidden_size == 2048
        assert info.quantization == "4-bit"

    def test_delete_model_not_found(self):
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        mgr = MLXModelManager(config=self.config)
        assert mgr.delete_model("org/missing") is False

    def test_delete_model_success(self):
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        model_dir = Path(self.temp_dir) / "org--deletable"
        model_dir.mkdir()
        (model_dir / "dummy.bin").write_bytes(b"\x00")

        mgr = MLXModelManager(config=self.config)
        assert mgr.delete_model("org/deletable") is True
        assert not model_dir.exists()

    def test_hidden_dirs_ignored(self):
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        (Path(self.temp_dir) / ".hidden").mkdir()
        (Path(self.temp_dir) / "org--visible").mkdir()

        mgr = MLXModelManager(config=self.config)
        models = mgr.list_cached_models()
        assert len(models) == 1


# ===========================================================================
# 4. Memory estimation
# ===========================================================================


@pytest.mark.unit
class TestMemoryEstimation:
    """Static memory estimation method."""

    def test_3b_4bit(self):
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        est = MLXModelManager.estimate_memory_gb(3.0, bits=4)
        assert 2.0 <= est <= 3.0  # ~1.4 GB weights + 1 GB overhead

    def test_7b_4bit(self):
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        est = MLXModelManager.estimate_memory_gb(7.0, bits=4)
        assert 4.0 <= est <= 5.0

    def test_7b_8bit(self):
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        est = MLXModelManager.estimate_memory_gb(7.0, bits=8)
        assert 7.0 <= est <= 8.0

    def test_custom_overhead(self):
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        est = MLXModelManager.estimate_memory_gb(3.0, bits=4, overhead_gb=2.0)
        assert est > MLXModelManager.estimate_memory_gb(3.0, bits=4, overhead_gb=1.0)
