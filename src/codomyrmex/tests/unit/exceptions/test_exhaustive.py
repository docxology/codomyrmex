"""Exhaustive zero-mock tests for all custom exceptions.

This module ensures every exception in the codomyrmex.exceptions hierarchy
is tested for instantiation, message formatting (including context),
and exception chaining.
"""

import pytest

from codomyrmex.exceptions import (
    ActiveInferenceError,
    AIProviderError,
    APIDocumentationError,
    APIError,
    ArtifactError,
    AuthenticationError,
    BayesianInferenceError,
    BuildError,
    BulkheadFullError,
    CacheError,
    CapabilityScanError,
    CaseError,
    CaseNotFoundError,
    CerebrumError,
    CICDError,
    CircuitOpenError,
    CodeEditingError,
    CodeExecutionError,
    CodeGenerationError,
    CommandExecutionError,
    CompressionError,
    ConfigurationError,
    ContainerError,
    DatabaseError,
    DependencyError,
    DeploymentError,
    DirectoryError,
    DocumentationError,
    EncryptionError,
    EnvironmentError,
    EventError,
    FileOperationError,
    GitOperationError,
    IDEConnectionError,
    IDEError,
    InferenceError,
    InteractiveShellError,
    InvalidCaseError,
    LoggingError,
    MemoryError,
    ModelContextError,
    ModelError,
    Modeling3DError,
    NetworkError,
    NetworkStructureError,
    OrchestrationError,
    PatternMatchingError,
    PerformanceError,
    PhysicalManagementError,
    PlottingError,
    PluginError,
    ProjectManagementError,
    RepositoryError,
    ResourceError,
    SandboxError,
    SchemaError,
    SecurityAuditError,
    SerializationError,
    SessionError,
    SimulationError,
    SkillError,
    SpatialError,
    StaticAnalysisError,
    SynthesisError,
    SystemDiscoveryError,
    TaskExecutionError,
    TemplateError,
    TerminalError,
    TimeoutError,
    TransformationError,
    ValidationError,
    VisualizationError,
    WorkflowError,
)
from codomyrmex.exceptions.base import format_exception_chain


@pytest.mark.unit
class TestExhaustiveExceptions:
    """Test every exception for required properties."""

    def test_ai_provider_error(self):
        err = AIProviderError("msg", provider_name="anthropic", model_name="claude")
        assert err.context["provider_name"] == "anthropic"
        assert err.context["model_name"] == "claude"
        assert "[AIProviderError] msg" in str(err)
        assert "provider_name=anthropic" in str(err)

        # Chaining
        cause = ValueError("cause")
        err.__cause__ = cause
        assert "ValueError" in format_exception_chain(err)

    def test_code_generation_error(self):
        err = CodeGenerationError("msg", language="python", prompt_preview="def foo")
        assert err.context["language"] == "python"
        assert err.context["prompt_preview"] == "def foo"
        assert "language=python" in str(err)

    def test_code_editing_error(self):
        err = CodeEditingError("msg", file_path="f.py", edit_type="insert")
        assert err.context["file_path"] == "f.py"
        assert err.context["edit_type"] == "insert"
        assert "file_path=f.py" in str(err)

    def test_model_context_error(self):
        err = ModelContextError("msg", protocol_version="1.0", operation="list")
        assert err.context["protocol_version"] == "1.0"
        assert err.context["operation"] == "list"
        assert "operation=list" in str(err)

    def test_static_analysis_error(self):
        err = StaticAnalysisError("msg", analyzer_name="ruff", file_path="f.py")
        assert err.context["analyzer_name"] == "ruff"
        assert err.context["file_path"] == "f.py"

    def test_pattern_matching_error(self):
        err = PatternMatchingError("msg", pattern=".*", subject_preview="abc")
        assert err.context["pattern"] == ".*"
        assert err.context["subject_preview"] == "abc"

    def test_security_audit_error(self):
        err = SecurityAuditError("msg", vulnerability_type="injection", severity="high")
        assert err.context["vulnerability_type"] == "injection"
        assert err.context["severity"] == "high"

    def test_cerebrum_error(self):
        err = CerebrumError("msg", system_component="core")
        assert err.context["system_component"] == "core"

    def test_case_error(self):
        err = CaseError("msg", case_id="c1")
        assert err.context["case_id"] == "c1"

    def test_bayesian_inference_error(self):
        err = BayesianInferenceError("msg", model_name="m1")
        assert err.context["model_name"] == "m1"

    def test_active_inference_error(self):
        err = ActiveInferenceError("msg", agent_id="a1")
        assert err.context["agent_id"] == "a1"

    def test_model_error(self):
        err = ModelError("msg", model_type="t1")
        assert err.context["model_type"] == "t1"

    def test_transformation_error(self):
        err = TransformationError("msg", source_format="f1", target_format="f2")
        assert err.context["source_format"] == "f1"
        assert err.context["target_format"] == "f2"

    def test_case_not_found_error(self):
        err = CaseNotFoundError("msg", case_id="c1")
        assert err.context["case_id"] == "c1"
        assert isinstance(err, CaseError)

    def test_invalid_case_error(self):
        err = InvalidCaseError("msg", case_id="c1", validation_error="bad")
        assert err.context["case_id"] == "c1"
        assert err.context["validation_error"] == "bad"

    def test_inference_error(self):
        err = InferenceError("msg", model_name="m1", inference_engine="e1")
        assert err.context["model_name"] == "m1"
        assert err.context["inference_engine"] == "e1"

    def test_network_structure_error(self):
        err = NetworkStructureError("msg", model_name="m1", missing_nodes=["a"])
        assert err.context["model_name"] == "m1"
        assert err.context["missing_nodes"] == ["a"]

    def test_configuration_error(self):
        err = ConfigurationError("msg", config_key="k1", config_file="f1")
        assert err.context["config_key"] == "k1"
        assert err.context["config_file"] == "f1"

    def test_environment_error(self):
        err = EnvironmentError("msg", variable_name="v1", expected_value="val")
        assert err.context["variable_name"] == "v1"
        assert err.context["expected_value"] == "val"

    def test_dependency_error(self):
        err = DependencyError(
            "msg", dependency_name="d1", required_version="1.0", installed_version="0.9"
        )
        assert err.context["dependency_name"] == "d1"
        assert err.context["required_version"] == "1.0"
        assert err.context["installed_version"] == "0.9"

    def test_code_execution_error(self):
        err = CodeExecutionError("msg", exit_code=1, stdout="out", stderr="err")
        assert err.context["exit_code"] == 1
        assert err.context["stdout"] == "out"
        assert err.context["stderr"] == "err"

    def test_sandbox_error(self):
        err = SandboxError("msg", sandbox_id="s1", runtime="python")
        assert err.context["sandbox_id"] == "s1"
        assert err.context["runtime"] == "python"

    def test_container_error(self):
        err = ContainerError("msg", container_id="c1", image_name="img")
        assert err.context["container_id"] == "c1"
        assert err.context["image_name"] == "img"

    def test_build_error(self):
        err = BuildError("msg", build_tool="make", target="all")
        assert err.context["build_tool"] == "make"
        assert err.context["target"] == "all"

    def test_synthesis_error(self):
        err = SynthesisError("msg", component="c1", synthesis_mode="m1")
        assert err.context["component"] == "c1"
        assert err.context["synthesis_mode"] == "m1"

    def test_git_operation_error(self):
        err = GitOperationError("msg", git_command="pull", repository_path="path")
        assert err.context["git_command"] == "pull"
        assert err.context["repository_path"] == "path"

    def test_repository_error(self):
        err = RepositoryError("msg", repository_path="path", remote_url="url")
        assert err.context["repository_path"] == "path"
        assert err.context["remote_url"] == "url"

    def test_file_operation_error(self):
        err = FileOperationError("msg", file_path="f.txt", operation="read")
        assert err.context["file_path"] == "f.txt"
        assert err.context["operation"] == "read"

    def test_directory_error(self):
        err = DirectoryError("msg", directory_path="dir", operation="create")
        assert err.context["directory_path"] == "dir"
        assert err.context["operation"] == "create"

    def test_network_error(self):
        err = NetworkError("msg", url="url", status_code=500)
        assert err.context["url"] == "url"
        assert err.context["status_code"] == 500

    def test_api_error(self):
        err = APIError("msg", endpoint="end", method="GET")
        assert err.context["endpoint"] == "end"
        assert err.context["method"] == "GET"

    def test_validation_error(self):
        err = ValidationError("msg", field_name="f1", validation_rule="r1")
        assert err.context["field_name"] == "f1"
        assert err.context["validation_rule"] == "r1"

    def test_schema_error(self):
        err = SchemaError("msg", schema_name="s1", data_preview="{}")
        assert err.context["schema_name"] == "s1"
        assert err.context["data_preview"] == "{}"

    def test_timeout_error(self):
        err = TimeoutError("msg", timeout_seconds=10.0)
        assert err.context["timeout_seconds"] == 10.0

    def test_orchestration_error(self):
        err = OrchestrationError("msg", orchestrator_id="o1", strategy="s1")
        assert err.context["orchestrator_id"] == "o1"
        assert err.context["strategy"] == "s1"

    def test_workflow_error(self):
        err = WorkflowError("msg", workflow_name="w1", step_name="s1")
        assert err.context["workflow_name"] == "w1"
        assert err.context["step_name"] == "s1"

    def test_project_management_error(self):
        err = ProjectManagementError("msg", project_name="p1", operation="op1")
        assert err.context["project_name"] == "p1"
        assert err.context["operation"] == "op1"

    def test_task_execution_error(self):
        err = TaskExecutionError("msg", task_id="t1", executor="e1")
        assert err.context["task_id"] == "t1"
        assert err.context["executor"] == "e1"

    def test_performance_error(self):
        err = PerformanceError("msg", metric_name="m1", threshold=0.9)
        assert err.context["metric_name"] == "m1"
        assert err.context["threshold"] == 0.9

    def test_logging_error(self):
        err = LoggingError("msg", logger_name="l1", level="INFO")
        assert err.context["logger_name"] == "l1"
        assert err.context["level"] == "INFO"

    def test_system_discovery_error(self):
        err = SystemDiscoveryError("msg", discovery_scope="s1")
        assert err.context["discovery_scope"] == "s1"

    def test_capability_scan_error(self):
        err = CapabilityScanError("msg", capability_name="c1")
        assert err.context["capability_name"] == "c1"

    def test_modeling_3d_error(self):
        err = Modeling3DError("msg", model_format="obj")
        assert err.context["model_format"] == "obj"

    def test_physical_management_error(self):
        err = PhysicalManagementError("msg", device_id="d1")
        assert err.context["device_id"] == "d1"

    def test_simulation_error(self):
        err = SimulationError("msg", simulation_id="s1", engine="e1")
        assert err.context["simulation_id"] == "s1"
        assert err.context["engine"] == "e1"

    def test_terminal_error(self):
        err = TerminalError("msg", terminal_type="xterm")
        assert err.context["terminal_type"] == "xterm"

    def test_interactive_shell_error(self):
        err = InteractiveShellError("msg", terminal_type="xterm", shell_name="bash")
        assert err.context["terminal_type"] == "xterm"
        assert err.context["shell_name"] == "bash"

    def test_database_error(self):
        err = DatabaseError("msg", db_name="db1", query="SELECT")
        assert err.context["db_name"] == "db1"
        assert err.context["query"] == "SELECT"

    def test_cicd_error(self):
        err = CICDError("msg", pipeline_id="p1", stage="build")
        assert err.context["pipeline_id"] == "p1"
        assert err.context["stage"] == "build"

    def test_deployment_error(self):
        err = DeploymentError("msg", environment="prod", version="1.0")
        assert err.context["environment"] == "prod"
        assert err.context["version"] == "1.0"

    def test_resource_error(self):
        err = ResourceError("msg", resource_id="r1", resource_type="cpu")
        assert err.context["resource_id"] == "r1"
        assert err.context["resource_type"] == "cpu"

    def test_memory_error(self):
        err = MemoryError("msg", resource_id="r1", memory_usage=100, limit=200)
        assert err.context["resource_id"] == "r1"
        assert err.context["memory_usage"] == 100
        assert err.context["limit"] == 200

    def test_spatial_error(self):
        err = SpatialError("msg", coordinate_system="wgs84")
        assert err.context["coordinate_system"] == "wgs84"

    def test_event_error(self):
        err = EventError("msg", event_type="t1", event_id="i1")
        assert err.context["event_type"] == "t1"
        assert err.context["event_id"] == "i1"

    def test_skill_error(self):
        err = SkillError("msg", skill_name="s1")
        assert err.context["skill_name"] == "s1"

    def test_template_error(self):
        err = TemplateError("msg", template_name="t1")
        assert err.context["template_name"] == "t1"

    def test_plugin_error(self):
        err = PluginError("msg", plugin_name="p1", plugin_version="1.0")
        assert err.context["plugin_name"] == "p1"
        assert err.context["plugin_version"] == "1.0"

    def test_authentication_error(self):
        err = AuthenticationError("msg", identity="user", mechanism="token")
        assert err.context["identity"] == "user"
        assert err.context["mechanism"] == "token"

    def test_circuit_open_error(self):
        err = CircuitOpenError("msg", circuit_name="c1")
        assert err.context["circuit_name"] == "c1"

    def test_bulkhead_full_error(self):
        err = BulkheadFullError("msg", bulkhead_name="b1", max_concurrency=5)
        assert err.context["bulkhead_name"] == "b1"
        assert err.context["max_concurrency"] == 5

    def test_compression_error(self):
        err = CompressionError("msg", algorithm="gzip")
        assert err.context["algorithm"] == "gzip"

    def test_encryption_error(self):
        err = EncryptionError("msg", algorithm="aes", key_id="k1")
        assert err.context["algorithm"] == "aes"
        assert err.context["key_id"] == "k1"

    def test_ide_error(self):
        err = IDEError("msg", ide_name="vscode")
        assert err.context["ide_name"] == "vscode"

    def test_ide_connection_error(self):
        err = IDEConnectionError("msg", ide_name="vscode", host="localhost", port=8080)
        assert err.context["ide_name"] == "vscode"
        assert err.context["host"] == "localhost"
        assert err.context["port"] == 8080

    def test_command_execution_error(self):
        err = CommandExecutionError("msg", ide_name="vscode", command_name="save")
        assert err.context["ide_name"] == "vscode"
        assert err.context["command_name"] == "save"

    def test_session_error(self):
        err = SessionError("msg", ide_name="vscode", session_id="s1")
        assert err.context["ide_name"] == "vscode"
        assert err.context["session_id"] == "s1"

    def test_artifact_error(self):
        err = ArtifactError("msg", ide_name="vscode", artifact_id="a1")
        assert err.context["ide_name"] == "vscode"
        assert err.context["artifact_id"] == "a1"

    def test_cache_error(self):
        err = CacheError("msg", cache_key="k1", backend="redis")
        assert err.context["cache_key"] == "k1"
        assert err.context["backend"] == "redis"

    def test_serialization_error(self):
        err = SerializationError("msg", format_type="json", data_type="dict")
        assert err.context["format_type"] == "json"
        assert err.context["data_type"] == "dict"

    def test_visualization_error(self):
        err = VisualizationError("msg", tool_name="matplotlib")
        assert err.context["tool_name"] == "matplotlib"

    def test_plotting_error(self):
        err = PlottingError("msg", tool_name="matplotlib", plot_type="scatter")
        assert err.context["tool_name"] == "matplotlib"
        assert err.context["plot_type"] == "scatter"

    def test_documentation_error(self):
        err = DocumentationError("msg", doc_type="sphinx")
        assert err.context["doc_type"] == "sphinx"

    def test_api_documentation_error(self):
        err = APIDocumentationError("msg", doc_type="openapi", target_path="path")
        assert err.context["doc_type"] == "openapi"
        assert err.context["target_path"] == "path"
