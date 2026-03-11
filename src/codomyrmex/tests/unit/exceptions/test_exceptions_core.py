"""Zero-mock tests for the codomyrmex exceptions module.

Covers: base hierarchy, custom attributes, __str__, to_dict,
chaining, utility functions, config/network/specialized subclasses.
"""

from __future__ import annotations

import pytest

from codomyrmex.exceptions import (
    AIProviderError,
    APIDocumentationError,
    APIError,
    ArtifactError,
    AuthenticationError,
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
    CodomyrmexError,
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
    create_error_context,
    format_exception_chain,
)

# ---------------------------------------------------------------------------
# TestCodomyrmexErrorBase — root exception behaviour
# ---------------------------------------------------------------------------


class TestCodomyrmexErrorBase:
    """Tests for CodomyrmexError — the root of the hierarchy."""

    def test_is_exception_subclass(self):
        assert issubclass(CodomyrmexError, Exception)

    def test_minimal_construction(self):
        err = CodomyrmexError("something went wrong")
        assert err.message == "something went wrong"
        assert err.context == {}
        assert err.error_code == "CodomyrmexError"

    def test_custom_error_code(self):
        err = CodomyrmexError("msg", error_code="ERR_001")
        assert err.error_code == "ERR_001"

    def test_context_dict_passed(self):
        ctx = {"module": "cli", "step": 3}
        err = CodomyrmexError("ctx error", context=ctx)
        assert err.context["module"] == "cli"
        assert err.context["step"] == 3

    def test_kwargs_merged_into_context(self):
        err = CodomyrmexError("err", operation="parse", line=42)
        assert err.context["operation"] == "parse"
        assert err.context["line"] == 42

    def test_context_dict_and_kwargs_merged(self):
        err = CodomyrmexError("err", context={"a": 1}, b=2)
        assert err.context["a"] == 1
        assert err.context["b"] == 2

    def test_str_without_context(self):
        err = CodomyrmexError("plain message")
        result = str(err)
        assert "[CodomyrmexError]" in result
        assert "plain message" in result
        assert "Context" not in result

    def test_str_with_context(self):
        err = CodomyrmexError("msg", context={"key": "val"})
        result = str(err)
        assert "Context:" in result
        assert "key=val" in result

    def test_to_dict_structure(self):
        err = CodomyrmexError("dict test", context={"x": 1}, error_code="E42")
        d = err.to_dict()
        assert d["error_type"] == "CodomyrmexError"
        assert d["error_code"] == "E42"
        assert d["message"] == "dict test"
        assert d["context"]["x"] == 1

    def test_to_dict_error_type_is_class_name(self):
        class MyCustomError(CodomyrmexError):
            pass

        err = MyCustomError("custom")
        assert err.to_dict()["error_type"] == "MyCustomError"

    def test_args_set_correctly(self):
        err = CodomyrmexError("arg check")
        assert err.args[0] == "arg check"

    def test_can_be_raised_and_caught(self):
        with pytest.raises(CodomyrmexError) as exc_info:
            raise CodomyrmexError("raised!")
        assert exc_info.value.message == "raised!"

    def test_catchable_as_exception(self):
        with pytest.raises(CodomyrmexError):
            raise CodomyrmexError("generic catch")


# ---------------------------------------------------------------------------
# TestExceptionChaining — __cause__ / __context__ traversal
# ---------------------------------------------------------------------------


class TestExceptionChaining:
    """Tests for format_exception_chain utility."""

    def test_single_codomyrmex_exception(self):
        err = CodomyrmexError("top level")
        result = format_exception_chain(err)
        assert "[CodomyrmexError]" in result
        assert "top level" in result

    def test_chain_codomyrmex_then_stdlib(self):
        original = ValueError("original value error")
        try:
            raise CodomyrmexError("wrapper") from original
        except CodomyrmexError as chained:
            result = format_exception_chain(chained)
        assert "[CodomyrmexError]" in result
        assert "[ValueError]" in result
        assert "original value error" in result

    def test_chain_stdlib_only(self):
        err = RuntimeError("raw runtime")
        result = format_exception_chain(err)
        assert "[RuntimeError]" in result
        assert "raw runtime" in result

    def test_no_chain_returns_single_line(self):
        err = CodomyrmexError("solo")
        result = format_exception_chain(err)
        assert "\n" not in result

    def test_multi_level_chain(self):
        try:
            try:
                raise OSError("disk full")
            except OSError as e:
                raise CodomyrmexError("io failed") from e
        except CodomyrmexError as top:
            result = format_exception_chain(top)
        assert "[CodomyrmexError]" in result
        assert "[OSError]" in result


# ---------------------------------------------------------------------------
# TestCreateErrorContext — utility function
# ---------------------------------------------------------------------------


class TestCreateErrorContext:
    """Tests for create_error_context helper."""

    def test_returns_dict(self):
        ctx = create_error_context(a=1, b="two")
        assert isinstance(ctx, dict)

    def test_non_none_values_included(self):
        ctx = create_error_context(x=10, y="hello")
        assert ctx["x"] == 10
        assert ctx["y"] == "hello"

    def test_none_values_excluded(self):
        ctx = create_error_context(present="yes", absent=None)
        assert "present" in ctx
        assert "absent" not in ctx

    def test_empty_call_returns_empty_dict(self):
        ctx = create_error_context()
        assert ctx == {}

    def test_all_none_returns_empty_dict(self):
        ctx = create_error_context(a=None, b=None)
        assert ctx == {}


# ---------------------------------------------------------------------------
# TestConfigExceptions
# ---------------------------------------------------------------------------


class TestConfigExceptions:
    """Tests for ConfigurationError, EnvironmentError, DependencyError."""

    def test_configuration_error_inherits_base(self):
        assert issubclass(ConfigurationError, CodomyrmexError)

    def test_configuration_error_stores_config_key(self):
        err = ConfigurationError("bad config", config_key="DATABASE_URL")
        assert err.context["config_key"] == "DATABASE_URL"

    def test_configuration_error_stores_config_file(self):
        err = ConfigurationError("missing file", config_file="/etc/app.yaml")
        assert "config_file" in err.context
        assert "/etc/app.yaml" in err.context["config_file"]

    def test_configuration_error_no_optional_args(self):
        err = ConfigurationError("simple")
        assert err.context == {}

    def test_environment_error_inherits_base(self):
        assert issubclass(EnvironmentError, CodomyrmexError)

    def test_environment_error_stores_variable_name(self):
        err = EnvironmentError("missing var", variable_name="API_KEY")
        assert err.context["variable_name"] == "API_KEY"

    def test_environment_error_stores_expected_value(self):
        err = EnvironmentError("bad value", expected_value="production")
        assert err.context["expected_value"] == "production"

    def test_dependency_error_stores_all_version_info(self):
        err = DependencyError(
            "wrong version",
            dependency_name="numpy",
            required_version=">=1.24",
            installed_version="1.20",
        )
        assert err.context["dependency_name"] == "numpy"
        assert err.context["required_version"] == ">=1.24"
        assert err.context["installed_version"] == "1.20"


# ---------------------------------------------------------------------------
# TestNetworkExceptions
# ---------------------------------------------------------------------------


class TestNetworkExceptions:
    """Tests for NetworkError, APIError, ValidationError, SchemaError, TimeoutError."""

    def test_network_error_with_url_and_status(self):
        err = NetworkError("failed", url="https://api.example.com", status_code=503)
        assert err.context["url"] == "https://api.example.com"
        assert err.context["status_code"] == 503

    def test_network_error_status_code_zero_stored(self):
        # 0 is falsy but should be stored (status_code is not None)
        err = NetworkError("err", status_code=0)
        assert err.context["status_code"] == 0

    def test_api_error_stores_endpoint_and_method(self):
        err = APIError("api down", endpoint="/v1/users", method="POST")
        assert err.context["endpoint"] == "/v1/users"
        assert err.context["method"] == "POST"

    def test_validation_error_stores_field_and_rule(self):
        err = ValidationError("invalid email", field_name="email", validation_rule="email_format")
        assert err.context["field_name"] == "email"
        assert err.context["validation_rule"] == "email_format"

    def test_schema_error_stores_schema_and_preview(self):
        err = SchemaError("schema mismatch", schema_name="UserSchema", data_preview='{"name":null}')
        assert err.context["schema_name"] == "UserSchema"
        assert err.context["data_preview"] == '{"name":null}'

    def test_timeout_error_stores_seconds(self):
        err = TimeoutError("timed out", timeout_seconds=30.5)
        assert err.context["timeout_seconds"] == 30.5

    def test_timeout_error_zero_seconds_stored(self):
        err = TimeoutError("instant timeout", timeout_seconds=0.0)
        assert err.context["timeout_seconds"] == 0.0

    def test_timeout_error_no_seconds(self):
        err = TimeoutError("no duration given")
        assert "timeout_seconds" not in err.context


# ---------------------------------------------------------------------------
# TestSpecializedExceptions
# ---------------------------------------------------------------------------


class TestSpecializedExceptions:
    """Tests for specialized domain exception classes."""

    def test_performance_error_metric_and_threshold(self):
        err = PerformanceError("slow", metric_name="latency_p99", threshold=200.0)
        assert err.context["metric_name"] == "latency_p99"
        assert err.context["threshold"] == 200.0

    def test_performance_error_threshold_zero_stored(self):
        err = PerformanceError("zero threshold", threshold=0.0)
        assert err.context["threshold"] == 0.0

    def test_logging_error_stores_logger_and_level(self):
        err = LoggingError("handler failed", logger_name="root", level="ERROR")
        assert err.context["logger_name"] == "root"
        assert err.context["level"] == "ERROR"

    def test_system_discovery_error_stores_scope(self):
        err = SystemDiscoveryError("scan failed", discovery_scope="modules")
        assert err.context["discovery_scope"] == "modules"

    def test_capability_scan_error_stores_capability(self):
        err = CapabilityScanError("cap missing", capability_name="git_operations")
        assert err.context["capability_name"] == "git_operations"

    def test_modeling_3d_error_stores_format(self):
        err = Modeling3DError("bad mesh", model_format="obj")
        assert err.context["model_format"] == "obj"

    def test_physical_management_error_stores_device(self):
        err = PhysicalManagementError("device lost", device_id="sensor-42")
        assert err.context["device_id"] == "sensor-42"

    def test_simulation_error_stores_id_and_engine(self):
        err = SimulationError("diverged", simulation_id="sim-007", engine="physics_v2")
        assert err.context["simulation_id"] == "sim-007"
        assert err.context["engine"] == "physics_v2"

    def test_terminal_error_stores_type(self):
        err = TerminalError("render fail", terminal_type="xterm-256color")
        assert err.context["terminal_type"] == "xterm-256color"

    def test_interactive_shell_error_inherits_terminal(self):
        assert issubclass(InteractiveShellError, TerminalError)

    def test_interactive_shell_error_stores_shell_name(self):
        err = InteractiveShellError("prompt broken", shell_name="zsh")
        assert err.context["shell_name"] == "zsh"

    def test_database_error_stores_db_and_query(self):
        err = DatabaseError("query failed", db_name="postgres", query="SELECT * FROM users")
        assert err.context["db_name"] == "postgres"
        assert err.context["query"] == "SELECT * FROM users"

    def test_cicd_error_stores_pipeline_and_stage(self):
        err = CICDError("build failed", pipeline_id="pipe-123", stage="test")
        assert err.context["pipeline_id"] == "pipe-123"
        assert err.context["stage"] == "test"

    def test_deployment_error_stores_env_and_version(self):
        err = DeploymentError("rollout failed", environment="production", version="2.1.0")
        assert err.context["environment"] == "production"
        assert err.context["version"] == "2.1.0"

    def test_resource_error_stores_id_and_type(self):
        err = ResourceError("out of quota", resource_id="gpu-0", resource_type="GPU")
        assert err.context["resource_id"] == "gpu-0"
        assert err.context["resource_type"] == "GPU"

    def test_memory_error_inherits_resource(self):
        assert issubclass(MemoryError, ResourceError)

    def test_memory_error_stores_usage_and_limit(self):
        err = MemoryError("OOM", memory_usage=8192, limit=4096)
        assert err.context["memory_usage"] == 8192
        assert err.context["limit"] == 4096

    def test_memory_error_usage_zero_stored(self):
        err = MemoryError("zero usage", memory_usage=0, limit=1024)
        assert err.context["memory_usage"] == 0

    def test_spatial_error_stores_coordinate_system(self):
        err = SpatialError("out of bounds", coordinate_system="WGS84")
        assert err.context["coordinate_system"] == "WGS84"

    def test_event_error_stores_type_and_id(self):
        err = EventError("dispatch failed", event_type="UserCreated", event_id="evt-999")
        assert err.context["event_type"] == "UserCreated"
        assert err.context["event_id"] == "evt-999"

    def test_skill_error_stores_skill_name(self):
        err = SkillError("skill crashed", skill_name="visual-explainer")
        assert err.context["skill_name"] == "visual-explainer"

    def test_template_error_stores_template_name(self):
        err = TemplateError("render error", template_name="report.html.j2")
        assert err.context["template_name"] == "report.html.j2"

    def test_plugin_error_stores_name_and_version(self):
        err = PluginError("load failed", plugin_name="auth-plugin", plugin_version="0.3.2")
        assert err.context["plugin_name"] == "auth-plugin"
        assert err.context["plugin_version"] == "0.3.2"

    def test_authentication_error_stores_identity_and_mechanism(self):
        err = AuthenticationError("denied", identity="user@example.com", mechanism="oauth2")
        assert err.context["identity"] == "user@example.com"
        assert err.context["mechanism"] == "oauth2"

    def test_circuit_open_error_stores_circuit_name(self):
        err = CircuitOpenError("circuit tripped", circuit_name="payment-service")
        assert err.context["circuit_name"] == "payment-service"

    def test_bulkhead_full_error_stores_name_and_concurrency(self):
        err = BulkheadFullError("full", bulkhead_name="db-pool", max_concurrency=10)
        assert err.context["bulkhead_name"] == "db-pool"
        assert err.context["max_concurrency"] == 10

    def test_bulkhead_full_error_max_concurrency_zero_stored(self):
        err = BulkheadFullError("no slots", max_concurrency=0)
        assert err.context["max_concurrency"] == 0

    def test_compression_error_stores_algorithm(self):
        err = CompressionError("bad archive", algorithm="lzma")
        assert err.context["algorithm"] == "lzma"

    def test_encryption_error_stores_algorithm_and_key_id(self):
        err = EncryptionError("decrypt failed", algorithm="AES-256-GCM", key_id="key-abc")
        assert err.context["algorithm"] == "AES-256-GCM"
        assert err.context["key_id"] == "key-abc"

    def test_cache_error_stores_key_and_backend(self):
        err = CacheError("miss storm", cache_key="user:42:profile", backend="redis")
        assert err.context["cache_key"] == "user:42:profile"
        assert err.context["backend"] == "redis"

    def test_serialization_error_stores_format_and_data_type(self):
        err = SerializationError("encode failed", format_type="json", data_type="UserModel")
        assert err.context["format_type"] == "json"
        assert err.context["data_type"] == "UserModel"


# ---------------------------------------------------------------------------
# TestIDEExceptionHierarchy
# ---------------------------------------------------------------------------


class TestIDEExceptionHierarchy:
    """Tests for IDEError and its subclasses."""

    def test_ide_error_inherits_base(self):
        assert issubclass(IDEError, CodomyrmexError)

    def test_ide_error_stores_ide_name(self):
        err = IDEError("connection lost", ide_name="VSCode")
        assert err.context["ide_name"] == "VSCode"

    def test_ide_connection_error_inherits_ide_error(self):
        assert issubclass(IDEConnectionError, IDEError)

    def test_ide_connection_error_stores_host_and_port(self):
        err = IDEConnectionError("refused", host="localhost", port=8080)
        assert err.context["host"] == "localhost"
        assert err.context["port"] == 8080

    def test_ide_connection_error_port_zero_stored(self):
        err = IDEConnectionError("invalid port", port=0)
        assert err.context["port"] == 0

    def test_command_execution_error_inherits_ide_error(self):
        assert issubclass(CommandExecutionError, IDEError)

    def test_command_execution_error_stores_command_name(self):
        err = CommandExecutionError("exec failed", command_name="formatDocument")
        assert err.context["command_name"] == "formatDocument"

    def test_session_error_inherits_ide_error(self):
        assert issubclass(SessionError, IDEError)

    def test_session_error_stores_session_id(self):
        err = SessionError("session expired", session_id="sess-abc123")
        assert err.context["session_id"] == "sess-abc123"

    def test_artifact_error_inherits_ide_error(self):
        assert issubclass(ArtifactError, IDEError)

    def test_artifact_error_stores_artifact_id(self):
        err = ArtifactError("write failed", artifact_id="art-7")
        assert err.context["artifact_id"] == "art-7"


# ---------------------------------------------------------------------------
# TestErrorCodeDefaultBehaviour
# ---------------------------------------------------------------------------


class TestErrorCodeDefaultBehaviour:
    """Verify error_code defaults to class name for every subclass."""

    @pytest.mark.parametrize(
        ("exc_class", "msg"),
        [
            (ConfigurationError, "cfg"),
            (NetworkError, "net"),
            (ValidationError, "val"),
            (GitOperationError, "git"),
            (CodeExecutionError, "exec"),
            (CacheError, "cache"),
            (EncryptionError, "enc"),
            (PerformanceError, "perf"),
            (PluginError, "plugin"),
            (AuthenticationError, "auth"),
        ],
    )
    def test_default_error_code_is_class_name(self, exc_class, msg):
        err = exc_class(msg)
        assert err.error_code == exc_class.__name__

    @pytest.mark.parametrize(
        ("exc_class", "msg"),
        [
            (ConfigurationError, "cfg"),
            (NetworkError, "net"),
            (CacheError, "cache"),
        ],
    )
    def test_custom_error_code_overrides_default(self, exc_class, msg):
        err = exc_class(msg, error_code="OVERRIDE_42")
        assert err.error_code == "OVERRIDE_42"


# ---------------------------------------------------------------------------
# TestAllExceptionsCatchableAsBase
# ---------------------------------------------------------------------------


class TestAllExceptionsCatchableAsBase:
    """Every public exception must be catchable as CodomyrmexError."""

    @pytest.mark.parametrize(
        "exc_class",
        [
            AIProviderError,
            APIError,
            AuthenticationError,
            BulkheadFullError,
            CICDError,
            CacheError,
            CapabilityScanError,
            CaseError,
            CerebrumError,
            CircuitOpenError,
            CodeExecutionError,
            CodeGenerationError,
            ConfigurationError,
            ContainerError,
            DatabaseError,
            DependencyError,
            DeploymentError,
            DirectoryError,
            DocumentationError,
            EncryptionError,
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
        ],
    )
    def test_catchable_as_codomyrmex_error(self, exc_class):
        caught = False
        try:
            raise exc_class("test")
        except CodomyrmexError:
            caught = True
        assert caught, f"{exc_class.__name__} not catchable as CodomyrmexError"
