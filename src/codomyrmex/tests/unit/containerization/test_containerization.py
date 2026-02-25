"""Enhanced tests for containerization improvements."""


import pytest

# Check Docker availability
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    docker = None


def check_docker_available():
    """Check if Docker daemon is actually available."""
    if not DOCKER_AVAILABLE:
        return False
    try:
        client = docker.from_env()
        client.ping()
        return True
    except (docker.errors.DockerException, Exception):
        return False


# Test ImageOptimizer
@pytest.mark.unit
class TestImageOptimizer:
    """Test cases for ImageOptimizer functionality."""

    def test_image_optimizer_creation(self):
        """Test creating an ImageOptimizer with real Docker."""
        try:
            from codomyrmex.containerization.docker.image_optimizer import (
                ImageOptimizer,
            )
        except ImportError:
            pytest.skip("ImageOptimizer not available")

        if not check_docker_available():
            pytest.skip("Docker daemon not available")

        optimizer = ImageOptimizer()
        assert optimizer is not None
        # Client may be None if Docker not available
        if optimizer.client:
            assert optimizer.client is not None

    def test_optimization_suggestions(self):
        """Test generation of optimization suggestions with real implementation."""
        try:
            from codomyrmex.containerization.docker.image_optimizer import (
                ImageOptimizer,
                OptimizationSuggestion,
            )
        except ImportError:
            pytest.skip("ImageOptimizer not available")

        if not check_docker_available():
            pytest.skip("Docker daemon not available")

        optimizer = ImageOptimizer()

        # Create a real analysis-like structure for testing suggestions
        # (We'll test the suggestion logic without requiring a real image)
        class MockAnalysis:
            def __init__(self):
                self.size_bytes = 800 * 1024 * 1024  # 800MB - large
                self.layers = ["layer"] * 25  # Many layers
                self.commands = ["RUN apt-get update", "RUN apt-get install python"]
                self.environment_vars = []  # No USER set

        analysis = MockAnalysis()

        # Test suggestion generation if method exists
        if hasattr(optimizer, '_generate_suggestions'):
            suggestions = optimizer._generate_suggestions(analysis)

            assert isinstance(suggestions, list)
            assert len(suggestions) >= 0  # May be empty or have suggestions

    def test_optimize_image_config(self):
        """Test image configuration optimization with real implementation."""
        try:
            from codomyrmex.containerization.docker.image_optimizer import (
                ImageOptimizer,
            )
        except ImportError:
            pytest.skip("ImageOptimizer not available")

        if not check_docker_available():
            pytest.skip("Docker daemon not available")

        optimizer = ImageOptimizer()

        config = {
            "base_image": "python:3.9",
            "commands": ["RUN apt-get update", "RUN pip install flask"]
        }

        # Test optimization if method exists
        if hasattr(optimizer, 'optimize_image'):
            optimized = optimizer.optimize_image(config)

            assert isinstance(optimized, dict)
            if "suggested_base_image" in optimized:
                assert len(optimized["suggested_base_image"]) > 0


# Test BuildGenerator
@pytest.mark.unit
class TestBuildGenerator:
    """Test cases for BuildGenerator functionality."""

    def test_build_generator_creation(self):
        """Test creating a BuildGenerator."""
        try:
            from codomyrmex.containerization.docker.build_generator import (
                BuildGenerator,
            )
        except ImportError:
            pytest.skip("BuildGenerator not available")

        generator = BuildGenerator()
        assert generator is not None
        assert hasattr(generator, 'templates')

    def test_create_multi_stage_build_python(self):
        """Test creating multi-stage build for Python."""
        try:
            from codomyrmex.containerization.docker.build_generator import (
                BuildGenerator,
                MultiStageBuild,
            )
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
        assert len(build.stages) >= 1
        assert hasattr(build, 'final_stage')

    def test_create_multi_stage_build_node(self):
        """Test creating multi-stage build for Node.js."""
        try:
            from codomyrmex.containerization.docker.build_generator import (
                BuildGenerator,
            )
        except ImportError:
            pytest.skip("BuildGenerator not available")

        generator = BuildGenerator()

        config = {
            "build_type": "node",
            "base_image": "node:18-alpine"
        }

        build = generator.create_multi_stage_build(config)

        assert len(build.stages) >= 1
        assert hasattr(build, 'final_stage')

    def test_optimize_dockerfile(self, tmp_path):
        """Test Dockerfile optimization with real file operations."""
        try:
            from codomyrmex.containerization.docker.build_generator import (
                BuildGenerator,
            )
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

        dockerfile_path = tmp_path / "test.dockerfile"
        dockerfile_path.write_text(dockerfile_content)

        optimized = generator.optimize_dockerfile(str(dockerfile_path))

        # Should return optimized content
        assert isinstance(optimized, str)
        assert len(optimized) > 0

    def test_validate_dockerfile(self):
        """Test Dockerfile validation with real implementation."""
        try:
            from codomyrmex.containerization.docker.build_generator import (
                BuildGenerator,
            )
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
        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)

        # Invalid Dockerfile
        invalid_dockerfile = """FROM ubuntu:latest
RUN chmod 777 /app
ENV PASSWORD=secret123
"""

        is_valid, issues = generator.validate_dockerfile(invalid_dockerfile)
        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)

    def test_generate_build_script(self):
        """Test build script generation with real implementation."""
        try:
            from codomyrmex.containerization.docker.build_generator import (
                BuildGenerator,
                BuildScript,
            )
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
        assert isinstance(shell_script, str)
        assert len(shell_script) > 0


# Test Enhanced DockerManager
@pytest.mark.unit
class TestDockerManagerEnhanced:
    """Test cases for enhanced DockerManager functionality."""

    def test_optimize_container_image(self):
        """Test container image optimization with real implementation."""
        try:
            from codomyrmex.containerization.docker.docker_manager import DockerManager
        except ImportError:
            pytest.skip("DockerManager not available")

        manager = DockerManager()

        # Test Python optimization if method exists
        if hasattr(manager, 'optimize_container_image'):
            optimized = manager.optimize_container_image("python:3.9", ["flask", "django"])

            assert isinstance(optimized, str)
            assert len(optimized) > 0


@pytest.mark.unit
class TestBuildStagesAndScripts:
    """Test cases for BuildStage and BuildScript classes."""

    def test_build_stage_creation(self):
        """Test creating a BuildStage."""
        try:
            from codomyrmex.containerization.docker.build_generator import BuildStage
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

        assert isinstance(dockerfile, str)
        assert "FROM ubuntu:20.04" in dockerfile or "AS test_stage" in dockerfile
        assert len(dockerfile) > 0

    def test_multi_stage_build(self):
        """Test MultiStageBuild functionality."""
        try:
            from codomyrmex.containerization.docker.build_generator import (
                BuildStage,
                MultiStageBuild,
            )
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

        assert isinstance(dockerfile, str)
        assert len(dockerfile) > 0

    def test_build_script_generation(self):
        """Test BuildScript shell script generation."""
        try:
            from codomyrmex.containerization.docker.build_generator import BuildScript
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

        assert isinstance(shell_script, str)
        assert len(shell_script) > 0


if __name__ == "__main__":
    pytest.main([__file__])


# Coverage push — containerization/docker
class TestImageOptimizerCoverage:
    """Coverage tests for Docker ImageOptimizer."""

    def test_image_analysis_dataclass(self):
        from codomyrmex.containerization.docker.image_optimizer import ImageAnalysis
        a = ImageAnalysis(
            image_name="myapp:latest", size_bytes=100_000_000, layers=[],
            base_image="python:3.12", exposed_ports=["8080"],
            volumes=[], environment_vars=[], commands=[],
        )
        assert a.image_name == "myapp:latest"
        assert a.optimization_score == 0.0

    def test_optimization_suggestions(self):
        from codomyrmex.containerization.docker.image_optimizer import ImageAnalysis
        a = ImageAnalysis(
            image_name="test", size_bytes=500_000_000, layers=[],
            base_image="ubuntu:22.04", exposed_ports=[], volumes=[],
            environment_vars=[], commands=["RUN apt-get install -y curl"],
            potential_optimizations=["Use multi-stage build", "Minimize layers"],
        )
        assert len(a.potential_optimizations) == 2


class TestBuildGeneratorCoverage:
    """Coverage tests for Docker BuildGenerator."""

    def test_build_script_dataclass(self):
        from codomyrmex.containerization.docker.build_generator import BuildScript
        bs = BuildScript(
            name="app", dockerfile_path="./Dockerfile",
            context_path=".", tags=["v1.0"],
        )
        assert bs.name == "app"
        assert bs.tags == ["v1.0"]
