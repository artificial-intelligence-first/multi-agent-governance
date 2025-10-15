#!/usr/bin/env python3
"""Send notification messages to collaboration channels (stub)."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit a notification message.")
    parser.add_argument("--channel", required=True, help="Channel identifier")
    parser.add_argument("--message", required=True, help="Message body to send")
    args = parser.parse_args()

    print(f"[{args.channel}] {args.message}")


if __name__ == "__main__":
    main()
