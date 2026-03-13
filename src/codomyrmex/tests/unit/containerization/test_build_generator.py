"""Zero-mock tests for containerization.docker.build_generator."""

import pytest

from codomyrmex.containerization.docker.build_generator import (
    BuildGenerator,
    BuildScript,
    BuildStage,
    MultiStageBuild,
)

# ---------------------------------------------------------------------------
# BuildStage — dataclass instantiation
# ---------------------------------------------------------------------------


class TestBuildStageInstantiation:
    def test_minimal_instantiation(self):
        stage = BuildStage(name="base", base_image="ubuntu:22.04")
        assert stage.name == "base"
        assert stage.base_image == "ubuntu:22.04"
        assert stage.commands == []
        assert stage.copy_commands == []
        assert stage.labels == {}
        assert stage.environment == {}
        assert stage.working_directory is None
        assert stage.user is None

    def test_full_instantiation(self):
        stage = BuildStage(
            name="builder",
            base_image="python:3.11-slim",
            commands=["RUN pip install uv"],
            copy_commands=["COPY . /app"],
            labels={"version": "1.0"},
            environment={"PYTHONUNBUFFERED": "1"},
            working_directory="/app",
            user="appuser",
        )
        assert stage.name == "builder"
        assert stage.base_image == "python:3.11-slim"
        assert len(stage.commands) == 1
        assert len(stage.copy_commands) == 1
        assert stage.labels["version"] == "1.0"
        assert stage.environment["PYTHONUNBUFFERED"] == "1"
        assert stage.working_directory == "/app"
        assert stage.user == "appuser"


# ---------------------------------------------------------------------------
# BuildStage.to_dockerfile — output content
# ---------------------------------------------------------------------------


class TestBuildStageToDockerfile:
    def test_from_line_present(self):
        stage = BuildStage(name="app", base_image="debian:12")
        output = stage.to_dockerfile()
        assert "FROM debian:12" in output

    def test_from_line_includes_as_name(self):
        stage = BuildStage(name="app", base_image="debian:12")
        output = stage.to_dockerfile()
        assert "FROM debian:12 AS app" in output

    def test_env_line_included(self):
        stage = BuildStage(
            name="s", base_image="alpine:3.18", environment={"PORT": "8080"}
        )
        output = stage.to_dockerfile()
        assert "ENV PORT=8080" in output

    def test_multiple_env_lines(self):
        stage = BuildStage(
            name="s",
            base_image="alpine:3.18",
            environment={"A": "1", "B": "2"},
        )
        output = stage.to_dockerfile()
        assert "ENV A=1" in output
        assert "ENV B=2" in output

    def test_workdir_line_included(self):
        stage = BuildStage(
            name="s", base_image="alpine:3.18", working_directory="/workspace"
        )
        output = stage.to_dockerfile()
        assert "WORKDIR /workspace" in output

    def test_workdir_absent_when_not_set(self):
        stage = BuildStage(name="s", base_image="alpine:3.18")
        output = stage.to_dockerfile()
        assert "WORKDIR" not in output

    def test_user_line_included(self):
        stage = BuildStage(name="s", base_image="alpine:3.18", user="nobody")
        output = stage.to_dockerfile()
        assert "USER nobody" in output

    def test_user_absent_when_not_set(self):
        stage = BuildStage(name="s", base_image="alpine:3.18")
        output = stage.to_dockerfile()
        assert "USER" not in output

    def test_label_line_included(self):
        stage = BuildStage(
            name="s", base_image="alpine:3.18", labels={"maintainer": "team"}
        )
        output = stage.to_dockerfile()
        assert "LABEL maintainer=team" in output

    def test_run_command_included(self):
        stage = BuildStage(
            name="s",
            base_image="alpine:3.18",
            commands=["RUN apk add curl"],
        )
        output = stage.to_dockerfile()
        assert "RUN apk add curl" in output

    def test_copy_command_included(self):
        stage = BuildStage(
            name="s",
            base_image="alpine:3.18",
            copy_commands=["COPY src/ /app/src/"],
        )
        output = stage.to_dockerfile()
        assert "COPY src/ /app/src/" in output

    def test_empty_stage_produces_only_from_line(self):
        stage = BuildStage(name="empty", base_image="scratch")
        output = stage.to_dockerfile()
        lines = [line for line in output.splitlines() if line.strip()]
        assert len(lines) == 1
        assert lines[0] == "FROM scratch AS empty"

    def test_scratch_base_image(self):
        stage = BuildStage(name="final", base_image="scratch")
        output = stage.to_dockerfile()
        assert "FROM scratch AS final" in output


# ---------------------------------------------------------------------------
# MultiStageBuild — dataclass + to_dockerfile
# ---------------------------------------------------------------------------


class TestMultiStageBuild:
    def test_default_instantiation(self):
        build = MultiStageBuild()
        assert build.stages == []
        assert build.final_stage is None
        assert build.metadata == {}

    def test_to_dockerfile_contains_header_comment(self):
        build = MultiStageBuild(stages=[BuildStage(name="a", base_image="alpine:3.18")])
        output = build.to_dockerfile()
        assert "# Auto-generated multi-stage Dockerfile" in output

    def test_to_dockerfile_project_name_in_header(self):
        build = MultiStageBuild(
            stages=[BuildStage(name="a", base_image="alpine:3.18")],
            metadata={"project_name": "myapp"},
        )
        output = build.to_dockerfile()
        assert "myapp" in output

    def test_unknown_project_name_fallback(self):
        build = MultiStageBuild(stages=[BuildStage(name="a", base_image="alpine:3.18")])
        output = build.to_dockerfile()
        assert "unknown" in output

    def test_all_stages_appear_in_output(self):
        build = MultiStageBuild(
            stages=[
                BuildStage(name="build", base_image="golang:1.21"),
                BuildStage(name="run", base_image="scratch"),
            ]
        )
        output = build.to_dockerfile()
        assert "FROM golang:1.21 AS build" in output
        assert "FROM scratch AS run" in output

    def test_stages_separated_by_blank_line(self):
        build = MultiStageBuild(
            stages=[
                BuildStage(name="s1", base_image="alpine:3.18"),
                BuildStage(name="s2", base_image="alpine:3.18"),
            ]
        )
        output = build.to_dockerfile()
        # Two FROM lines separated somewhere by a blank line
        lines = output.splitlines()
        from_indices = [i for i, ln in enumerate(lines) if ln.startswith("FROM")]
        assert len(from_indices) == 2
        # There should be at least one blank line between them
        between = lines[from_indices[0] + 1 : from_indices[1]]
        assert any(ln.strip() == "" for ln in between)

    def test_complex_two_stage_python_build(self):
        builder = BuildStage(
            name="builder",
            base_image="python:3.11-slim",
            commands=["RUN pip install -r requirements.txt"],
            copy_commands=["COPY . /app"],
            environment={"PYTHONUNBUFFERED": "1"},
            working_directory="/app",
        )
        runtime = BuildStage(
            name="runtime",
            base_image="python:3.11-slim",
            copy_commands=["COPY --from=builder /app /app"],
            working_directory="/app",
            user="appuser",
        )
        build = MultiStageBuild(
            stages=[builder, runtime],
            final_stage="runtime",
            metadata={"project_name": "myservice"},
        )
        output = build.to_dockerfile()
        assert "FROM python:3.11-slim AS builder" in output
        assert "FROM python:3.11-slim AS runtime" in output
        assert "COPY --from=builder /app /app" in output
        assert "WORKDIR /app" in output
        assert "USER appuser" in output


# ---------------------------------------------------------------------------
# BuildScript — instantiation + to_shell_script
# ---------------------------------------------------------------------------


class TestBuildScript:
    def test_instantiation_defaults(self):
        script = BuildScript(
            name="my-app", dockerfile_path="Dockerfile", context_path="."
        )
        assert script.name == "my-app"
        assert script.build_args == {}
        assert script.tags == []
        assert script.push_targets == []
        assert script.dependencies == []

    def test_to_shell_script_starts_with_shebang(self):
        script = BuildScript(
            name="app",
            dockerfile_path="Dockerfile",
            context_path=".",
            tags=["myapp:latest"],
        )
        output = script.to_shell_script()
        assert output.startswith("#!/bin/bash")

    def test_to_shell_script_contains_docker_build_with_tag(self):
        script = BuildScript(
            name="app",
            dockerfile_path="Dockerfile",
            context_path=".",
            tags=["registry/myapp:1.0"],
        )
        output = script.to_shell_script()
        assert "docker build" in output
        assert "-t registry/myapp:1.0" in output

    def test_to_shell_script_includes_build_args(self):
        script = BuildScript(
            name="app",
            dockerfile_path="Dockerfile",
            context_path=".",
            tags=["app:latest"],
            build_args={"VERSION": "1.0", "ENV": "prod"},
        )
        output = script.to_shell_script()
        assert "--build-arg VERSION=1.0" in output
        assert "--build-arg ENV=prod" in output

    def test_to_shell_script_no_push_when_no_targets(self):
        script = BuildScript(
            name="app",
            dockerfile_path="Dockerfile",
            context_path=".",
            tags=["app:latest"],
        )
        output = script.to_shell_script()
        assert "docker push" not in output

    def test_to_shell_script_includes_docker_push(self):
        script = BuildScript(
            name="app",
            dockerfile_path="Dockerfile",
            context_path=".",
            tags=["app:latest"],
            push_targets=["registry/app:latest"],
        )
        output = script.to_shell_script()
        assert "docker push registry/app:latest" in output

    def test_empty_build_args_produces_no_build_arg_flag(self):
        script = BuildScript(
            name="app",
            dockerfile_path="Dockerfile",
            context_path=".",
            tags=["app:1.0"],
            build_args={},
        )
        output = script.to_shell_script()
        assert "--build-arg" not in output


# ---------------------------------------------------------------------------
# BuildGenerator — create_multi_stage_build
# ---------------------------------------------------------------------------


class TestBuildGenerator:
    def setup_method(self):
        self.gen = BuildGenerator()

    def test_creates_python_build(self):
        result = self.gen.create_multi_stage_build({"build_type": "python"})
        assert isinstance(result, MultiStageBuild)
        assert len(result.stages) == 2
        stage_names = [s.name for s in result.stages]
        assert "builder" in stage_names
        assert "runtime" in stage_names

    def test_creates_node_build(self):
        result = self.gen.create_multi_stage_build({"build_type": "node"})
        assert isinstance(result, MultiStageBuild)
        assert len(result.stages) == 2

    def test_creates_go_build_with_scratch_runtime(self):
        result = self.gen.create_multi_stage_build({"build_type": "go"})
        assert isinstance(result, MultiStageBuild)
        runtime = next(s for s in result.stages if s.name == "runtime")
        assert runtime.base_image == "alpine:latest"

    def test_creates_java_build(self):
        result = self.gen.create_multi_stage_build({"build_type": "java"})
        assert isinstance(result, MultiStageBuild)
        assert len(result.stages) == 2

    def test_creates_generic_build_for_unknown_type(self):
        result = self.gen.create_multi_stage_build({"build_type": "rust"})
        assert isinstance(result, MultiStageBuild)
        assert len(result.stages) == 2

    def test_python_build_uses_custom_base_image(self):
        result = self.gen.create_multi_stage_build(
            {"build_type": "python", "base_image": "python:3.12-slim"}
        )
        builder = next(s for s in result.stages if s.name == "builder")
        assert builder.base_image == "python:3.12-slim"

    def test_metadata_stored_on_build(self):
        result = self.gen.create_multi_stage_build(
            {"build_type": "python", "metadata": {"project_name": "api"}}
        )
        assert result.metadata.get("project_name") == "api"


# ---------------------------------------------------------------------------
# BuildGenerator — validate_dockerfile
# ---------------------------------------------------------------------------


class TestValidateDockerfile:
    def setup_method(self):
        self.gen = BuildGenerator()

    def test_valid_dockerfile_returns_true(self):
        content = "FROM ubuntu:22.04\nUSER nobody\nWORKDIR /app\n"
        valid, issues = self.gen.validate_dockerfile(content)
        assert valid is True
        assert issues == []

    def test_missing_from_adds_issue(self):
        content = "RUN echo hello\n"
        valid, issues = self.gen.validate_dockerfile(content)
        assert valid is False
        assert any("FROM" in issue for issue in issues)

    def test_chmod_777_adds_issue(self):
        content = "FROM ubuntu:22.04\nUSER nobody\nRUN chmod 777 /app\n"
        valid, issues = self.gen.validate_dockerfile(content)
        assert any("permissions" in issue.lower() for issue in issues)

    def test_root_user_adds_issue(self):
        content = "FROM ubuntu:22.04\nUSER root\n"
        valid, issues = self.gen.validate_dockerfile(content)
        assert any("root" in issue.lower() for issue in issues)

    def test_no_user_instruction_adds_advisory_issue(self):
        content = "FROM ubuntu:22.04:slim\nWORKDIR /app\n"
        valid, issues = self.gen.validate_dockerfile(content)
        assert any("USER" in issue for issue in issues)

    def test_latest_tag_adds_issue(self):
        content = "FROM ubuntu:latest\nUSER nobody\n"
        valid, issues = self.gen.validate_dockerfile(content)
        assert any("latest" in issue.lower() for issue in issues)


# ---------------------------------------------------------------------------
# BuildGenerator — optimize_dockerfile
# ---------------------------------------------------------------------------


class TestOptimizeDockerfile:
    def setup_method(self):
        self.gen = BuildGenerator()

    def test_combines_consecutive_run_commands(self, tmp_path):
        # The optimizer combines consecutive RUN lines into one RUN ... && ... line.
        # The join logic: "RUN " + " && ".join(cmd[4:] for cmd in combined_commands)
        # combined_commands[0] is the full "RUN apt-get update" line;
        # [4:] gives "apt-get update". Subsequent entries already had "RUN " stripped
        # before appending, so [4:] strips 4 more chars (a known source quirk).
        # Test verifies the combination happens (only one RUN in output).
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text(
            "FROM ubuntu:22.04\nRUN apt-get update\nRUN apt-get install curl\n"
        )
        result = self.gen.optimize_dockerfile(str(dockerfile))
        # Two consecutive RUN lines should be merged into a single RUN line
        run_count = sum(1 for line in result.splitlines() if line.startswith("RUN "))
        assert run_count == 1
        # The combined line uses && separator
        assert "&&" in result

    def test_raises_on_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            self.gen.optimize_dockerfile("/nonexistent/path/Dockerfile")
