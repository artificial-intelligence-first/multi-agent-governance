#!/usr/bin/env python3
"""Ensure observability dashboards exist for a given agent."""

import argparse


DASHBOARD_REGISTRY = {
    "workflow-mag": "https://grafana.example.com/d/workflow-mag",
    "knowledge-mag": "https://grafana.example.com/d/knowledge-mag",
    "operations-mag": "https://grafana.example.com/d/operations-mag",
    "qa-mag": "https://grafana.example.com/d/qa-mag",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Check dashboard availability.")
    parser.add_argument("agent", help="Agent identifier, e.g., workflow-mag")
    args = parser.parse_args()

    if args.agent not in DASHBOARD_REGISTRY:
        raise SystemExit(f"No dashboard registered for {args.agent}")

    print(f"Dashboard located: {DASHBOARD_REGISTRY[args.agent]}")


if __name__ == "__main__":
    main()
