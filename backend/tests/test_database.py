"""Tests for database module (get_db dependency)."""

import pytest


def test_get_db_yields_session_and_closes_on_exit(monkeypatch):
    """get_db() is a generator: it yields a session and closes it in finally."""
    from app.database import get_db

    closed = []

    class FakeSession:
        def close(self):
            closed.append(True)

    def fake_session_local():
        return FakeSession()

    monkeypatch.setattr("app.database.SessionLocal", fake_session_local)

    gen = get_db()
    session = next(gen)
    assert session is not None
    assert isinstance(session, FakeSession)
    try:
        gen.close()  # runs finally -> db.close()
    except GeneratorExit:
        pass
    assert closed == [True]
