#!/usr/bin/env python3
"""Validate BrowserSAG prerequisites.

Checks that BrowserSAG documentation for browser MCP servers is present and that the
shared MCP configuration exposes the `servers.chrome-devtools`, `servers.playwright`,
and `servers.markitdown` entries.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate BrowserSAG docs and MCP configuration."
    )
    parser.add_argument(
        "--docs",
        type=Path,
        nargs="*",
        default=[
            Path("docs/reference/tool/mcp/chrome-devtools/overview.md"),
            Path("docs/reference/tool/mcp/playwright/overview.md"),
            Path("docs/reference/tool/mcp/markitdown/overview.md"),
        ],
        help="Paths to required MCP reference documents.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(".mcp/.mcp-config.yaml"),
        help="Path to the MCP router configuration.",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> dict:
    try:
        return yaml.safe_load(path.read_text())
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Missing YAML file: {path}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"Failed to parse YAML file {path}: {exc}") from exc


def main() -> int:
    args = parse_args()

    missing_docs = [doc for doc in args.docs if not doc.is_file()]
    if missing_docs:
        for doc in missing_docs:
            print(f"[browser-sag] Documentation missing: {doc}", file=sys.stderr)
        return 1

    config = load_yaml(args.config)
    servers = config.get("servers", {})
    required_servers = {
        "chrome-devtools",
        "playwright",
        "markitdown",
    }
    missing_servers = [name for name in required_servers if name not in servers]
    if missing_servers:
        print(
            "[browser-sag] Missing server configuration(s) in "
            f"{args.config}: {', '.join(sorted(missing_servers))}",
            file=sys.stderr,
        )
        return 2

    print(
        "[browser-sag] Browser MCP documentation and configuration validated "
        "successfully."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
