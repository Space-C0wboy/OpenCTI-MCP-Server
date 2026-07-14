from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from ..client import get_client
from ._common import register_delete, register_reads, register_update

_HELPER = lambda c: c.campaign  # noqa: E731
_NAME = "campaigns"
_LABEL = "campaign"


def register(mcp: FastMCP, *, read_only: bool) -> None:
    register_reads(mcp, name=_NAME, label=_LABEL, helper=_HELPER)
    register_update(mcp, name=_NAME, label=_LABEL, read_only=read_only)
    register_delete(mcp, name=_NAME, label=_LABEL, read_only=read_only)
    if read_only:
        return

    @mcp.tool(name="campaigns_create", description="Create a campaign.")
    async def _create(
        name: Annotated[str, Field(description="Campaign name")],
        description: Annotated[str | None, Field(description="Description")] = None,
    ) -> Any:
        return get_client().campaign.create(name=name, description=description)
