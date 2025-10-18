"""Minimal CLI for interacting with MCP Router."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

from .router import MCPRouter


def _run_route(args: argparse.Namespace) -> int:
    """Execute a single prompt through MCPRouter."""

    log_dir = Path(args.log_dir).expanduser().resolve()
    log_dir.mkdir(parents=True, exist_ok=True)
    with MCPRouter.from_env(log_dir=log_dir) as router:
        result = router.generate(
            prompt=args.prompt,
            model=args.model,
            prompt_limit=args.prompt_limit,
            prompt_buffer=args.prompt_buffer,
            sandbox="read-only",
            approval_policy="never",
            config={},
        )
    output = {
        "text": result.text,
        "meta": result.meta,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the top-level argument parser."""

    parser = argparse.ArgumentParser(prog="mcpctl", description="MCP Router debug CLI")
    sub = parser.add_subparsers(dest="command")
    route_parser = sub.add_parser("route", help="Send a prompt through MCP Router")
    route_parser.add_argument("prompt", help="Prompt content to send to the provider")
    route_parser.add_argument("--model", default="debug-model", help="Model identifier")
    route_parser.add_argument("--prompt-limit", type=int, default=8096, help="Prompt token budget")
    route_parser.add_argument(
        "--prompt-buffer",
        type=int,
        default=512,
        help="Token reserve to avoid hitting the limit",
    )
    route_parser.add_argument(
        "--log-dir",
        default="telemetry/runs/mcpctl",
        help="Directory where MCP logs will be written",
    )
    route_parser.set_defaults(handler=_run_route)
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entry point."""

    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 1
    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
