"""Tests for HermesSession.close() lifecycle / on_close callback.

Zero-mock policy: all tests use real HermesSession dataclass.
"""

from __future__ import annotations

import pytest

from codomyrmex.agents.hermes.session import HermesSession


class TestHermesSessionClose:
    """Tests for HermesSession.close() and on_close callback behaviour."""

    def test_close_without_callback_is_noop(self) -> None:
        sess = HermesSession()
        sess.close()  # Must not raise

    def test_on_close_callback_is_called(self) -> None:
        called: list[str] = []

        def _cb(s: HermesSession) -> None:
            called.append(s.session_id)

        sess = HermesSession(on_close=_cb)
        sess.close()
        assert called == [sess.session_id]

    def test_on_close_called_only_once(self) -> None:
        count: list[int] = [0]

        def _cb(_s: HermesSession) -> None:
            count[0] += 1

        sess = HermesSession(on_close=_cb)
        sess.close()
        sess.close()  # Second call — callback must not fire again
        assert count[0] == 1

    def test_on_close_clears_after_first_call(self) -> None:
        sess = HermesSession(on_close=lambda s: None)
        sess.close()
        assert sess.on_close is None

    def test_on_close_exception_does_not_propagate(self) -> None:
        def _bad(_s: HermesSession) -> None:
            raise ValueError("intentional test error")

        sess = HermesSession(on_close=_bad)
        sess.close()  # Must not raise
        assert sess.on_close is None  # callback cleared even after exception

    def test_close_receives_full_session_object(self) -> None:
        received: list[HermesSession] = []

        def _cb(s: HermesSession) -> None:
            received.append(s)

        sess = HermesSession(name="test-ki-session", on_close=_cb)
        sess.add_message("user", "Hello")
        sess.add_message("assistant", "World")
        sess.close()

        assert received[0] is sess
        assert received[0].message_count == 2
        assert received[0].name == "test-ki-session"

    def test_ki_extraction_triggered_on_close(self) -> None:
        """Simulate the recommended KI extraction pattern."""
        extracted: list[str] = []

        def _extract_ki(session: HermesSession) -> None:
            if session.message_count >= 3:
                extracted.append(session.session_id)

        sess = HermesSession(on_close=_extract_ki)
        for role, content in [
            ("user", "Q1"),
            ("assistant", "A1"),
            ("user", "Q2"),
        ]:
            sess.add_message(role, content)

        sess.close()
        assert extracted == [sess.session_id]

    def test_ki_extraction_skipped_for_short_sessions(self) -> None:
        extracted: list[str] = []

        def _extract_ki(session: HermesSession) -> None:
            if session.message_count >= 3:
                extracted.append(session.session_id)

        sess = HermesSession(on_close=_extract_ki)
        sess.add_message("user", "Q1")  # Only 1 message — below threshold
        sess.close()
        assert extracted == []

    def test_close_not_in_repr_or_compare(self) -> None:
        import dataclasses
        cb = lambda s: None
        s1 = HermesSession(session_id="abc", on_close=cb)
        # on_close is excluded from __repr__
        assert "on_close" not in repr(s1)
        # on_close excluded from __eq__ via compare=False — use dataclasses.replace
        # to clone s1 with only on_close changed (avoids timestamp drift)
        s2 = dataclasses.replace(s1, on_close=None)
        assert s1 == s2
