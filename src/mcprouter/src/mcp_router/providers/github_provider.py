"""GitHub provider implementation."""

from __future__ import annotations

import httpx

from ..schemas import ProviderRequest, ProviderResponse
from .base import BaseProvider, ProviderError

_DEFAULT_TIMEOUT = 15.0
_DEFAULT_ACCEPT = "application/vnd.github+json"
_DEFAULT_API_VERSION = "2022-11-28"
_DEFAULT_USER_AGENT = "multi-agent-governance-mcp-router/1.0"


class GitHubProvider(BaseProvider):
    """Minimal provider that proxies requests to the GitHub REST API."""

    name = "github"
    default_timeout = _DEFAULT_TIMEOUT
    default_api_version = _DEFAULT_API_VERSION

    def __init__(
        self,
        token: str,
        *,
        base_url: str = "https://api.github.com",
        default_timeout: float = _DEFAULT_TIMEOUT,
        api_version: str = _DEFAULT_API_VERSION,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if not token:
            raise ValueError("token must be provided for GitHubProvider")
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._api_version = api_version
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": _DEFAULT_ACCEPT,
            "X-GitHub-Api-Version": api_version,
            "User-Agent": _DEFAULT_USER_AGENT,
        }
        if client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=default_timeout,
                headers=headers,
            )
            self._owns_client = True
        else:
            # Ensure token and accept headers are present.
            client.headers.setdefault("Authorization", f"Bearer {token}")
            client.headers.setdefault("Accept", _DEFAULT_ACCEPT)
            client.headers.setdefault("X-GitHub-Api-Version", api_version)
            client.headers.setdefault("User-Agent", _DEFAULT_USER_AGENT)
            self._client = client
            self._owns_client = False

    async def agenerate(self, payload: ProviderRequest) -> ProviderResponse:
        config = dict(payload.config or {})
        method_raw = config.get("method") or "GET"
        method = str(method_raw).upper().strip()
        path = self._resolve_path(config, payload.prompt)
        params = config.get("params")
        json_payload = config.get("json")
        data_payload = config.get("data")
        text_payload = config.get("text_body")
        raw_body = config.get("body")
        graphql_enabled = bool(config.get("graphql"))
        headers = dict(config.get("headers") or {})

        if graphql_enabled:
            method = "POST"
            graphql_query = config.get("query") or payload.prompt
            variables = config.get("variables")
            json_payload = {
                "query": graphql_query,
                "variables": variables or {},
            }
            path = config.get("path") or "/graphql"
            headers.setdefault("Content-Type", "application/json")

        try:
            response = await self._client.request(
                method,
                path,
                params=params,
                json=json_payload if json_payload is not None else None,
                data=data_payload,
                content=self._prepare_body(text_payload, raw_body),
                headers=headers or None,
                timeout=payload.timeout_sec,
            )
            response.raise_for_status()
            await response.aread()
        except httpx.HTTPStatusError as exc:
            retriable = 500 <= exc.response.status_code < 600
            raise ProviderError(
                f"github request failed: {exc.response.status_code} {exc.response.reason_phrase}",
                retriable=retriable,
            ) from exc
        except httpx.HTTPError as exc:  # pragma: no cover - network failures mocked in tests
            raise ProviderError(str(exc), retriable=True) from exc

        try:
            json_content = response.json()
            content = [{"data": json_content}]
        except ValueError:
            json_content = None
            content = []

        text = response.text

        latency_ms = None
        try:
            elapsed = response.elapsed
        except RuntimeError:  # Mock transports might skip elapsed tracking
            elapsed = None
        if elapsed is not None:
            latency_ms = elapsed.total_seconds() * 1000

        meta = {
            "status_code": response.status_code,
            "url": str(response.request.url),
            "method": method,
        }
        if headers:
            meta["request_headers"] = headers

        rate_remaining = response.headers.get("X-RateLimit-Remaining")
        rate_reset = response.headers.get("X-RateLimit-Reset")
        if rate_remaining is not None:
            try:
                meta["rate_limit_remaining"] = int(rate_remaining)
            except ValueError:
                meta["rate_limit_remaining"] = rate_remaining
        if rate_reset is not None:
            meta["rate_limit_reset"] = rate_reset

        token_usage = {"tokens": {"input": 0, "output": 0, "total": 0}}
        return ProviderResponse(
            text=text,
            content=content,
            meta=meta,
            latency_ms=latency_ms,
            token_usage=token_usage,
        )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    def _resolve_path(self, config: dict, prompt: str) -> str:
        """Resolve the API path or URL from config/prompt."""

        path = config.get("path") or config.get("api_path") or prompt
        if not isinstance(path, str) or not path.strip():
            raise ProviderError("github provider requires a path or prompt describing the API call")
        path = path.strip()
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = f"/{path}"
        return path

    @staticmethod
    def _prepare_body(text_payload: str | None, raw_body: bytes | str | None) -> bytes | None:
        if raw_body is None and text_payload is None:
            return None
        if raw_body is not None:
            if isinstance(raw_body, bytes):
                return raw_body
            return str(raw_body).encode("utf-8")
        return text_payload.encode("utf-8")
