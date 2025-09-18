"""Minimal PDF-like writer used for tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class SimplePDF:
    """Simple text-based PDF surrogate for unit testing."""

    _lines: List[str] = field(default_factory=list)

    def add_page(self) -> None:
        self._lines.append("--- PAGE BREAK ---")

    def set_font(self, *_args, **_kwargs) -> None:  # pragma: no cover - no-op
        return None

    def cell(self, _w: int, _h: int, txt: str, ln: bool = False, align: str = "L") -> None:
        line = f"{align}:{txt}"
        self._lines.append(line)
        if ln:
            self._lines.append("")

    def ln(self, _h: int = 0) -> None:
        self._lines.append("")

    def multi_cell(self, _w: int, _h: int, txt: str) -> None:
        for part in txt.split("\n"):
            self._lines.append(part)

    def output(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(self._lines))
