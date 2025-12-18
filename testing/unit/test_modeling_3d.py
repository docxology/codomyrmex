"""Unit tests for modeling_3d module."""

import sys
import pytest
from pathlib import Path


class TestModeling3D:
    """Test cases for 3D modeling functionality."""

    def test_modeling_3d_import(self, code_dir):
        """Test that we can import modeling_3d module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex import modeling_3d
            assert modeling_3d is not None
        except ImportError as e:
            pytest.fail(f"Failed to import modeling_3d: {e}")

    def test_modeling_3d_module_exists(self, code_dir):
        """Test that modeling_3d module directory exists."""
        m3d_path = code_dir / "codomyrmex" / "modeling_3d"
        assert m3d_path.exists()
        assert m3d_path.is_dir()

    def test_modeling_3d_init_file(self, code_dir):
        """Test that modeling_3d has __init__.py."""
        init_path = code_dir / "codomyrmex" / "modeling_3d" / "__init__.py"
        assert init_path.exists()

    def test_engine_3d_module_exists(self, code_dir):
        """Test that engine_3d module exists."""
        engine_path = code_dir / "codomyrmex" / "modeling_3d" / "engine_3d.py"
        assert engine_path.exists()

    def test_rendering_pipeline_module_exists(self, code_dir):
        """Test that rendering_pipeline module exists."""
        rp_path = code_dir / "codomyrmex" / "modeling_3d" / "rendering_pipeline.py"
        assert rp_path.exists()

    def test_ar_vr_support_module_exists(self, code_dir):
        """Test that ar_vr_support module exists."""
        arvr_path = code_dir / "codomyrmex" / "modeling_3d" / "ar_vr_support.py"
        assert arvr_path.exists()

    def test_scene3d_import(self, code_dir):
        """Test that Scene3D class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.modeling_3d import Scene3D
            assert Scene3D is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Scene3D: {e}")

    def test_object3d_import(self, code_dir):
        """Test that Object3D class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.modeling_3d import Object3D
            assert Object3D is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Object3D: {e}")

    def test_camera3d_import(self, code_dir):
        """Test that Camera3D class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.modeling_3d import Camera3D
            assert Camera3D is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Camera3D: {e}")

    def test_light3d_import(self, code_dir):
        """Test that Light3D class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.modeling_3d import Light3D
            assert Light3D is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Light3D: {e}")

    def test_material3d_import(self, code_dir):
        """Test that Material3D class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.modeling_3d import Material3D
            assert Material3D is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Material3D: {e}")

    def test_ar_session_import(self, code_dir):
        """Test that ARSession class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.modeling_3d import ARSession
            assert ARSession is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ARSession: {e}")

    def test_vr_renderer_import(self, code_dir):
        """Test that VRRenderer class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.modeling_3d import VRRenderer
            assert VRRenderer is not None
        except ImportError as e:
            pytest.fail(f"Failed to import VRRenderer: {e}")

    def test_xr_interface_import(self, code_dir):
        """Test that XRInterface class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.modeling_3d import XRInterface
            assert XRInterface is not None
        except ImportError as e:
            pytest.fail(f"Failed to import XRInterface: {e}")

    def test_render_pipeline_import(self, code_dir):
        """Test that RenderPipeline class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.modeling_3d import RenderPipeline
            assert RenderPipeline is not None
        except ImportError as e:
            pytest.fail(f"Failed to import RenderPipeline: {e}")

    def test_shader_manager_import(self, code_dir):
        """Test that ShaderManager class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.modeling_3d import ShaderManager
            assert ShaderManager is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ShaderManager: {e}")

    def test_mesh_loader_import(self, code_dir):
        """Test that MeshLoader class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.modeling_3d import MeshLoader
            assert MeshLoader is not None
        except ImportError as e:
            pytest.fail(f"Failed to import MeshLoader: {e}")

    def test_modeling_3d_version(self, code_dir):
        """Test that modeling_3d has version defined."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex import modeling_3d
        assert hasattr(modeling_3d, "__version__")
        assert modeling_3d.__version__ == "0.1.0"

    def test_modeling_3d_all_exports(self, code_dir):
        """Test that modeling_3d exports all expected symbols."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex import modeling_3d

        expected_exports = [
            "Scene3D",
            "Object3D",
            "Camera3D",
            "Light3D",
            "Material3D",
            "ARSession",
            "VRRenderer",
            "XRInterface",
            "RenderPipeline",
            "ShaderManager",
            "TextureManager",
            "MeshLoader",
        ]

        for export in expected_exports:
            assert hasattr(modeling_3d, export), f"Missing export: {export}"

    def test_agents_md_exists(self, code_dir):
        """Test that AGENTS.md exists for modeling_3d module."""
        agents_path = code_dir / "codomyrmex" / "modeling_3d" / "AGENTS.md"
        assert agents_path.exists()

    def test_readme_exists(self, code_dir):
        """Test that README.md exists for modeling_3d module."""
        readme_path = code_dir / "codomyrmex" / "modeling_3d" / "README.md"
        assert readme_path.exists()

    def test_docs_directory_exists(self, code_dir):
        """Test that docs directory exists for modeling_3d module."""
        docs_path = code_dir / "codomyrmex" / "modeling_3d" / "docs"
        assert docs_path.exists()
        assert docs_path.is_dir()

    def test_examples_directory_exists(self, code_dir):
        """Test that examples directory exists for modeling_3d module."""
        examples_path = code_dir / "codomyrmex" / "modeling_3d" / "examples"
        assert examples_path.exists()
        assert examples_path.is_dir()

    def test_tests_directory_exists(self, code_dir):
        """Test that tests directory exists for modeling_3d module."""
        tests_path = code_dir / "codomyrmex" / "modeling_3d" / "tests"
        assert tests_path.exists()
        assert tests_path.is_dir()


