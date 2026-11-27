"""Smoke tests for the tkinter front end.

These skip when tkinter is missing or no display is available; everything else
in the graphical layer is covered headlessly by ``test_scenes.py``.

The Tk interpreter is created lazily inside each test, never at import time:
on Windows, building and destroying a root during collection can leave Tcl
unable to read its own library files later in the same process.
"""

from __future__ import annotations

import gc
import time

import pytest

tk = pytest.importorskip("tkinter")


@pytest.fixture(autouse=True)
def _collect_tk_garbage():
    """Collect destroyed tkinter widgets on the main thread.

    Tk objects form reference cycles; if the worker threads in later tests
    trigger a collection, Tcl would be entered from the wrong thread.  Running
    the collector here, after each test's window is gone, keeps that from
    happening.
    """
    yield
    gc.collect()


def new_root() -> tk.Tk:
    try:
        return tk.Tk()
    except tk.TclError as exc:  # no display, or a broken Tcl installation
        pytest.skip("tkinter cannot open a display: %s" % exc)


def pump_until(app, predicate, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        app.update()
        if predicate():
            return
        time.sleep(0.01)
    raise AssertionError("the window did not reach the expected state")


def close(app) -> None:
    try:
        if app.winfo_exists():
            app._on_close()
    except tk.TclError:
        pass


def test_canvas_painter_draws_every_scene_and_object(capfd) -> None:
    from advent import art, scenes
    from advent.gui import CanvasPainter
    from advent.vocabulary import Object

    # tkinter's Tcl interpreter cannot initialise while pytest replaces the
    # process's file descriptors, so suspend fd capture for the window tests.
    with capfd.disabled():
        root = new_root()
        root.withdraw()
        canvas = tk.Canvas(root, width=400, height=240)
        try:
            for loc in scenes.SCENES:
                canvas.delete("all")
                art.draw_scene(
                    CanvasPainter(canvas, 400, 240),
                    scenes.scene_for(loc),
                    dark=bool(loc % 2),
                )
                assert canvas.find_all(), loc
            for obj in range(1, int(Object.CHAIN) + 1):
                canvas.delete("all")
                art.draw_item(
                    CanvasPainter(canvas, 60, 60, 100, 100),
                    obj,
                    50,
                    50,
                    84,
                    state=0,
                    lit=True,
                )
                assert canvas.find_all(), obj
        finally:
            root.destroy()


def test_window_plays_a_few_moves(capfd) -> None:
    from advent.gui import AdventureApp
    from advent.vocabulary import Location, Object

    with capfd.disabled():
        try:
            app = AdventureApp(seed=7)
        except tk.TclError as exc:
            pytest.skip("tkinter cannot open a display: %s" % exc)
        try:
            pump_until(app, lambda: app.awaiting)
            assert app.scene.find_all(), "the opening scene was not painted"
            assert app.log.get("1.0", "end").strip(), "the narration pane is empty"
            assert app.question is True

            # A scene shortcut must not answer the welcome question with "No".
            app._scene_key("n")
            assert app.awaiting and app.question
            assert app.session is not None and app.session.game is not None
            assert app.session.game.hinted[0] is False

            # Only y/n are accepted while a question is open.
            app._submit("house")
            assert app.awaiting and app.question
            assert "Please answer Yes or No." in app.log.get("1.0", "end")

            app._submit("n")
            pump_until(app, lambda: app.awaiting and not app.question)
            exits = [
                child for child in app.exits.winfo_children() if isinstance(child, tk.Button)
            ]
            assert exits and any(button.cget("state") == "normal" for button in exits)

            app._submit("house")
            pump_until(app, lambda: app.awaiting)
            assert app.session is not None and app.session.game is not None
            assert app.session.game.loc == int(Location.HOUSE)

            app._submit("take keys")
            pump_until(app, lambda: app.awaiting)
            assert int(Object.KEYS) in app.session.game.inventory()

            app.select(int(Object.LAMP))
            assert app.verb_buttons["take"].cget("state") == "normal"
            app._run_action("take")
            pump_until(app, lambda: app.awaiting)
            assert int(Object.LAMP) in app.session.game.inventory()
            assert "> take lamp" in app.log.get("1.0", "end")
        finally:
            close(app)


def test_dark_snapshot_hides_room_objects(capfd) -> None:
    from advent.gui import AdventureApp
    from advent.session import GameSnapshot
    from advent.vocabulary import Location, Motion, Object

    with capfd.disabled():
        try:
            app = AdventureApp(seed=7)
        except tk.TclError as exc:
            pytest.skip("tkinter cannot open a display: %s" % exc)
        try:
            pump_until(app, lambda: app.awaiting)
            app.snapshot = GameSnapshot(
                loc=int(Location.DEBRIS),
                oldloc=int(Location.ROAD),
                dark=True,
                here=(int(Object.KEYS),),
                inventory=(),
                motions=(int(Motion.W),),
                turns=4,
                bottle=0,
                lamp=0,
            )
            app._refresh_view()
            assert app.scene.find_all(), "the dark scene was not painted"
            assert app.hit_boxes == [], "objects must not be clickable in the dark"
        finally:
            close(app)


def test_new_game_resets_the_window(capfd) -> None:
    from advent.gui import AdventureApp

    with capfd.disabled():
        try:
            app = AdventureApp(seed=7)
        except tk.TclError as exc:
            pytest.skip("tkinter cannot open a display: %s" % exc)
        try:
            pump_until(app, lambda: app.awaiting)
            old = app.session
            assert old is not None

            app.new_game()
            assert app.session is not old
            assert app.snapshot is None
            assert app.awaiting is False
            assert app.question is False
            assert not app.yes_button.winfo_ismapped()
            assert not app.no_button.winfo_ismapped()

            pump_until(app, lambda: app.awaiting)
            assert app.session is not old
            assert app.session is not None
            assert old is not None and not old.running
        finally:
            close(app)


def test_close_stops_the_engine(capfd) -> None:
    from advent.gui import AdventureApp

    with capfd.disabled():
        try:
            app = AdventureApp(seed=7)
        except tk.TclError as exc:
            pytest.skip("tkinter cannot open a display: %s" % exc)
        try:
            pump_until(app, lambda: app.awaiting)
            session = app.session
            assert session is not None
            app._on_close()
            assert not session.running
        finally:
            close(app)
