#!/usr/bin/env python3
"""Utility to update AGENT_REGISTRY routes."""

import argparse
import yaml
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Update agent registry primary handler.")
    parser.add_argument("--route", required=True, help="Route key, e.g., documentation")
    parser.add_argument("--primary", required=True, help="Primary handler value")
    parser.add_argument("--registry", default="agents/AGENT_REGISTRY.yaml", help="Path to registry file")
    args = parser.parse_args()

    registry_path = Path(args.registry)
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))

    routes = data.setdefault("routes", {})
    if args.route not in routes:
        raise SystemExit(f"Route {args.route} not found in registry")

    routes[args.route]["primary"] = args.primary
    registry_path.write_text(yaml.dump(data, sort_keys=False), encoding="utf-8")
    print(f"Updated {args.route} primary to {args.primary}")


if __name__ == "__main__":
    main()
