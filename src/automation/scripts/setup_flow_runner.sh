#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN=${PYTHON_BIN:-python3}
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
FLOW_RUNNER_SPEC=${FLOW_RUNNER_SPEC:-"${REPO_ROOT}/src/flowrunner"}
MCP_ROUTER_SPEC=${MCP_ROUTER_SPEC:-"${REPO_ROOT}/src/mcprouter"}

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "[setup-flow-runner] ${PYTHON_BIN} not found. Install Python 3.14.x (or at least 3.12+) and rerun." >&2
  exit 1
fi

PIP_CMD=("${PYTHON_BIN}" -m pip --disable-pip-version-check)

echo "[setup-flow-runner] Installing mcprouter via user-site (${MCP_ROUTER_SPEC})" >&2
"${PIP_CMD[@]}" install --user --break-system-packages --upgrade "${MCP_ROUTER_SPEC}"

echo "[setup-flow-runner] Installing flowrunner via user-site (${FLOW_RUNNER_SPEC})" >&2
"${PIP_CMD[@]}" install --user --break-system-packages --upgrade "${FLOW_RUNNER_SPEC}"

cat <<'MSG'
[setup-flow-runner] Done.
- Ensure '
  python3 -m site --user-base
' bin directory is on your PATH (e.g., export PATH="$HOME/Library/Python/3.14/bin:$PATH").
- Example: flowctl run runtime/automation/flow_runner/flows/workflow_mag.flow.yaml --dry-run
MSG
