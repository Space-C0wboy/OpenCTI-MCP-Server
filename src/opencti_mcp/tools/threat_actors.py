from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from ..client import get_client
from ._common import register_delete, register_reads, register_update

_HELPER = lambda c: c.threat_actor_group  # noqa: E731
_NAME = "threat_actors"
_LABEL = "threat actor"


def register(mcp: FastMCP, *, read_only: bool) -> None:
    register_reads(mcp, name=_NAME, label=_LABEL, helper=_HELPER)
    register_update(mcp, name=_NAME, label=_LABEL, read_only=read_only)
    register_delete(mcp, name=_NAME, label=_LABEL, read_only=read_only)
    if read_only:
        return

    @mcp.tool(name="threat_actors_create", description="Create a threat actor group.")
    async def _create(
        name: Annotated[str, Field(description="Threat actor name")],
        description: Annotated[str | None, Field(description="Description")] = None,
        threat_actor_types: Annotated[
            list[str], Field(description="Types, e.g. ['crime-syndicate']")
        ] = [],
    ) -> Any:
        return get_client().threat_actor_group.create(
            name=name, description=description, threat_actor_types=threat_actor_types or None
        )
