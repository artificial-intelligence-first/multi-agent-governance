"""ContextSAG package exports."""

from __future__ import annotations

from .agent import ContextSAG

__all__ = ["ContextSAG", "assemble"]


async def assemble(
    *,
    request=None,
    request_path=None,
    output_path=None,
    context=None,
) -> dict:
    """Convenience entrypoint used by Flow Runner route configuration."""

    agent = ContextSAG()
    return await agent.run(
        request=request,
        request_path=request_path,
        output_path=output_path,
        context=context,
    )
