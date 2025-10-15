#!/usr/bin/env python3
"""Lightweight code style sanity check for agent-generated code artifacts."""

import argparse
import json
from pathlib import Path

ALLOWED_LANGS = {"python", "typescript", "bash", "javascript", "go", "ruby"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate code block metadata.")
    parser.add_argument("response", type=Path, help="Path to the artifact JSON to inspect")
    args = parser.parse_args()

    payload = json.loads(args.response.read_text(encoding="utf-8"))

    output_mode = payload.get("output_mode")
    if output_mode != "code":
        print("Skipped: output_mode is not code.")
        return

    blocks = payload.get("code_blocks", [])
    if not blocks:
        raise SystemExit("output_mode is code but no code_blocks provided")

    for index, block in enumerate(blocks):
        language = block.get("language", "")
        if language.lower() not in ALLOWED_LANGS:
            raise SystemExit(f"code block {index} uses unsupported language '{language}'")
        content = block.get("content", "")
        if not content.strip():
            raise SystemExit(f"code block {index} has empty content")

    print("Code style check passed.")


if __name__ == "__main__":
    main()
