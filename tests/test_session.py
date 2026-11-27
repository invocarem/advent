"""Tests for the engine/front-end bridge."""

from __future__ import annotations

import time

import pytest

from advent.session import DONE, PROMPT, EngineSession, Event
from advent.vocabulary import Location, Object


def wait_event(session: EngineSession, kind: str, timeout: float = 5.0) -> Event:
    """Wait for the next event of ``kind`` and return it."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for event in session.drain():
            if event.kind == kind:
                return event
        time.sleep(0.005)
    raise AssertionError("no %r event arrived" % kind)


def wait_for(session: EngineSession, kind: str, timeout: float = 5.0) -> str | None:
    """Wait for the next event of ``kind`` and return its payload."""
    return wait_event(session, kind, timeout).payload


@pytest.fixture
def session():
    engine = EngineSession(seed=7).start()
    try:
        yield engine
    finally:
        engine.stop()
        engine.join(2.0)


def test_the_session_bridges_a_scripted_game(session: EngineSession) -> None:
    prompt = wait_for(session, PROMPT)
    assert prompt is not None and prompt.rstrip().endswith("**")
    assert session.game is not None
    assert session.game.loc == int(Location.ROAD)

    session.submit("n")
    wait_for(session, PROMPT)
    session.submit("house")
    wait_for(session, PROMPT)
    assert session.game.loc == int(Location.HOUSE)

    session.submit("take keys")
    wait_for(session, PROMPT)
    assert int(Object.KEYS) in session.game.inventory()

    session.submit("quit")
    wait_for(session, PROMPT)
    session.submit("y")
    wait_for(session, DONE, timeout=5.0)
    assert session.finished.is_set()


def test_prompt_events_carry_a_frozen_snapshot(session: EngineSession) -> None:
    event = wait_event(session, PROMPT)
    snapshot = event.snapshot
    assert snapshot is not None
    assert snapshot.loc == int(Location.ROAD)
    assert snapshot.here == ()
    assert snapshot.inventory == ()
    assert snapshot.dark is False
    assert snapshot.motions

    session.submit("n")
    wait_for(session, PROMPT)
    session.submit("house")
    snapshot = wait_event(session, PROMPT).snapshot
    assert snapshot is not None
    assert snapshot.loc == int(Location.HOUSE)
    assert int(Object.KEYS) in snapshot.here
    assert snapshot.motions

    session.submit("quit")
    wait_for(session, PROMPT)
    session.submit("y")
    done = wait_event(session, DONE)
    assert done.snapshot is not None


def test_stop_ends_the_engine_cleanly(session: EngineSession) -> None:
    wait_for(session, PROMPT)
    session.stop()
    wait_for(session, DONE)
    session.join(2.0)
    assert not session.running
    assert session.finished.is_set()


def test_welcome_arrives_as_the_first_prompt() -> None:
    session = EngineSession(seed=7).start()
    try:
        # The welcome question is a prompt (a yes/no question), not a write.
        prompt = wait_for(session, PROMPT)
        assert prompt is not None
        assert "Welcome to Adventure" in prompt
    finally:
        session.stop()
        session.join(2.0)
