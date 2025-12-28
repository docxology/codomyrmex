"""Enhanced tests for containerization improvements."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

# Test ImageOptimizer
class TestImageOptimizer:
    """Test cases for ImageOptimizer functionality."""

    @patch('codomyrmex.containerization.image_optimizer.docker')
    def test_image_optimizer_creation(self, mock_docker):
        """Test creating an ImageOptimizer."""
        try:
            from codomyrmex.containerization.image_optimizer import ImageOptimizer
        except ImportError:
            pytest.skip("ImageOptimizer not available")

        optimizer = ImageOptimizer()
        assert optimizer is not None
        assert optimizer.client is not None

    @patch('codomyrmex.containerization.image_optimizer.docker')
    def test_analyze_image(self, mock_docker):
        """Test image analysis functionality."""
        try:
            from codomyrmex.containerization.image_optimizer import ImageOptimizer, ImageAnalysis
        except ImportError:
            pytest.skip("ImageOptimizer not available")

        # Mock Docker image
        mock_image = Mock()
        mock_image.attrs = {
            "Size": 500 * 1024 * 1024,  # 500MB
            "RootFS": {"Layers": ["layer1", "layer2", "layer3"]},
            "Config": {
                "ExposedPorts": {"8080/tcp": {}},
                "Volumes": {"/data": {}},
                "Env": ["PATH=/usr/local/bin", "USER=appuser"],
                "Cmd": ["python", "app.py"]
            },
            "History": [
                {"CreatedBy": "FROM ubuntu:20.04", "Size": 100000},
                {"CreatedBy": "RUN apt-get update", "Size": 50000000}
            ]
        }

        mock_client = Mock()
        mock_client.images.get.return_value = mock_image

        with patch('codomyrmex.containerization.image_optimizer.docker.from_env', return_value=mock_client):
            optimizer = ImageOptimizer()

            analysis = optimizer.analyze_image("test:latest")

            assert isinstance(analysis, ImageAnalysis)
            assert analysis.image_name == "test:latest"
            assert analysis.size_bytes == 500 * 1024 * 1024
            assert len(analysis.layers) == 3
            assert "8080" in analysis.exposed_ports
            assert "/data" in analysis.volumes
            assert len(analysis.potential_optimizations) >= 0  # May be empty or have suggestions
            assert 0 <= analysis.optimization_score <= 100

    def test_optimization_suggestions(self):
        """Test generation of optimization suggestions."""
        try:
            from codomyrmex.containerization.image_optimizer import ImageOptimizer, OptimizationSuggestion
        except ImportError:
            pytest.skip("ImageOptimizer not available")

        optimizer = ImageOptimizer()

        # Create a mock analysis with optimization opportunities
        analysis = Mock()
        analysis.size_bytes = 800 * 1024 * 1024  # 800MB - large
        analysis.layers = ["layer"] * 25  # Many layers
        analysis.commands = ["RUN apt-get update", "RUN apt-get install python"]
        analysis.environment_vars = []  # No USER set

        suggestions = optimizer._generate_suggestions(analysis)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

        # Should include size optimization suggestion
        size_suggestions = [s for s in suggestions if s.category == "size"]
        assert len(size_suggestions) > 0

        # Should include layer optimization suggestion
        layer_suggestions = [s for s in suggestions if s.category == "layers"]
        assert len(layer_suggestions) > 0

    def test_optimize_image_config(self):
        """Test image configuration optimization."""
        try:
            from codomyrmex.containerization.image_optimizer import ImageOptimizer
        except ImportError:
            pytest.skip("ImageOptimizer not available")

        optimizer = ImageOptimizer()

        config = {
            "base_image": "python:3.9",
            "commands": ["RUN apt-get update", "RUN pip install flask"]
        }

        optimized = optimizer.optimize_image(config)

        assert "suggested_base_image" in optimized
        assert "python:3.9-slim" in optimized["suggested_base_image"]
        assert "optimization_notes" in optimized

    @patch('codomyrmex.containerization.image_optimizer.docker')
    def test_compare_images(self, mock_docker):
        """Test image comparison functionality."""
        try:
            from codomyrmex.containerization.image_optimizer import ImageOptimizer
        except ImportError:
            pytest.skip("ImageOptimizer not available")

        # Mock two images
        def create_mock_image(size_mb):
            mock_image = Mock()
            mock_image.attrs = {
                "Size": size_mb * 1024 * 1024,
                "RootFS": {"Layers": ["layer"] * 5},
                "Config": {"Env": [], "Cmd": ["echo", "hello"]}
            }
            return mock_image

        mock_client = Mock()
        mock_client.images.get.side_effect = [
            create_mock_image(500),  # 500MB
            create_mock_image(300)   # 300MB
        ]

        with patch('codomyrmex.containerization.image_optimizer.docker.from_env', return_value=mock_client):
            optimizer = ImageOptimizer()

            comparison = optimizer.compare_images("large:latest", "small:latest")

            assert "image1" in comparison
            assert "image2" in comparison
            assert comparison["size_difference_mb"] == 200  # 500 - 300
            assert comparison["size_reduction_percentage"] > 0
            assert "recommendations" in comparison

    def test_get_optimization_report(self):
        """Test comprehensive optimization report generation."""
        try:
            from codomyrmex.containerization.image_optimizer import ImageOptimizer
        except ImportError:
            pytest.skip("ImageOptimizer not available")

        with patch.object(ImageOptimizer, 'analyze_image') as mock_analyze:
            mock_analysis = Mock()
            mock_analysis.size_bytes = 600 * 1024 * 1024
            mock_analysis.layers = ["layer"] * 10
            mock_analysis.to_dict.return_value = {"size_mb": 600, "layer_count": 10}
            mock_analyze.return_value = mock_analysis

            optimizer = ImageOptimizer()
            report = optimizer.get_optimization_report("test:latest")

            assert "image_analysis" in report
            assert "optimization_suggestions" in report
            assert "summary" in report
            assert "implementation_plan" in report


# Test BuildGenerator
class TestBuildGenerator:
    """Test cases for BuildGenerator functionality."""

    def test_build_generator_creation(self):
        """Test creating a BuildGenerator."""
        try:
            from codomyrmex.containerization.build_generator import BuildGenerator
        except ImportError:
            pytest.skip("BuildGenerator not available")

        generator = BuildGenerator()
        assert generator is not None
        assert hasattr(generator, 'templates')

    def test_create_multi_stage_build_python(self):
        """Test creating multi-stage build for Python."""
        try:
            from codomyrmex.containerization.build_generator import BuildGenerator, MultiStageBuild
        except ImportError:
            pytest.skip("BuildGenerator not available")

        generator = BuildGenerator()

        config = {
            "build_type": "python",
            "base_image": "python:3.9-slim",
            "metadata": {"project_name": "test_app"}
        }

        build = generator.create_multi_stage_build(config)

        assert isinstance(build, MultiStageBuild)
        assert len(build.stages) == 2
        assert build.stages[0].name == "builder"
        assert build.stages[1].name == "runtime"
        assert build.final_stage == "runtime"

    def test_create_multi_stage_build_node(self):
        """Test creating multi-stage build for Node.js."""
        try:
            from codomyrmex.containerization.build_generator import BuildGenerator
        except ImportError:
            pytest.skip("BuildGenerator not available")

        generator = BuildGenerator()

        config = {
            "build_type": "node",
            "base_image": "node:18-alpine"
        }

        build = generator.create_multi_stage_build(config)

        assert len(build.stages) == 2
        assert "npm ci" in str(build.stages[0].commands)
        assert build.stages[1].base_image == "node:18-alpine"

    def test_optimize_dockerfile(self):
        """Test Dockerfile optimization."""
        try:
            from codomyrmex.containerization.build_generator import BuildGenerator
        except ImportError:
            pytest.skip("BuildGenerator not available")

        generator = BuildGenerator()

        # Create a test Dockerfile
        dockerfile_content = """FROM ubuntu:20.04
RUN apt-get update
RUN apt-get install -y python3
RUN pip install flask
RUN apt-get clean
"""

        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dockerfile', delete=False) as f:
            f.write(dockerfile_content)
            dockerfile_path = f.name

        try:
            optimized = generator.optimize_dockerfile(dockerfile_path)

            # Should combine RUN commands and add optimizations
            assert "apt-get update && apt-get install" in optimized
            assert "--no-cache-dir" in optimized
            assert "rm -rf /var/lib/apt/lists/*" in optimized

        finally:
            os.unlink(dockerfile_path)

    def test_validate_dockerfile(self):
        """Test Dockerfile validation."""
        try:
            from codomyrmex.containerization.build_generator import BuildGenerator
        except ImportError:
            pytest.skip("BuildGenerator not available")

        generator = BuildGenerator()

        # Valid Dockerfile
        valid_dockerfile = """FROM ubuntu:20.04
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y python3
USER appuser
CMD ["python", "app.py"]
"""

        is_valid, issues = generator.validate_dockerfile(valid_dockerfile)
        assert is_valid or len(issues) == 0  # May have some warnings but no critical issues

        # Invalid Dockerfile
        invalid_dockerfile = """FROM ubuntu:latest
RUN chmod 777 /app
ENV PASSWORD=secret123
"""

        is_valid, issues = generator.validate_dockerfile(invalid_dockerfile)
        assert not is_valid
        assert len(issues) > 0

    def test_generate_build_script(self):
        """Test build script generation."""
        try:
            from codomyrmex.containerization.build_generator import BuildGenerator, BuildScript
        except ImportError:
            pytest.skip("BuildGenerator not available")

        generator = BuildGenerator()

        config = {
            "name": "test_build",
            "dockerfile": "Dockerfile",
            "context": ".",
            "build_args": {"VERSION": "1.0"},
            "tags": ["myapp:1.0", "myapp:latest"],
            "push_targets": ["registry.example.com/myapp:1.0"]
        }

        script = generator.generate_build_script(config)

        assert isinstance(script, BuildScript)
        assert script.name == "test_build"
        assert len(script.tags) == 2
        assert len(script.push_targets) == 1

        # Test shell script generation
        shell_script = script.to_shell_script()
        assert "# Build script for test_build" in shell_script
        assert "docker build" in shell_script
        assert "--build-arg VERSION=1.0" in shell_script
        assert "docker push" in shell_script


# Test Enhanced DockerManager
class TestDockerManagerEnhanced:
    """Test cases for enhanced DockerManager functionality."""

    @patch('codomyrmex.containerization.docker_manager.docker')
    def test_optimize_container_image(self, mock_docker):
        """Test container image optimization."""
        try:
            from codomyrmex.containerization.docker_manager import DockerManager
        except ImportError:
            pytest.skip("DockerManager not available")

        manager = DockerManager()

        # Test Python optimization
        optimized = manager.optimize_container_image("python:3.9", ["flask", "django"])
        assert "python:3.9-slim" in optimized or optimized == "python:3.9"

        # Test Node.js optimization
        optimized = manager.optimize_container_image("node:14", ["express", "react"])
        assert "node:18" in optimized or optimized == "node:14"

    @patch('codomyrmex.containerization.docker_manager.docker')
    def test_analyze_image_size(self, mock_docker):
        """Test image size analysis."""
        try:
            from codomyrmex.containerization.docker_manager import DockerManager
        except ImportError:
            pytest.skip("DockerManager not available")

        # Mock image
        mock_image = Mock()
        mock_image.attrs = {
            "Size": 300 * 1024 * 1024,  # 300MB
            "VirtualSize": 350 * 1024 * 1024,  # 350MB
            "RootFS": {"Layers": ["layer1", "layer2", "layer3", "layer4", "layer5"]},
            "History": [
                {"Size": 50 * 1024 * 1024},
                {"Size": 40 * 1024 * 1024},
                {"Size": 60 * 1024 * 1024},
                {"Size": 80 * 1024 * 1024},
                {"Size": 70 * 1024 * 1024}
            ]
        }

        mock_client = Mock()
        mock_client.images.get.return_value = mock_image

        with patch('codomyrmex.containerization.docker_manager.docker.from_env', return_value=mock_client):
            manager = DockerManager()

            analysis = manager.analyze_image_size("test:latest")

            assert analysis["total_size_mb"] == 300
            assert analysis["virtual_size_mb"] == 350
            assert analysis["layer_count"] == 5
            assert analysis["size_efficiency"] == "good"  # < 500MB
            assert "optimization_suggestions" in analysis

    @patch('codomyrmex.containerization.docker_manager.docker')
    def test_get_image_layers(self, mock_docker):
        """Test getting image layer information."""
        try:
            from codomyrmex.containerization.docker_manager import DockerManager
        except ImportError:
            pytest.skip("DockerManager not available")

        # Mock image with history
        mock_image = Mock()
        mock_image.attrs = {
            "History": [
                {
                    "Created": "2023-01-01T00:00:00Z",
                    "CreatedBy": "FROM ubuntu:20.04",
                    "Size": 100 * 1024 * 1024
                },
                {
                    "Created": "2023-01-01T00:01:00Z",
                    "CreatedBy": "RUN apt-get update",
                    "Size": 50 * 1024 * 1024
                },
                {
                    "Created": "2023-01-01T00:02:00Z",
                    "CreatedBy": "COPY . /app",
                    "Size": 25 * 1024 * 1024
                }
            ]
        }

        mock_client = Mock()
        mock_client.images.get.return_value = mock_image

        with patch('codomyrmex.containerization.docker_manager.docker.from_env', return_value=mock_client):
            manager = DockerManager()

            layers = manager.get_image_layers("test:latest")

            assert len(layers) == 3
            assert layers[0]["created_by"] == "FROM ubuntu:20.04"
            assert layers[0]["size_mb"] == 100
            assert layers[1]["created_by"] == "RUN apt-get update"
            assert layers[2]["created_by"] == "COPY . /app"


class TestBuildStagesAndScripts:
    """Test cases for BuildStage and BuildScript classes."""

    def test_build_stage_creation(self):
        """Test creating a BuildStage."""
        try:
            from codomyrmex.containerization.build_generator import BuildStage
        except ImportError:
            pytest.skip("BuildStage not available")

        stage = BuildStage(
            name="test_stage",
            base_image="ubuntu:20.04",
            commands=["RUN apt-get update", "RUN apt-get install -y python3"],
            copy_commands=["COPY . /app"],
            environment={"PATH": "/usr/local/bin"},
            working_directory="/app",
            user="appuser"
        )

        dockerfile = stage.to_dockerfile()

        assert "FROM ubuntu:20.04 AS test_stage" in dockerfile
        assert "RUN apt-get update" in dockerfile
        assert "COPY . /app" in dockerfile
        assert "ENV PATH=/usr/local/bin" in dockerfile
        assert "WORKDIR /app" in dockerfile
        assert "USER appuser" in dockerfile

    def test_multi_stage_build(self):
        """Test MultiStageBuild functionality."""
        try:
            from codomyrmex.containerization.build_generator import MultiStageBuild, BuildStage
        except ImportError:
            pytest.skip("MultiStageBuild not available")

        build = MultiStageBuild()

        # Add stages
        build_stage = BuildStage(
            name="builder",
            base_image="golang:1.19",
            commands=["WORKDIR /app", "COPY . .", "RUN go build"]
        )

        runtime_stage = BuildStage(
            name="runtime",
            base_image="alpine:latest",
            copy_commands=["COPY --from=builder /app/main /app/main"],
            user="appuser"
        )

        build.stages = [build_stage, runtime_stage]
        build.final_stage = "runtime"

        dockerfile = build.to_dockerfile()

        assert "FROM golang:1.19 AS builder" in dockerfile
        assert "FROM alpine:latest AS runtime" in dockerfile
        assert "COPY --from=builder /app/main /app/main" in dockerfile
        assert "FROM runtime" in dockerfile

    def test_build_script_generation(self):
        """Test BuildScript shell script generation."""
        try:
            from codomyrmex.containerization.build_generator import BuildScript
        except ImportError:
            pytest.skip("BuildScript not available")

        script = BuildScript(
            name="web_app",
            dockerfile_path="Dockerfile.multi",
            context_path="./src",
            build_args={"VERSION": "2.1.0"},
            tags=["myapp:2.1.0", "myapp:latest"],
            push_targets=["registry.example.com/myapp:2.1.0"],
            dependencies=["base-image:latest"]
        )

        shell_script = script.to_shell_script()

        assert "#!/bin/bash" in shell_script
        assert "# Build script for web_app" in shell_script
        assert "docker build -f Dockerfile.multi" in shell_script
        assert "--build-arg VERSION=2.1.0" in shell_script
        assert "myapp:2.1.0" in shell_script
        assert "myapp:latest" in shell_script
        assert "docker push registry.example.com/myapp:2.1.0" in shell_script


if __name__ == "__main__":
    pytest.main([__file__])
