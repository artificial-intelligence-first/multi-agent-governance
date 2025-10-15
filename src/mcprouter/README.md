# Mcprouter Package

`mcprouter` exposes a synchronous facade over an asyncio worker pool, dispatching requests to either OpenAI or the built-in dummy provider.

## Highlights

- Worker pool sized via `MCP_MAX_SESSIONS`
- Timeouts, retries, and jittered exponential backoff
- Audit log (`mcp_calls.jsonl`) including `token_usage`, with sensitive fields automatically masked
- Automatic dummy provider fallback when `OPENAI_API_KEY` is unset

## Example

```python
from pathlib import Path
from mcprouter import MCPRouter

with MCPRouter.from_env(log_dir=Path(".runs/sample")) as router:
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

Use `mcpctl route "hello"` to exercise the dummy provider. Pass `--log-dir` to control where JSONL audit logs are saved.

## Tests

```bash
python -m pytest packages/mcprouter
```

All tests run locally; no network access is required.
