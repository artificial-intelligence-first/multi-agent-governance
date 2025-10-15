"""Flow Runner core package."""

from __future__ import annotations

import os
from importlib.metadata import PackageNotFoundError, version
from pkgutil import extend_path

try:
    __version__ = version("flowrunner")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = ["__version__"]

# Allow downstream repositories to register additional module search paths
# for the flow_runner namespace (used for custom tasks/stages).
for extra in os.environ.get("FLOW_RUNNER_EXT_PATH", "").split(os.pathsep):
    if extra:
        __path__ = extend_path(__path__, __name__)
        if extra not in __path__:
            __path__.append(extra)
