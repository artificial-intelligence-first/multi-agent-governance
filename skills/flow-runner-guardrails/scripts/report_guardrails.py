#!/usr/bin/env python3
"""Emit a lightweight summary of Flow Runner skills guardrail status."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarise guardrail configuration for the skills execution pilot."
    )
    parser.add_argument(
        "--allowlist",
        default="skills/ALLOWLIST.txt",
        help="Path to the skills execution allowlist file.",
    )
    parser.add_argument(
        "--output",
        help="Optional path to write a JSON status report.",
    )
    return parser.parse_args()


def load_allowlist(path: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    if not path.exists():
        return entries
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=2)
        if len(parts) != 3:
            continue
        entries.append(
            {
                "path": parts[0],
                "sha256": parts[1],
                "args_pattern": parts[2],
            }
        )
    return entries


def main() -> int:
    args = parse_args()
    allowlist_path = Path(args.allowlist)
    entries = load_allowlist(allowlist_path)
    summary = {
        "allowlist_path": str(allowlist_path),
        "entries": entries,
        "entry_count": len(entries),
    }
    payload = json.dumps(summary, indent=2)
    print(payload)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
