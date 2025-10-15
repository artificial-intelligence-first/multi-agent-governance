#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH="${PYTHONPATH:-src}"
export PYTHONPATH

uv run -m automation.compliance.pre "$@"
