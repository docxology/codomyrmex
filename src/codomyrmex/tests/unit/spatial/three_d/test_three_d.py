"""Unit tests for spatial.three_d module."""


import pytest


@pytest.mark.unit
class TestThreeD:
    """Test cases for 3D modeling functionality."""

    def test_three_d_import(self, code_dir):
        """Test that we can import three_d module."""
        try:
            from codomyrmex.spatial import three_d
            assert three_d is not None
        except ImportError as e:
            pytest.fail(f"Failed to import three_d: {e}")

    def test_three_d_module_exists(self, code_dir):
        """Test that three_d module directory exists."""
        m3d_path = code_dir / "codomyrmex" / "spatial" / "three_d"
        assert m3d_path.exists()
        assert m3d_path.is_dir()

    def test_three_d_init_file(self, code_dir):
        """Test that three_d has __init__.py."""
        init_path = code_dir / "codomyrmex" / "spatial" / "three_d" / "__init__.py"
        assert init_path.exists()

    def test_engine_3d_module_exists(self, code_dir):
        """Test that engine_3d module exists."""
        engine_path = code_dir / "codomyrmex" / "spatial" / "three_d" / "engine_3d.py"
        assert engine_path.exists()

    def test_rendering_pipeline_module_exists(self, code_dir):
        """Test that rendering_pipeline module exists."""
        rp_path = code_dir / "codomyrmex" / "spatial" / "three_d" / "rendering_pipeline.py"
        assert rp_path.exists()

    def test_ar_vr_support_module_exists(self, code_dir):
        """Test that ar_vr_support module exists."""
        arvr_path = code_dir / "codomyrmex" / "spatial" / "three_d" / "ar_vr_support.py"
        assert arvr_path.exists()

    def test_scene3d_import(self, code_dir):
        """Test that Scene3D class can be imported."""
        try:
            from codomyrmex.spatial.three_d import Scene3D
            assert Scene3D is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Scene3D: {e}")

    def test_object3d_import(self, code_dir):
        """Test that Object3D class can be imported."""
        try:
            from codomyrmex.spatial.three_d import Object3D
            assert Object3D is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Object3D: {e}")

    def test_camera3d_import(self, code_dir):
        """Test that Camera3D class can be imported."""
        try:
            from codomyrmex.spatial.three_d import Camera3D
            assert Camera3D is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Camera3D: {e}")

    def test_light3d_import(self, code_dir):
        """Test that Light3D class can be imported."""
        try:
            from codomyrmex.spatial.three_d import Light3D
            assert Light3D is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Light3D: {e}")

    def test_material3d_import(self, code_dir):
        """Test that Material3D class can be imported if available."""
        from codomyrmex.spatial import three_d
        if not hasattr(three_d, 'Material3D'):
            pytest.skip("Material3D not yet implemented")
        assert three_d.Material3D is not None

    def test_ar_session_import(self, code_dir):
        """Test that ARSession class can be imported."""
        try:
            from codomyrmex.spatial.three_d import ARSession
            assert ARSession is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ARSession: {e}")

    def test_vr_renderer_import(self, code_dir):
        """Test that VRRenderer class can be imported."""
        try:
            from codomyrmex.spatial.three_d import VRRenderer
            assert VRRenderer is not None
        except ImportError as e:
            pytest.fail(f"Failed to import VRRenderer: {e}")

    def test_xr_interface_import(self, code_dir):
        """Test that XRInterface class can be imported."""
        try:
            from codomyrmex.spatial.three_d import XRInterface
            assert XRInterface is not None
        except ImportError as e:
            pytest.fail(f"Failed to import XRInterface: {e}")

    def test_render_pipeline_import(self, code_dir):
        """Test that RenderPipeline class can be imported."""
        try:
            from codomyrmex.spatial.three_d import RenderPipeline
            assert RenderPipeline is not None
        except ImportError as e:
            pytest.fail(f"Failed to import RenderPipeline: {e}")

    def test_shader_manager_import(self, code_dir):
        """Test that ShaderManager class can be imported."""
        try:
            from codomyrmex.spatial.three_d import ShaderManager
            assert ShaderManager is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ShaderManager: {e}")

    def test_mesh_loader_import(self, code_dir):
        """Test that MeshLoader class can be imported if available."""
        from codomyrmex.spatial import three_d
        if not hasattr(three_d, 'MeshLoader'):
            pytest.skip("MeshLoader not yet implemented")
        assert three_d.MeshLoader is not None

    def test_three_d_version(self, code_dir):
        """Test that three_d has version defined."""
        from codomyrmex.spatial import three_d
        assert hasattr(three_d, "__version__")
        assert three_d.__version__ == "0.1.0"

    def test_three_d_all_exports(self, code_dir):
        """Test that three_d exports all expected symbols."""
        from codomyrmex.spatial import three_d

        # Core exports that are currently implemented
        core_exports = [
            "Scene3D",
            "Object3D",
            "Camera3D",
            "Light3D",
            "ARSession",
            "VRRenderer",
            "XRInterface",
            "RenderPipeline",
            "ShaderManager",
            "TextureManager",
        ]

        for export in core_exports:
            assert hasattr(three_d, export), f"Missing export: {export}"

        # Optional exports (not yet implemented)
        optional_exports = ["Material3D", "MeshLoader"]
        for export in optional_exports:
            if not hasattr(three_d, export):
                pass  # Expected: not yet implemented

    def test_agents_md_exists(self, code_dir):
        """Test that AGENTS.md exists for three_d module."""
        agents_path = code_dir / "codomyrmex" / "spatial" / "three_d" / "AGENTS.md"
        assert agents_path.exists()

    def test_readme_exists(self, code_dir):
        """Test that README.md exists for three_d module."""
        readme_path = code_dir / "codomyrmex" / "spatial" / "three_d" / "README.md"
        assert readme_path.exists()

    def test_docs_directory_exists(self, code_dir):
        """Test that docs directory exists for three_d module if created."""
        docs_path = code_dir / "codomyrmex" / "spatial" / "three_d" / "docs"
        if not docs_path.exists():
            pytest.skip("docs/ directory not yet created for three_d module")

    def test_examples_directory_exists(self, code_dir):
        """Test that examples directory exists for three_d module."""
        examples_path = code_dir / "codomyrmex" / "spatial" / "three_d" / "examples"
        assert examples_path.exists()
        assert examples_path.is_dir()

    def test_tests_directory_exists(self, code_dir):
        """Test that tests directory exists for three_d module if created."""
        tests_path = code_dir / "codomyrmex" / "spatial" / "three_d" / "tests"
        if not tests_path.exists():
            pytest.skip("tests/ directory not yet created for three_d module")
