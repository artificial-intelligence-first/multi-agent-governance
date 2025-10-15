"""Shell step implementation."""

from __future__ import annotations

import asyncio
import os
from typing import Any, Dict

from .base import BaseStep, ExecutionContext, StepExecutionError


class ShellStep(BaseStep):
    """Executes a shell command within the workspace."""

    async def run(self, context: ExecutionContext) -> Dict[str, Any]:
        env = os.environ.copy()
        env.update(
            {
                "FLOW_RUN_ID": context.run_id,
                "FLOW_OUTPUT_DIR": str(context.run_dir),
                "FLOW_ARTIFACTS_DIR": str(context.artifacts_dir),
            }
        )
        process = await asyncio.create_subprocess_shell(
            self.spec.run,
            cwd=context.workspace_dir,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await process.communicate()
        except asyncio.CancelledError:  # pragma: no cover - cooperative cancellation
            process.kill()
            raise
        stdout_text = stdout.decode("utf-8", errors="replace")
        stderr_text = stderr.decode("utf-8", errors="replace")
        if process.returncode != 0:
            detail = (stderr_text or stdout_text).strip()
            if detail and len(detail) > 500:
                detail = f"{detail[:497]}..."
            message = f"shell step '{self.id}' failed with exit code {process.returncode}"
            if detail:
                message += f": {detail}"
            raise StepExecutionError(message)
        return {
            "stdout": stdout_text.strip(),
            "stderr": stderr_text.strip(),
            "command": self.spec.run,
        }
