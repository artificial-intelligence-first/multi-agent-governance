import asyncio
import json

import httpx
import pytest

from mcp_router.providers.base import ProviderError
from mcp_router.providers.github_provider import GitHubProvider
from mcp_router.schemas import ProviderRequest


@pytest.mark.asyncio
async def test_github_provider_success_request() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("Authorization") == "Bearer ghp_test"
        assert request.headers.get("X-GitHub-Api-Version") == "2022-11-28"
        assert request.headers.get("User-Agent")
        assert request.url.path == "/rate_limit"
        return httpx.Response(200, json={"resources": {"core": {"remaining": 4999}}})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="https://api.github.com") as client:
        provider = GitHubProvider("ghp_test", client=client)
        payload = ProviderRequest(
            prompt="/rate_limit",
            model="github",
            sandbox="read-only",
            approval_policy="never",
            config={},
            timeout_sec=5.0,
        )
        response = await provider.agenerate(payload)
        assert response.meta["status_code"] == 200
        assert response.content[0]["data"]["resources"]["core"]["remaining"] == 4999
        await provider.aclose()


@pytest.mark.asyncio
async def test_github_provider_requires_path() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="https://api.github.com") as client:
        provider = GitHubProvider("ghp_test", client=client)
        payload = ProviderRequest(
            prompt=" ",
            model="github",
            sandbox="read-only",
            approval_policy="never",
            config={},
            timeout_sec=5.0,
        )
        with pytest.raises(ProviderError):
            await provider.agenerate(payload)
        await provider.aclose()


@pytest.mark.asyncio
async def test_github_provider_graphql_support() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/graphql"
        body = json.loads(request.content.decode())
        assert body["query"].startswith("query Repo")
        assert body["variables"] == {"name": "multi-agent-governance"}
        return httpx.Response(200, json={"data": {"viewer": {"login": "octocat"}}})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="https://api.github.com") as client:
        provider = GitHubProvider("ghp_test", client=client)
        payload = ProviderRequest(
            prompt="query Repo($name: String!) { repository(name: $name, owner: \"openai\") { id } }",
            model="github",
            sandbox="read-only",
            approval_policy="never",
            config={
                "graphql": True,
                "variables": {"name": "multi-agent-governance"},
            },
            timeout_sec=5.0,
        )
        response = await provider.agenerate(payload)
        assert response.meta["status_code"] == 200
        assert response.content[0]["data"]["data"]["viewer"]["login"] == "octocat"
        await provider.aclose()
