from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from ..client import get_client
from ._common import register_delete, register_reads, register_update

_HELPER = lambda c: c.tool  # noqa: E731
_NAME = "tools"
_LABEL = "tool"


def register(mcp: FastMCP, *, read_only: bool) -> None:
    register_reads(mcp, name=_NAME, label=_LABEL, helper=_HELPER)
    register_update(mcp, name=_NAME, label=_LABEL, read_only=read_only)
    register_delete(mcp, name=_NAME, label=_LABEL, read_only=read_only)
    if read_only:
        return

    @mcp.tool(name="tools_create", description="Create a tool (software used by actors).")
    async def _create(
        name: Annotated[str, Field(description="Tool name")],
        description: Annotated[str | None, Field(description="Description")] = None,
        tool_types: Annotated[
            list[str], Field(description="Tool types, e.g. ['remote-access']")
        ] = [],
        marking_ids: Annotated[
            list[str], Field(description="Marking-definition ids to attach (e.g. a TLP marking id)")
        ] = [],
        label_ids: Annotated[
            list[str], Field(description="Label ids to attach")
        ] = [],
    ) -> Any:
        return get_client().tool.create(
            name=name,
            description=description,
            tool_types=tool_types or None,
            objectMarking=marking_ids or None,
            objectLabel=label_ids or None,
        )
