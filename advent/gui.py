"""Graphical front end for Adventure (tkinter, standard library only).

The window is a point-and-click reading of the same game:

* the large canvas paints the current location with the vector art in
  :mod:`advent.art`, and draws the objects that are here;
* clicking an object selects it, and the verb buttons send ordinary engine
  commands such as ``take keys``;
* the exit bar offers the motions that could work from here;
* the narration pane reproduces every line the engine prints, and the command
  entry still accepts the original two-word vocabulary.

Nothing about the game's rules changes: every button ultimately submits a line
to the same :class:`~advent.game.Game` that ``python -m advent`` uses.
"""

from __future__ import annotations

import argparse
import gc
import sys
import tkinter as tk
from collections.abc import Sequence

from . import art, scenes
from . import data as D
from .session import DONE, PROMPT, WRITE, EngineSession, GameSnapshot
from .vocabulary import Location, Motion, Object

BG = "#14121a"
PANEL = "#1c1924"
CARD = "#26222e"
CARD_SELECTED = "#3a3346"
TEXT = "#ddd8cc"
MUTED = "#8f8a7a"
ACCENT = "#d9b64a"
BLUE = "#7fb2e5"
WARN = "#d98b6a"
FONT = "Segoe UI"
MONO = "Consolas"

#: How many portable objects are drawn in the scene; the side panel lists all.
MAX_SCENE_ITEMS = 8

_UNSET = object()

#: ``(button label, engine verb)`` for the object actions.
VERBS: tuple[tuple[str, str], ...] = (
    ("Take", "take"),
    ("Drop", "drop"),
    ("Open", "open"),
    ("Close", "close"),
    ("Light", "on"),
    ("Out", "off"),
    ("Wave", "wave"),
    ("Rub", "rub"),
    ("Eat", "eat"),
    ("Drink", "drink"),
    ("Fill", "fill"),
    ("Pour", "pour"),
    ("Break", "break"),
    ("Read", "read"),
    ("Feed", "feed"),
    ("Wake", "wake"),
    ("Throw", "toss"),
    ("Attack", "kill"),
    ("Calm", "calm"),
    ("Blast", "blast"),
)


class CanvasPainter:
    """A :class:`advent.art.Painter` that draws on a tkinter canvas."""

    def __init__(
        self,
        canvas: tk.Canvas,
        width: float,
        height: float,
        logical_w: float = art.LOGICAL_W,
        logical_h: float = art.LOGICAL_H,
    ) -> None:
        self.canvas = canvas
        self.sx = max(1e-6, width / logical_w)
        self.sy = max(1e-6, height / logical_h)
        self.unit = min(self.sx, self.sy)

    # -- helpers -----------------------------------------------------------

    def _flat(self, points: Sequence[tuple[float, float]]) -> list[float]:
        coords: list[float] = []
        for x, y in points:
            coords.append(x * self.sx)
            coords.append(y * self.sy)
        return coords

    def _width(self, width: float) -> float:
        return max(1.0, width * self.unit)

    @staticmethod
    def _stipple(stipple: str | None) -> dict[str, str]:
        return {"stipple": stipple} if stipple else {}

    # -- Painter -----------------------------------------------------------

    def rect(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        *,
        fill: str | None = None,
        outline: str | None = None,
        width: float = 1,
        stipple: str | None = None,
    ) -> None:
        self.canvas.create_rectangle(
            x0 * self.sx,
            y0 * self.sy,
            x1 * self.sx,
            y1 * self.sy,
            fill=fill or "",
            outline=outline or "",
            width=self._width(width),
            **self._stipple(stipple),
        )

    def oval(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        *,
        fill: str | None = None,
        outline: str | None = None,
        width: float = 1,
        stipple: str | None = None,
    ) -> None:
        self.canvas.create_oval(
            x0 * self.sx,
            y0 * self.sy,
            x1 * self.sx,
            y1 * self.sy,
            fill=fill or "",
            outline=outline or "",
            width=self._width(width),
            **self._stipple(stipple),
        )

    def polygon(
        self,
        points: Sequence[tuple[float, float]],
        *,
        fill: str | None = None,
        outline: str | None = None,
        width: float = 1,
        stipple: str | None = None,
        smooth: bool = False,
    ) -> None:
        if len(points) < 3:
            return
        self.canvas.create_polygon(
            self._flat(points),
            fill=fill or "",
            outline=outline or "",
            width=self._width(width),
            smooth=smooth,
            **self._stipple(stipple),
        )

    def line(
        self,
        points: Sequence[tuple[float, float]],
        fill: str,
        *,
        width: float = 1,
        smooth: bool = False,
    ) -> None:
        if len(points) < 2:
            return
        self.canvas.create_line(
            self._flat(points),
            fill=fill,
            width=self._width(width),
            smooth=smooth,
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND,
        )

    def text(
        self,
        x: float,
        y: float,
        text: str,
        *,
        fill: str,
        size: float = 14,
        anchor: str = "center",
        bold: bool = False,
    ) -> None:
        px = max(6, int(round(size * self.unit)))
        self.canvas.create_text(
            x * self.sx,
            y * self.sy,
            text=text,
            fill=fill,
            anchor=anchor,
            font=(FONT, -px, "bold" if bold else "normal"),
        )


class AdventureApp(tk.Tk):
    """The main window."""

    def __init__(self, seed: int | None = None) -> None:
        super().__init__()
        self.title("Adventure — Colossal Cave")
        self.geometry("1280x900")
        self.minsize(1020, 760)
        self.configure(bg=BG)
        self.seed = seed
        self.session: EngineSession | None = None
        self.snapshot: GameSnapshot | None = None
        self.selected: int | None = None
        self.awaiting = False
        self.question = False
        self.history: list[str] = []
        self.history_pos = 0
        self.hit_boxes: list[tuple[float, float, float, float, int]] = []
        self.verb_buttons: dict[str, tk.Button] = {}
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.new_game()
        self.after(40, self._poll)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=5)
        self.grid_rowconfigure(2, weight=2)

        top = tk.Frame(self, bg=PANEL)
        top.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        for label, command in (
            ("New game", self.new_game),
            ("Look", lambda: self._submit("look")),
            ("Inventory", lambda: self._submit("inventory")),
            ("Score", lambda: self._submit("score")),
            ("Help", lambda: self._submit("help")),
            ("Brief", lambda: self._submit("brief")),
            ("Quit", lambda: self._submit("quit")),
        ):
            button = self._button(top, label, command)
            button.pack(side="left", padx=3)
        self.status = tk.Label(top, text="", bg=PANEL, fg=MUTED, font=(FONT, 9))
        self.status.pack(side="right", padx=8)

        main = tk.Frame(self, bg=BG)
        main.grid(row=1, column=0, sticky="nsew", padx=8)
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=0, minsize=400)
        main.grid_rowconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=0)

        self.scene = tk.Canvas(
            main,
            bg="#000000",
            highlightthickness=0,
            width=840,
            height=505,
            takefocus=1,
        )
        self.scene.grid(row=0, column=0, sticky="nsew")
        self.scene.bind("<Configure>", lambda _event: self._draw_scene())
        self.scene.bind("<Button-1>", self._on_scene_click)
        self.scene.bind("<Double-Button-1>", lambda _event: self._submit("look"))
        self.scene.bind("<Up>", lambda _event: self._scene_key("n"))
        self.scene.bind("<Down>", lambda _event: self._scene_key("s"))
        self.scene.bind("<Left>", lambda _event: self._scene_key("w"))
        self.scene.bind("<Right>", lambda _event: self._scene_key("e"))
        self.scene.bind("<Shift-Up>", lambda _event: self._scene_key("up"))
        self.scene.bind("<Shift-Down>", lambda _event: self._scene_key("down"))

        self.exits = tk.Frame(main, bg=BG)
        self.exits.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        for column in range(9):
            self.exits.grid_columnconfigure(column, weight=1)

        self._build_side(main)
        self._build_log()
        self._build_entry()

    def _button(self, parent: tk.Misc, label: str, command, **kwargs) -> tk.Button:
        return tk.Button(
            parent,
            text=label,
            command=command,
            bg="#2a2533",
            fg=TEXT,
            activebackground="#3f3752",
            activeforeground="#ffffff",
            disabledforeground="#5c5768",
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
            font=(FONT, 9),
            **kwargs,
        )

    def _build_side(self, main: tk.Frame) -> None:
        holder = tk.Frame(main, bg=PANEL, width=400)
        holder.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        holder.grid_propagate(False)
        holder.grid_rowconfigure(0, weight=1)
        holder.grid_columnconfigure(0, weight=1)
        self.side_canvas = tk.Canvas(holder, bg=PANEL, highlightthickness=0)
        self.side_canvas.grid(row=0, column=0, sticky="nsew")
        side_scroll = tk.Scrollbar(holder, orient="vertical", command=self.side_canvas.yview)
        side_scroll.grid(row=0, column=1, sticky="ns")
        self.side_canvas.configure(yscrollcommand=side_scroll.set)

        side = tk.Frame(self.side_canvas, bg=PANEL, padx=10, pady=10)
        self.side_window = self.side_canvas.create_window((0, 0), window=side, anchor="nw")
        side.bind(
            "<Configure>",
            lambda _event: self.side_canvas.configure(scrollregion=self.side_canvas.bbox("all")),
        )
        self.side_canvas.bind(
            "<Configure>",
            lambda event: self.side_canvas.itemconfigure(self.side_window, width=event.width),
        )
        self.side_canvas.bind("<MouseWheel>", self._scroll_side)
        side.grid_columnconfigure(0, weight=1)

        tk.Label(
            side, text="IN THIS PLACE", bg=PANEL, fg=ACCENT, font=(FONT, 9, "bold"), anchor="w"
        ).grid(row=0, column=0, sticky="ew")

        here_box = tk.Frame(side, bg=PANEL)
        here_box.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        here_box.grid_columnconfigure(0, weight=1)
        here_box.grid_rowconfigure(0, weight=1)
        self.here_canvas = tk.Canvas(here_box, bg=PANEL, highlightthickness=0, height=196)
        self.here_canvas.grid(row=0, column=0, sticky="nsew")
        here_scroll = tk.Scrollbar(here_box, orient="vertical", command=self.here_canvas.yview)
        here_scroll.grid(row=0, column=1, sticky="ns")
        self.here_canvas.configure(yscrollcommand=here_scroll.set)
        self.here_inner = tk.Frame(self.here_canvas, bg=PANEL)
        self.here_window = self.here_canvas.create_window((0, 0), window=self.here_inner, anchor="nw")
        self.here_inner.bind(
            "<Configure>",
            lambda _event: self.here_canvas.configure(scrollregion=self.here_canvas.bbox("all")),
        )
        self.here_canvas.bind(
            "<Configure>",
            lambda event: self.here_canvas.itemconfigure(self.here_window, width=event.width),
        )
        for widget in (self.here_canvas, self.here_inner):
            widget.bind("<MouseWheel>", self._scroll_here)

        tk.Label(
            side, text="YOU ARE CARRYING", bg=PANEL, fg=ACCENT, font=(FONT, 9, "bold"), anchor="w"
        ).grid(row=2, column=0, sticky="ew", pady=(12, 4))
        self.inv_frame = tk.Frame(side, bg=PANEL)
        self.inv_frame.grid(row=3, column=0, sticky="ew")
        for column in range(5):
            self.inv_frame.grid_columnconfigure(column, weight=1)

        self.sel_label = tk.Label(
            side,
            text="Nothing selected — click an object",
            bg=PANEL,
            fg=TEXT,
            font=(FONT, 9, "italic"),
            anchor="w",
            wraplength=360,
            justify="left",
        )
        self.sel_label.grid(row=4, column=0, sticky="ew", pady=(12, 4))

        self.verb_frame = tk.Frame(side, bg=PANEL)
        self.verb_frame.grid(row=5, column=0, sticky="ew")
        for column in range(4):
            self.verb_frame.grid_columnconfigure(column, weight=1)
        for index, (label, verb) in enumerate(VERBS):
            button = self._button(self.verb_frame, label, lambda v=verb: self._run_action(v))
            button.grid(row=index // 4, column=index % 4, sticky="ew", padx=2, pady=2)
            button.configure(state="disabled")
            self.verb_buttons[verb] = button

        side.grid_rowconfigure(1, weight=1)

    def _build_log(self) -> None:
        frame = tk.Frame(self, bg=BG)
        frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=(8, 0))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        self.log = tk.Text(
            frame,
            height=8,
            wrap="word",
            state="disabled",
            bg="#0e0d12",
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            padx=10,
            pady=8,
            font=(MONO, 10),
        )
        self.log.grid(row=0, column=0, sticky="nsew")
        scroll = tk.Scrollbar(frame, orient="vertical", command=self.log.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.log.configure(yscrollcommand=scroll.set)
        self.log.tag_configure("prompt", foreground=MUTED, font=(MONO, 10, "italic"))
        self.log.tag_configure("command", foreground=BLUE, font=(MONO, 10, "bold"))
        self.log.tag_configure("system", foreground=WARN, font=(MONO, 10, "italic"))

    def _build_entry(self) -> None:
        bar = tk.Frame(self, bg=PANEL)
        bar.grid(row=3, column=0, sticky="ew", padx=8, pady=8)
        bar.grid_columnconfigure(1, weight=1)
        self.prompt_label = tk.Label(
            bar, text="*", bg=PANEL, fg=ACCENT, font=(MONO, 12, "bold"), width=2
        )
        self.prompt_label.grid(row=0, column=0, padx=(6, 2))
        self.entry = tk.Entry(
            bar,
            bg="#0e0d12",
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=(MONO, 11),
        )
        self.entry.grid(row=0, column=1, sticky="ew", ipady=5, padx=4)
        self.entry.bind("<Return>", self._on_entry_return)
        self.entry.bind("<Up>", self._history_up)
        self.entry.bind("<Down>", self._history_down)
        self.send_button = self._button(bar, "Send", self._on_send)
        self.send_button.grid(row=0, column=2, padx=4)
        self.yes_button = self._button(bar, "Yes", lambda: self._submit("y"))
        self.no_button = self._button(bar, "No", lambda: self._submit("n"))
        self.yes_button.grid(row=0, column=3, padx=(10, 3))
        self.no_button.grid(row=0, column=4, padx=(0, 6))
        self.yes_button.grid_remove()
        self.no_button.grid_remove()

    # ------------------------------------------------------------------
    # Game lifecycle
    # ------------------------------------------------------------------

    def new_game(self, seed: int | None | object = _UNSET) -> None:
        if seed is _UNSET:
            seed = self.seed
        if self.session is not None:
            self.session.stop()
            self.session.join(0.5)
        self.snapshot = None
        self.selected = None
        self.awaiting = False
        self.question = False
        self.history.clear()
        self.history_pos = 0
        self.hit_boxes.clear()
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self.yes_button.grid_remove()
        self.no_button.grid_remove()
        self._set_exits_enabled(False)
        self._set_input_enabled(True)
        self.prompt_label.configure(text="…")
        self.session = EngineSession(seed=seed).start()  # type: ignore[arg-type]
        self._refresh_view()

    def _on_close(self) -> None:
        if self.session is not None:
            self.session.stop()
            self.session.join(0.3)
        self.destroy()
        # Tk widgets form reference cycles.  Collect them here, on the thread
        # that owns Tcl, rather than letting the engine thread's collector find
        # them and enter Tcl from the wrong thread.
        gc.collect()

    # ------------------------------------------------------------------
    # Engine messages
    # ------------------------------------------------------------------

    def _poll(self) -> None:
        try:
            session = self.session
            if session is not None:
                for event in session.drain():
                    if event.kind == WRITE:
                        self._append(event.payload or "")
                    elif event.kind == PROMPT:
                        self.snapshot = event.snapshot
                        self._on_prompt(event.payload or "* ")
                    elif event.kind == DONE:
                        self.snapshot = event.snapshot
                        self._on_done()
        except Exception as exc:  # noqa: BLE001 - keep the window responsive
            try:
                self._append(
                    "\n[Interface error: %s: %s]\n" % (type(exc).__name__, exc),
                    "system",
                )
            except tk.TclError:
                pass
        finally:
            try:
                self.after(40, self._poll)
            except tk.TclError:
                pass

    def report_callback_exception(self, exc_type, exc_value, _traceback) -> None:
        """Show callback failures in the narration pane instead of only stderr."""
        try:
            self._append(
                "\n[Interface error: %s: %s]\n" % (exc_type.__name__, exc_value),
                "system",
            )
        except tk.TclError:
            pass

    def _on_prompt(self, prompt: str) -> None:
        self.awaiting = True
        self.question = prompt.rstrip().endswith("**")
        if self.question:
            text = prompt.rstrip()
            if text.endswith("**"):
                text = text[:-2]
            self._append("\n" + text.rstrip() + "\n", "prompt")
            self.prompt_label.configure(text="?")
            self.yes_button.grid()
            self.no_button.grid()
        else:
            self.prompt_label.configure(text="*")
            self.yes_button.grid_remove()
            self.no_button.grid_remove()
        self._set_input_enabled(True)
        self.entry.focus_set()
        self._refresh_view()

    def _on_done(self) -> None:
        self.awaiting = False
        self.question = False
        self.prompt_label.configure(text="—")
        self.yes_button.grid_remove()
        self.no_button.grid_remove()
        self._append("\n[The adventure is over.  Choose “New game” to play again.]\n", "system")
        self._set_input_enabled(False)
        self._refresh_view()

    def _append(self, text: str, tag: str | None = None) -> None:
        if not text:
            return
        self.log.configure(state="normal")
        self.log.insert("end", text, tag or ())
        self.log.see("end")
        self.log.configure(state="disabled")

    def _set_input_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.entry.configure(state=state)
        self.send_button.configure(state=state)
        if not enabled:
            for button in self.verb_buttons.values():
                button.configure(state="disabled")

    def _set_exits_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for child in self.exits.winfo_children():
            if isinstance(child, tk.Button):
                child.configure(state=state)

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    def _scene_key(self, command: str) -> str:
        """Arrow keys move, but never answer a yes/no question."""
        if self.awaiting and not self.question:
            self._submit(command)
        else:
            self.entry.focus_set()
        return "break"

    def _on_entry_return(self, _event: tk.Event) -> None:
        self._on_send()

    def _on_send(self) -> None:
        self._submit(self.entry.get())

    def _submit(self, line: str) -> None:
        line = line.strip()
        if not line or not self.awaiting or self.session is None:
            return
        if self.question:
            # The engine reads only the first letter here; keep the window to
            # the same Yes/No contract instead of letting "north" mean "No".
            if line[:1].lower() not in ("y", "n"):
                self._append("\n[Please answer Yes or No.]\n", "system")
                return
        self._append("\n> " + line + "\n", "command")
        self.history.append(line)
        self.history_pos = len(self.history)
        self.entry.delete(0, "end")
        self.awaiting = False
        self.question = False
        self.prompt_label.configure(text="…")
        self.yes_button.grid_remove()
        self.no_button.grid_remove()
        self._render_verbs()
        self._set_exits_enabled(False)
        self.session.submit(line)

    def _run_action(self, verb: str) -> None:
        obj = self.selected
        if obj is None:
            return
        word = scenes.item_word(obj)
        if word is None:
            self._append(
                "\n[The original vocabulary has no word for the %s.]\n"
                % scenes.item_label(obj).lower(),
                "system",
            )
            return
        self._submit("%s %s" % (verb, word))

    def _quick_take(self, obj: int) -> None:
        word = scenes.item_word(obj)
        if word:
            self._submit("take " + word)

    def _quick_drop(self, obj: int) -> None:
        word = scenes.item_word(obj)
        if word:
            self._submit("drop " + word)

    def _history_up(self, _event: tk.Event) -> str:
        if not self.history:
            return "break"
        self.history_pos = max(0, self.history_pos - 1)
        self.entry.delete(0, "end")
        self.entry.insert(0, self.history[self.history_pos])
        return "break"

    def _history_down(self, _event: tk.Event) -> str:
        if not self.history:
            return "break"
        self.history_pos = min(len(self.history), self.history_pos + 1)
        self.entry.delete(0, "end")
        if self.history_pos < len(self.history):
            self.entry.insert(0, self.history[self.history_pos])
        return "break"

    def _scroll_here(self, event: tk.Event) -> str:
        self.here_canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
        return "break"

    def _scroll_side(self, event: tk.Event) -> str:
        self.side_canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
        return "break"

    # ------------------------------------------------------------------
    # View
    # ------------------------------------------------------------------

    def _refresh_view(self) -> None:
        snapshot = self.snapshot
        if snapshot is not None and self.selected is not None:
            if self.selected not in snapshot.here and self.selected not in snapshot.inventory:
                self.selected = None
        self._draw_scene()
        self._render_here(snapshot)
        self._render_inventory(snapshot)
        self._render_exits(snapshot)
        self._render_verbs()
        if snapshot is None:
            self.status.configure(text="starting…")
        else:
            self.status.configure(
                text="Turn %d   ·   Carrying %d" % (snapshot.turns, len(snapshot.inventory))
            )
        # The panels were rebuilt; collect their old Tk widgets on this thread.
        gc.collect()

    def _draw_scene(self) -> None:
        canvas = self.scene
        if not canvas.winfo_exists():
            return
        canvas.delete("all")
        self.hit_boxes = []
        width = max(1, canvas.winfo_width())
        height = max(1, canvas.winfo_height())
        painter = CanvasPainter(canvas, width, height)
        snapshot = self.snapshot
        loc = snapshot.loc if snapshot is not None else int(Location.ROAD)
        dark = snapshot.dark if snapshot is not None else False
        art.draw_scene(painter, scenes.scene_for(loc), dark=dark)
        if snapshot is None:
            return
        self._draw_caption(painter, snapshot.loc)
        if not dark:
            self._draw_here_objects(painter, snapshot)

    def _draw_caption(self, painter: CanvasPainter, loc: int) -> None:
        info = D.LOCATIONS.get(loc)
        if info is None:
            return
        title = (info.short or info.long or "").replace("\n", " ").strip()
        if not title:
            return
        title = title[:72]
        box_width = min(760.0, 26 + len(title) * 9.4)
        painter.rect(18, 14, 18 + box_width, 54, fill="#0b0a10", outline=ACCENT, width=2)
        painter.text(32, 34, title, fill="#e8e2d2", size=17, anchor="w")

    def _draw_here_objects(self, painter: CanvasPainter, snapshot: GameSnapshot) -> None:
        here = snapshot.here
        actors = [obj for obj in here if scenes.is_actor(obj)]
        small = [obj for obj in here if not scenes.is_actor(obj)]
        shown = small[:MAX_SCENE_ITEMS]

        for obj in actors:
            slot = scenes.ACTOR_SLOTS[obj]
            cx = slot[0] * art.LOGICAL_W
            cy = slot[1] * art.LOGICAL_H
            size = 320.0 * slot[2]
            self._draw_object(painter, snapshot, obj, cx, cy, size, label_size=16)
            half = size * 0.46
            self.hit_boxes.append((cx - half, cy - half, cx + half, cy + half, obj))

        positions = self._item_positions(len(shown))
        for obj, (cx, cy) in zip(shown, positions):
            size = 84.0
            self._draw_object(painter, snapshot, obj, cx, cy, size, label_size=12)
            half = size * 0.62
            self.hit_boxes.append((cx - half, cy - half, cx + half, cy + half, obj))

        hidden = len(small) - len(shown)
        if hidden:
            painter.text(
                500.0,
                580.0,
                "and %d more — the list on the right shows everything here" % hidden,
                fill="#050408",
                size=14,
            )
            painter.text(
                500.0,
                579.0,
                "and %d more — the list on the right shows everything here" % hidden,
                fill="#f0ead8",
                size=14,
            )

    def _draw_object(
        self,
        painter: CanvasPainter,
        snapshot: GameSnapshot,
        obj: int,
        cx: float,
        cy: float,
        size: float,
        label_size: float,
    ) -> None:
        state = snapshot.bottle if obj == int(Object.BOTTLE) else None
        lit = obj == int(Object.LAMP) and snapshot.lamp != 0
        art.draw_item(painter, obj, cx, cy, size, state=state, lit=lit)
        label = scenes.item_label(obj)
        painter.text(cx + 1, cy + size * 0.5 + label_size + 2, label, fill="#050408", size=label_size, anchor="n")
        painter.text(cx, cy + size * 0.5 + label_size, label, fill="#f0ead8", size=label_size, anchor="n")
        if self.selected == obj:
            radius = size * 0.60
            painter.oval(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                fill=None,
                outline=ACCENT,
                width=3,
            )

    @staticmethod
    def _item_positions(count: int) -> list[tuple[float, float]]:
        if count <= 0:
            return []
        columns = min(4, count)
        positions: list[tuple[float, float]] = []
        for index in range(count):
            row, column = divmod(index, columns)
            in_row = min(columns, count - row * columns)
            x = 500.0 + (column - (in_row - 1) / 2.0) * 172.0
            y = 508.0 - row * 98.0
            positions.append((x, y))
        return positions

    def _on_scene_click(self, event: tk.Event) -> None:
        self.scene.focus_set()
        width = max(1, self.scene.winfo_width())
        height = max(1, self.scene.winfo_height())
        x = event.x * art.LOGICAL_W / width
        y = event.y * art.LOGICAL_H / height
        for x0, y0, x1, y1, obj in reversed(self.hit_boxes):
            if x0 <= x <= x1 and y0 <= y <= y1:
                self.select(obj)
                return
        self.select(None)

    def select(self, obj: int | None) -> None:
        self.selected = obj
        snapshot = self.snapshot
        self._render_here(snapshot)
        self._render_inventory(snapshot)
        self._render_verbs()
        self._draw_scene()
        gc.collect()

    # -- side panel --------------------------------------------------------

    def _paint_item_icon(
        self, canvas: tk.Canvas, obj: int, size: int, snapshot: GameSnapshot
    ) -> None:
        canvas.delete("all")
        painter = CanvasPainter(canvas, size, size, 100.0, 100.0)
        state = snapshot.bottle if obj == int(Object.BOTTLE) else None
        lit = obj == int(Object.LAMP) and snapshot.lamp != 0
        art.draw_item(painter, obj, 50.0, 50.0, 84.0, state=state, lit=lit)

    def _render_here(self, snapshot: GameSnapshot | None) -> None:
        for child in self.here_inner.winfo_children():
            child.destroy()
        if snapshot is None:
            self._here_note("Waiting for the game…")
            return
        if snapshot.dark:
            self._here_note("It is now pitch dark.")
            return
        here = snapshot.here
        if not here:
            self._here_note("Nothing of interest.")
            return
        for obj in here:
            selected = obj == self.selected
            card = tk.Frame(
                self.here_inner,
                bg=CARD_SELECTED if selected else CARD,
                highlightthickness=1,
                highlightbackground=ACCENT if selected else PANEL,
            )
            card.pack(fill="x", pady=2)
            icon = tk.Canvas(
                card, width=46, height=46, bg=card["bg"], highlightthickness=0
            )
            icon.pack(side="left", padx=(5, 7), pady=3)
            self._paint_item_icon(icon, obj, 46, snapshot)
            text = tk.Frame(card, bg=card["bg"])
            text.pack(side="left", fill="x", expand=True)
            name = tk.Label(
                text,
                text=scenes.item_label(obj),
                bg=card["bg"],
                fg=TEXT,
                anchor="w",
                font=(FONT, 9),
            )
            name.pack(fill="x")
            hint = "double-click to take" if scenes.item_word(obj) else "no command word"
            sub = tk.Label(
                text,
                text=hint,
                bg=card["bg"],
                fg=MUTED,
                anchor="w",
                font=(FONT, 7),
            )
            sub.pack(fill="x")
            for widget in (card, icon, text, name, sub):
                widget.bind("<Button-1>", lambda _event, o=obj: self.select(o))
                widget.bind("<Double-Button-1>", lambda _event, o=obj: self._quick_take(o))
                widget.bind("<MouseWheel>", self._scroll_here)

    def _here_note(self, text: str) -> None:
        tk.Label(
            self.here_inner,
            text=text,
            bg=PANEL,
            fg=MUTED,
            anchor="w",
            font=(FONT, 9, "italic"),
        ).pack(fill="x", pady=4)

    def _render_inventory(self, snapshot: GameSnapshot | None) -> None:
        for child in self.inv_frame.winfo_children():
            child.destroy()
        items = list(snapshot.inventory) if snapshot is not None else []
        if not items:
            tk.Label(
                self.inv_frame,
                text="Nothing at all.",
                bg=PANEL,
                fg=MUTED,
                anchor="w",
                font=(FONT, 9, "italic"),
            ).grid(row=0, column=0, sticky="ew")
            return
        for index, obj in enumerate(items):
            selected = obj == self.selected
            background = CARD_SELECTED if selected else CARD
            holder = tk.Frame(
                self.inv_frame,
                bg=background,
                highlightthickness=1,
                highlightbackground=ACCENT if selected else PANEL,
            )
            holder.grid(row=index // 5, column=index % 5, padx=2, pady=2, sticky="nsew")
            icon = tk.Canvas(holder, width=42, height=42, bg=background, highlightthickness=0)
            icon.pack(padx=2, pady=(2, 0))
            self._paint_item_icon(icon, obj, 42, snapshot)  # type: ignore[arg-type]
            label = tk.Label(
                holder,
                text=scenes.item_label(obj),
                bg=background,
                fg=TEXT,
                font=(FONT, 6),
                wraplength=62,
                justify="center",
            )
            label.pack(padx=1, pady=(0, 2))
            for widget in (holder, icon, label):
                widget.bind("<Button-1>", lambda _event, o=obj: self.select(o))
                widget.bind("<Double-Button-1>", lambda _event, o=obj: self._quick_drop(o))

    def _render_verbs(self) -> None:
        obj = self.selected
        word = scenes.item_word(obj) if obj is not None else None
        enabled = bool(word) and self.awaiting and not self.question
        for button in self.verb_buttons.values():
            button.configure(state="normal" if enabled else "disabled")
        if obj is None:
            self.sel_label.configure(text="Nothing selected — click an object")
        elif word is None:
            self.sel_label.configure(
                text="Selected: %s  (the original vocabulary has no word for it)"
                % scenes.item_label(obj)
            )
        else:
            self.sel_label.configure(text="Selected: %s" % scenes.item_label(obj))

    def _render_exits(self, snapshot: GameSnapshot | None) -> None:
        for child in self.exits.winfo_children():
            child.destroy()
        if snapshot is None:
            return
        buttons: list[tuple[str, str]] = [("Look", "look")]
        for motion in scenes.sorted_motions(list(snapshot.motions)):
            if motion == int(Motion.LOOK):
                continue
            if motion == int(Motion.BACK) and snapshot.oldloc == snapshot.loc:
                continue
            buttons.append((scenes.motion_label(motion), scenes.motion_command(motion)))
        row = 0
        if len(buttons) == 1:
            tk.Label(
                self.exits,
                text="No obvious exits — try the command line.",
                bg=BG,
                fg=MUTED,
                font=(FONT, 9, "italic"),
            ).grid(row=1, column=0, columnspan=9, sticky="w", padx=4)
        for index, (label, command) in enumerate(buttons):
            button = self._button(self.exits, label, lambda c=command: self._submit(c))
            if not self.awaiting or self.question:
                button.configure(state="disabled")
            button.grid(row=row + index // 9, column=index % 9, sticky="ew", padx=2, pady=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m advent --gui",
        description="Adventure (Colossal Cave) with a graphical front end.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        metavar="N",
        help="seed the random number generator (default: from the clock)",
    )
    return parser


def run(seed: int | None = None) -> int:
    """Open the window and play until it is closed."""
    try:
        app = AdventureApp(seed=seed)
    except tk.TclError as exc:  # no display, or tkinter built without Tk
        print("Cannot open a window: %s" % exc, file=sys.stderr)
        return 2
    app.mainloop()
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(seed=args.seed)


if __name__ == "__main__":
    sys.exit(main())
