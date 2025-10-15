"""Module entry point for `python -m automation.execplan`."""

from __future__ import annotations

from .cli import main


if __name__ == "__main__":  # pragma: no cover - exercised via `-m`
    raise SystemExit(main())
