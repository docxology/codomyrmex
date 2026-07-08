"""
Unit tests for plugin_system.exceptions — Zero-Mock compliant.

Covers: PluginError (base), LoadError, DependencyError, HookError,
PluginValidationError, PluginStateError, PluginConflictError —
context field storage, inheritance from CodomyrmexError, raise/catch.
"""

import pytest

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.plugin_system.exceptions import (
    DependencyError,
    HookError,
    LoadError,
    PluginConflictError,
    PluginError,
    PluginStateError,
    PluginValidationError,
)

# ── PluginError ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestPluginError:
    def test_is_codomyrmex_error(self):
        e = PluginError("plugin failed")
        assert isinstance(e, CodomyrmexError)

    def test_message_stored(self):
        e = PluginError("something broke in plugin")
        assert "something broke in plugin" in str(e)

    def test_plugin_name_stored_when_provided(self):
        e = PluginError("err", plugin_name="my-plugin")
        assert e.context["plugin_name"] == "my-plugin"

    def test_plugin_name_not_stored_when_none(self):
        e = PluginError("err")
        assert "plugin_name" not in e.context

    def test_plugin_version_stored_when_provided(self):
        e = PluginError("err", plugin_version="1.2.3")
        assert e.context["plugin_version"] == "1.2.3"

    def test_plugin_version_not_stored_when_none(self):
        e = PluginError("err")
        assert "plugin_version" not in e.context

    def test_both_fields_stored(self):
        e = PluginError("err", plugin_name="acme", plugin_version="0.1.0")
        assert e.context["plugin_name"] == "acme"
        assert e.context["plugin_version"] == "0.1.0"

    def test_raise_and_catch(self):
        with pytest.raises(PluginError, match="plugin error"):
            raise PluginError("plugin error")

    def test_catch_as_codomyrmex_error(self):
        with pytest.raises(CodomyrmexError):
            raise PluginError("plugin error")


# ── LoadError ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestLoadError:
    def test_is_plugin_error(self):
        e = LoadError("load failed")
        assert isinstance(e, PluginError)

    def test_is_codomyrmex_error(self):
        e = LoadError("load failed")
        assert isinstance(e, CodomyrmexError)

    def test_message_stored(self):
        e = LoadError("failed to load module")
        assert "failed to load module" in str(e)

    def test_plugin_path_stored_when_provided(self):
        e = LoadError("err", plugin_path="/opt/plugins/my_plugin.py")
        assert e.context["plugin_path"] == "/opt/plugins/my_plugin.py"

    def test_plugin_path_not_stored_when_none(self):
        e = LoadError("err")
        assert "plugin_path" not in e.context

    def test_module_name_stored_when_provided(self):
        e = LoadError("err", module_name="my_plugin.core")
        assert e.context["module_name"] == "my_plugin.core"

    def test_module_name_not_stored_when_none(self):
        e = LoadError("err")
        assert "module_name" not in e.context

    def test_plugin_name_inherited_from_plugin_error(self):
        e = LoadError("err", plugin_name="loader-plugin")
        assert e.context["plugin_name"] == "loader-plugin"

    def test_all_fields_stored(self):
        e = LoadError(
            "err",
            plugin_name="alpha",
            plugin_version="2.0",
            plugin_path="/plugins/alpha.py",
            module_name="alpha.entry",
        )
        assert e.context["plugin_name"] == "alpha"
        assert e.context["plugin_version"] == "2.0"
        assert e.context["plugin_path"] == "/plugins/alpha.py"
        assert e.context["module_name"] == "alpha.entry"

    def test_none_fields_not_in_context(self):
        e = LoadError("err")
        assert "plugin_name" not in e.context
        assert "plugin_version" not in e.context
        assert "plugin_path" not in e.context
        assert "module_name" not in e.context

    def test_raise_and_catch(self):
        with pytest.raises(LoadError):
            raise LoadError("import error", module_name="bad.module")

    def test_catch_as_plugin_error(self):
        with pytest.raises(PluginError):
            raise LoadError("import failed")


# ── DependencyError ───────────────────────────────────────────────────


@pytest.mark.unit
class TestDependencyError:
    def test_is_plugin_error(self):
        e = DependencyError("dep failed")
        assert isinstance(e, PluginError)

    def test_message_stored(self):
        e = DependencyError("missing required dependency")
        assert "missing required dependency" in str(e)

    def test_required_dependency_stored_when_provided(self):
        e = DependencyError("err", required_dependency="requests")
        assert e.context["required_dependency"] == "requests"

    def test_required_dependency_not_stored_when_none(self):
        e = DependencyError("err")
        assert "required_dependency" not in e.context

    def test_required_version_stored_when_provided(self):
        e = DependencyError("err", required_version=">=2.0")
        assert e.context["required_version"] == ">=2.0"

    def test_required_version_not_stored_when_none(self):
        e = DependencyError("err")
        assert "required_version" not in e.context

    def test_available_version_stored_when_provided(self):
        e = DependencyError("err", available_version="1.8.0")
        assert e.context["available_version"] == "1.8.0"

    def test_available_version_not_stored_when_none(self):
        e = DependencyError("err")
        assert "available_version" not in e.context

    def test_all_fields_stored(self):
        e = DependencyError(
            "version conflict",
            required_dependency="numpy",
            required_version=">=1.24",
            available_version="1.20.0",
        )
        assert e.context["required_dependency"] == "numpy"
        assert e.context["required_version"] == ">=1.24"
        assert e.context["available_version"] == "1.20.0"

    def test_none_fields_not_in_context(self):
        e = DependencyError("err")
        assert "required_dependency" not in e.context
        assert "required_version" not in e.context
        assert "available_version" not in e.context

    def test_raise_and_catch(self):
        with pytest.raises(DependencyError):
            raise DependencyError("missing dep", required_dependency="scipy")


# ── HookError ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestHookError:
    def test_is_plugin_error(self):
        e = HookError("hook failed")
        assert isinstance(e, PluginError)

    def test_message_stored(self):
        e = HookError("hook invocation failed")
        assert "hook invocation failed" in str(e)

    def test_hook_name_stored_when_provided(self):
        e = HookError("err", hook_name="on_startup")
        assert e.context["hook_name"] == "on_startup"

    def test_hook_name_not_stored_when_none(self):
        e = HookError("err")
        assert "hook_name" not in e.context

    def test_hook_type_stored_when_provided(self):
        e = HookError("err", hook_type="pre")
        assert e.context["hook_type"] == "pre"

    def test_hook_type_not_stored_when_none(self):
        e = HookError("err")
        assert "hook_type" not in e.context

    def test_both_fields_stored(self):
        e = HookError("err", hook_name="before_request", hook_type="filter")
        assert e.context["hook_name"] == "before_request"
        assert e.context["hook_type"] == "filter"

    def test_plugin_name_passed_through(self):
        e = HookError("err", plugin_name="auth-plugin", hook_name="verify")
        assert e.context["plugin_name"] == "auth-plugin"
        assert e.context["hook_name"] == "verify"

    def test_none_fields_not_in_context(self):
        e = HookError("err")
        assert "hook_name" not in e.context
        assert "hook_type" not in e.context

    def test_raise_and_catch(self):
        with pytest.raises(HookError):
            raise HookError(
                "post hook crashed", hook_name="on_shutdown", hook_type="post"
            )


# ── PluginValidationError ─────────────────────────────────────────────


@pytest.mark.unit
class TestPluginValidationError:
    def test_is_plugin_error(self):
        e = PluginValidationError("validation failed")
        assert isinstance(e, PluginError)

    def test_message_stored(self):
        e = PluginValidationError("schema mismatch")
        assert "schema mismatch" in str(e)

    def test_validation_errors_stored_when_provided(self):
        errors = ["field 'name' required", "field 'version' must be semver"]
        e = PluginValidationError("err", validation_errors=errors)
        assert e.context["validation_errors"] == errors

    def test_validation_errors_not_stored_when_none(self):
        e = PluginValidationError("err")
        assert "validation_errors" not in e.context

    def test_empty_validation_errors_not_stored(self):
        """Empty list is falsy — not stored in context per source logic."""
        e = PluginValidationError("err", validation_errors=[])
        assert "validation_errors" not in e.context

    def test_single_validation_error(self):
        e = PluginValidationError("err", validation_errors=["missing field 'id'"])
        assert len(e.context["validation_errors"]) == 1
        assert "missing field 'id'" in e.context["validation_errors"]

    def test_plugin_name_combined_with_validation_errors(self):
        e = PluginValidationError(
            "err",
            plugin_name="bad-plugin",
            validation_errors=["invalid schema"],
        )
        assert e.context["plugin_name"] == "bad-plugin"
        assert e.context["validation_errors"] == ["invalid schema"]

    def test_raise_and_catch(self):
        with pytest.raises(PluginValidationError):
            raise PluginValidationError("invalid", validation_errors=["field missing"])


# ── PluginStateError ──────────────────────────────────────────────────


@pytest.mark.unit
class TestPluginStateError:
    def test_is_plugin_error(self):
        e = PluginStateError("state error")
        assert isinstance(e, PluginError)

    def test_message_stored(self):
        e = PluginStateError("invalid state transition")
        assert "invalid state transition" in str(e)

    def test_current_state_stored_when_provided(self):
        e = PluginStateError("err", current_state="loaded")
        assert e.context["current_state"] == "loaded"

    def test_current_state_not_stored_when_none(self):
        e = PluginStateError("err")
        assert "current_state" not in e.context

    def test_attempted_state_stored_when_provided(self):
        e = PluginStateError("err", attempted_state="unloaded")
        assert e.context["attempted_state"] == "unloaded"

    def test_attempted_state_not_stored_when_none(self):
        e = PluginStateError("err")
        assert "attempted_state" not in e.context

    def test_both_fields_stored(self):
        e = PluginStateError("err", current_state="running", attempted_state="paused")
        assert e.context["current_state"] == "running"
        assert e.context["attempted_state"] == "paused"

    def test_none_fields_not_in_context(self):
        e = PluginStateError("err")
        assert "current_state" not in e.context
        assert "attempted_state" not in e.context

    def test_raise_and_catch(self):
        with pytest.raises(PluginStateError):
            raise PluginStateError(
                "cannot transition",
                current_state="active",
                attempted_state="init",
            )

    def test_catch_as_plugin_error(self):
        with pytest.raises(PluginError):
            raise PluginStateError("bad state")


# ── PluginConflictError ───────────────────────────────────────────────


@pytest.mark.unit
class TestPluginConflictError:
    def test_is_plugin_error(self):
        e = PluginConflictError("conflict detected")
        assert isinstance(e, PluginError)

    def test_message_stored(self):
        e = PluginConflictError("namespace collision")
        assert "namespace collision" in str(e)

    def test_conflicting_plugin_stored_when_provided(self):
        e = PluginConflictError("err", conflicting_plugin="other-plugin")
        assert e.context["conflicting_plugin"] == "other-plugin"

    def test_conflicting_plugin_not_stored_when_none(self):
        e = PluginConflictError("err")
        assert "conflicting_plugin" not in e.context

    def test_conflict_type_stored_when_provided(self):
        e = PluginConflictError("err", conflict_type="namespace")
        assert e.context["conflict_type"] == "namespace"

    def test_conflict_type_not_stored_when_none(self):
        e = PluginConflictError("err")
        assert "conflict_type" not in e.context

    def test_both_fields_stored(self):
        e = PluginConflictError(
            "err", conflicting_plugin="plugin-b", conflict_type="resource"
        )
        assert e.context["conflicting_plugin"] == "plugin-b"
        assert e.context["conflict_type"] == "resource"

    def test_none_fields_not_in_context(self):
        e = PluginConflictError("err")
        assert "conflicting_plugin" not in e.context
        assert "conflict_type" not in e.context

    def test_raise_and_catch(self):
        with pytest.raises(PluginConflictError):
            raise PluginConflictError(
                "conflict",
                conflicting_plugin="rival-plugin",
                conflict_type="namespace",
            )

    def test_catch_as_codomyrmex_error(self):
        with pytest.raises(CodomyrmexError):
            raise PluginConflictError("conflict")


# ── Inheritance chain ─────────────────────────────────────────────────


@pytest.mark.unit
class TestInheritanceChain:
    def test_all_inherit_from_plugin_error(self):
        for cls in [
            LoadError,
            DependencyError,
            HookError,
            PluginValidationError,
            PluginStateError,
            PluginConflictError,
        ]:
            assert issubclass(cls, PluginError), (
                f"{cls.__name__} must subclass PluginError"
            )

    def test_all_inherit_from_codomyrmex_error(self):
        for cls in [
            PluginError,
            LoadError,
            DependencyError,
            HookError,
            PluginValidationError,
            PluginStateError,
            PluginConflictError,
        ]:
            assert issubclass(cls, CodomyrmexError), (
                f"{cls.__name__} must subclass CodomyrmexError"
            )

    def test_all_are_exceptions(self):
        for cls in [
            PluginError,
            LoadError,
            DependencyError,
            HookError,
            PluginValidationError,
            PluginStateError,
            PluginConflictError,
        ]:
            assert issubclass(cls, Exception), f"{cls.__name__} must subclass Exception"
