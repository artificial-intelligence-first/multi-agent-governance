# Mcprouter Package

`mcprouter` exposes a synchronous facade over an asyncio worker pool, dispatching requests to either OpenAI or the built-in dummy provider.

## Highlights

- Router/session defaults resolved from `.mcp/.mcp-config.yaml` (single source of truth shared with Codex, Cursor, and Flow Runner)
- Supports `dummy`, `openai`, and `github` providers out of the box (GitHub REST + GraphQL with rate-limit metadata)
- Timeouts, retries, and jittered exponential backoff
- Audit log (`mcp_calls.jsonl`) including `token_usage`, with sensitive fields automatically masked
- Automatic dummy provider fallback when `router.provider` is `dummy` or when the configured OpenAI key is absent

## Example

```python
from pathlib import Path
from mcprouter import MCPRouter

with MCPRouter.from_env(log_dir=Path("telemetry/runs/sample")) as router:
    result = router.generate(
        prompt="Summarize the repository in two sentences.",
        model="gpt-4o-mini",
        prompt_limit=8192,
        prompt_buffer=512,
        sandbox="read-only",
        approval_policy="never",
    )

print(result.text)
print(result.meta["token_usage"])
```

## CLI

Use `uvx mcpctl route "hello"` to exercise the dummy provider. Pass `--log-dir` to control where JSONL audit logs are saved.

## Tests

```bash
PYTHONPATH=src/mcprouter/src uv run python -m pytest src/mcprouter/tests
```

All tests run locally; no network access is required.
