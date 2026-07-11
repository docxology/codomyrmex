"""Unit tests for codomyrmex.exceptions.base.

Targets: CodomyrmexError, format_exception_chain, create_error_context.

These tests exercise the base module directly (not via the package-level
re-exports) to guarantee base.py lines are covered.  They are intentionally
additive: test_exceptions.py covers higher-level specialised classes;
this file focuses on the base primitives and every code path in base.py.
"""

import pytest

from codomyrmex.exceptions.base import (
    CodomyrmexError,
    create_error_context,
    format_exception_chain,
)

# ─────────────────────────────────────────────────────────────────────────────
#  CodomyrmexError construction
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCodomyrmexErrorConstruction:
    """Construction edge-cases for CodomyrmexError."""

    def test_message_only(self):
        err = CodomyrmexError("plain message")
        assert err.message == "plain message"
        assert err.context == {}
        assert err.error_code == "CodomyrmexError"

    def test_error_code_defaults_to_class_name(self):
        err = CodomyrmexError("msg")
        assert err.error_code == "CodomyrmexError"

    def test_explicit_error_code_stored(self):
        err = CodomyrmexError("msg", error_code="E_001")
        assert err.error_code == "E_001"

    def test_context_dict_stored(self):
        ctx = {"user": "alice", "op": "read"}
        err = CodomyrmexError("msg", context=ctx)
        assert err.context["user"] == "alice"
        assert err.context["op"] == "read"

    def test_kwargs_merged_into_context(self):
        """Extra kwargs must be merged into self.context."""
        err = CodomyrmexError("msg", path="/tmp/x", retries=3)
        assert err.context["path"] == "/tmp/x"
        assert err.context["retries"] == 3

    def test_kwargs_and_context_merged(self):
        """When both context dict and kwargs supplied, both appear in context."""
        err = CodomyrmexError("msg", context={"a": 1}, b=2)
        assert err.context["a"] == 1
        assert err.context["b"] == 2

    def test_kwargs_override_context(self):
        """kwargs that share a key with context dict overwrite the dict value."""
        err = CodomyrmexError("msg", context={"k": "old"}, k="new")
        assert err.context["k"] == "new"

    def test_none_context_becomes_empty_dict(self):
        err = CodomyrmexError("msg", context=None)
        assert err.context == {}

    def test_is_subclass_of_exception(self):
        err = CodomyrmexError("msg")
        assert isinstance(err, Exception)

    def test_super_call_propagates_message(self):
        """args[0] must be the message string (standard Exception behaviour)."""
        err = CodomyrmexError("hello")
        assert err.args[0] == "hello"


# ─────────────────────────────────────────────────────────────────────────────
#  CodomyrmexError.__str__
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCodomyrmexErrorStr:
    """__str__ output covers both the no-context and with-context branches."""

    def test_str_no_context(self):
        err = CodomyrmexError("oops")
        assert str(err) == "[CodomyrmexError] oops"

    def test_str_with_custom_code(self):
        err = CodomyrmexError("oops", error_code="X_99")
        assert str(err) == "[X_99] oops"

    def test_str_with_context_includes_prefix(self):
        err = CodomyrmexError("oops", context={"k": "v"})
        s = str(err)
        assert s.startswith("[CodomyrmexError] oops")
        assert "(Context:" in s

    def test_str_with_context_includes_kv_pairs(self):
        err = CodomyrmexError("oops", context={"alpha": 1, "beta": "two"})
        s = str(err)
        assert "alpha=1" in s
        assert "beta=two" in s

    def test_str_empty_context_omits_context_clause(self):
        err = CodomyrmexError("oops", context={})
        assert "(Context:" not in str(err)

    def test_str_kwargs_appear_in_output(self):
        err = CodomyrmexError("oops", file="/a/b.py")
        assert "file=/a/b.py" in str(err)


# ─────────────────────────────────────────────────────────────────────────────
#  CodomyrmexError.to_dict
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCodomyrmexErrorToDict:
    """to_dict() serialisation."""

    def test_to_dict_keys_present(self):
        err = CodomyrmexError("msg")
        d = err.to_dict()
        assert set(d.keys()) == {"error_type", "error_code", "message", "context"}

    def test_to_dict_error_type_is_class_name(self):
        err = CodomyrmexError("msg")
        assert err.to_dict()["error_type"] == "CodomyrmexError"

    def test_to_dict_message_matches(self):
        err = CodomyrmexError("the message")
        assert err.to_dict()["message"] == "the message"

    def test_to_dict_context_matches(self):
        ctx = {"x": 42}
        err = CodomyrmexError("msg", context=ctx)
        assert err.to_dict()["context"] == {"x": 42}

    def test_to_dict_error_code_matches(self):
        err = CodomyrmexError("msg", error_code="MY_CODE")
        assert err.to_dict()["error_code"] == "MY_CODE"

    def test_to_dict_subclass_error_type(self):
        """Subclass instances report their own class name as error_type."""

        class MyError(CodomyrmexError):
            pass

        err = MyError("sub message")
        assert err.to_dict()["error_type"] == "MyError"


# ─────────────────────────────────────────────────────────────────────────────
#  Subclassing behaviour
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCodomyrmexErrorSubclassing:
    """Subclasses inherit construction, __str__, and to_dict behaviour."""

    def setup_method(self):
        class ChildError(CodomyrmexError):
            pass

        self.ChildError = ChildError

    def test_subclass_error_code_defaults_to_subclass_name(self):
        err = self.ChildError("sub")
        assert err.error_code == "ChildError"

    def test_subclass_isinstance_checks(self):
        err = self.ChildError("sub")
        assert isinstance(err, CodomyrmexError)
        assert isinstance(err, Exception)

    def test_subclass_can_be_raised_and_caught_as_base(self):
        with pytest.raises(CodomyrmexError):
            raise self.ChildError("child raise")

    def test_subclass_str_uses_child_class_name_as_code(self):
        err = self.ChildError("msg")
        assert "[ChildError]" in str(err)

    def test_subclass_to_dict_error_type(self):
        err = self.ChildError("msg")
        assert err.to_dict()["error_type"] == "ChildError"

    def test_deep_subclass_chain(self):
        class GrandChildError(self.ChildError):
            pass

        err = GrandChildError("deep")
        assert isinstance(err, CodomyrmexError)
        assert err.error_code == "GrandChildError"


# ─────────────────────────────────────────────────────────────────────────────
#  format_exception_chain
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestFormatExceptionChain:
    """format_exception_chain covers all traversal branches."""

    def test_single_codomyrmex_error(self):
        err = CodomyrmexError("solo")
        result = format_exception_chain(err)
        assert result == "[CodomyrmexError] solo"

    def test_single_standard_exception(self):
        err = ValueError("bad value")
        result = format_exception_chain(err)
        assert result == "[ValueError] bad value"

    def test_chain_via_cause(self):
        root = ValueError("root cause")
        wrapper = CodomyrmexError("wrapper")
        wrapper.__cause__ = root
        lines = format_exception_chain(wrapper).split("\n")
        assert len(lines) == 2
        assert "[CodomyrmexError]" in lines[0]
        assert "[ValueError]" in lines[1]

    def test_chain_via_context(self):
        ctx_err = RuntimeError("context error")
        main = CodomyrmexError("main")
        main.__context__ = ctx_err
        lines = format_exception_chain(main).split("\n")
        assert len(lines) == 2
        assert "[CodomyrmexError]" in lines[0]
        assert "[RuntimeError]" in lines[1]

    def test_cause_takes_priority_over_context(self):
        """__cause__ is followed before __context__ by the traversal logic."""
        cause_err = TypeError("the cause")
        ctx_err = RuntimeError("the context")
        main = CodomyrmexError("main")
        main.__cause__ = cause_err
        main.__context__ = ctx_err
        # traversal uses __cause__ first, so only __cause__ appears
        lines = format_exception_chain(main).split("\n")
        assert any("TypeError" in line for line in lines)

    def test_three_level_chain(self):
        root = OSError("disk full")
        mid = ValueError("conversion failed")
        mid.__cause__ = root
        top = CodomyrmexError("operation failed")
        top.__cause__ = mid
        lines = format_exception_chain(top).split("\n")
        assert len(lines) == 3
        assert "[CodomyrmexError]" in lines[0]
        assert "[ValueError]" in lines[1]
        assert "[OSError]" in lines[2]

    def test_codomyrmex_error_with_context_in_chain(self):
        """CodomyrmexError in chain uses its own __str__ (includes [code])."""
        inner = CodomyrmexError("inner", error_code="INNER")
        outer = CodomyrmexError("outer")
        outer.__cause__ = inner
        lines = format_exception_chain(outer).split("\n")
        assert "[INNER]" in lines[1]


# ─────────────────────────────────────────────────────────────────────────────
#  create_error_context
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCreateErrorContext:
    """create_error_context filters None values and returns a plain dict."""

    def test_empty_call_returns_empty_dict(self):
        result = create_error_context()
        assert result == {}

    def test_all_non_none_values_kept(self):
        result = create_error_context(user="bob", count=5, flag=False)
        assert result == {"user": "bob", "count": 5, "flag": False}

    def test_none_values_filtered(self):
        result = create_error_context(a=1, b=None, c="x")
        assert "b" not in result
        assert result == {"a": 1, "c": "x"}

    def test_all_none_returns_empty_dict(self):
        result = create_error_context(x=None, y=None)
        assert result == {}

    def test_false_and_zero_are_not_filtered(self):
        """Only None is excluded — falsy values like 0 and False are kept."""
        result = create_error_context(zero=0, false_val=False, empty_str="")
        assert result["zero"] == 0
        assert result["false_val"] is False
        assert result["empty_str"] == ""

    def test_result_is_plain_dict(self):
        result = create_error_context(k="v")
        assert type(result) is dict

    def test_returned_dict_is_usable_as_context(self):
        """Context dict produced here can be passed directly to CodomyrmexError."""
        ctx = create_error_context(module="auth", action="login", reason=None)
        err = CodomyrmexError("context test", context=ctx)
        assert err.context["module"] == "auth"
        assert "reason" not in err.context
