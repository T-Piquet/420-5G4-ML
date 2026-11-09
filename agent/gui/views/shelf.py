"""Rayon de bibliothèque dessiné : un dos de livre par ouvrage."""
import tkinter as tk
import zlib
from collections.abc import Sequence
from dataclasses import dataclass

from gui.views import theme

_MAX_SCALE = 1.5
_MIN_SPINE_WIDTH = 2
_GAP = 2
_SHELF_THICKNESS = 5
_TOP_MARGIN = 6


@dataclass(frozen=True)
class Spine:
    title: str
    on_shelf: bool


class Shelf(tk.Canvas):
    """Les livres disponibles sont pleins ; un livre emprunté laisse sa silhouette."""

    def __init__(self, master, height: int = 118) -> None:
        super().__init__(master, height=height, bg=theme.SURFACE, highlightthickness=0)
        self._spines: Sequence[Spine] = ()
        self.bind("<Configure>", lambda _event: self._draw())

    def show(self, spines: Sequence[Spine]) -> None:
        self._spines = spines
        self._draw()

    def _draw(self) -> None:
        self.delete("all")
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()
        if canvas_width <= 1:
            return
        base = canvas_height - _SHELF_THICKNESS
        self.create_rectangle(0, base, canvas_width, canvas_height, fill=theme.INK, width=0)
        if not self._spines:
            return

        seeds = [zlib.crc32(spine.title.encode("utf-8")) for spine in self._spines]
        widths = [12 + seed % 4 * 3 for seed in seeds]
        room = canvas_width - _GAP * (len(widths) + 1)
        scale = min(_MAX_SCALE, room / sum(widths))
        max_height = base - _TOP_MARGIN

        x = float(_GAP)
        for spine, seed, width in zip(self._spines, seeds, widths):
            spine_width = max(_MIN_SPINE_WIDTH, width * scale)
            top = base - max_height * (0.72 + (seed >> 8) % 28 / 100)
            if spine.on_shelf:
                color = theme.SPINE_COLORS[(seed >> 16) % len(theme.SPINE_COLORS)]
                self.create_rectangle(x, top, x + spine_width, base, fill=color, width=0)
            else:
                self.create_rectangle(
                    x + 1, top, x + spine_width - 1, base - 1,
                    fill=theme.OCHRE_PALE, outline=theme.OCHRE, dash=(3, 2),
                )
            x += spine_width + _GAP
