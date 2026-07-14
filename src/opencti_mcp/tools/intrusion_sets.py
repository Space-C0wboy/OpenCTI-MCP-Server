from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from ..client import get_client
from ._common import register_delete, register_reads, register_update

_HELPER = lambda c: c.intrusion_set  # noqa: E731
_NAME = "intrusion_sets"
_LABEL = "intrusion set"


def register(mcp: FastMCP, *, read_only: bool) -> None:
    register_reads(mcp, name=_NAME, label=_LABEL, helper=_HELPER)
    register_update(mcp, name=_NAME, label=_LABEL, read_only=read_only)
    register_delete(mcp, name=_NAME, label=_LABEL, read_only=read_only)
    if read_only:
        return

    @mcp.tool(name="intrusion_sets_create", description="Create an intrusion set.")
    async def _create(
        name: Annotated[str, Field(description="Intrusion set name")],
        description: Annotated[str | None, Field(description="Description")] = None,
        marking_ids: Annotated[
            list[str], Field(description="Marking-definition ids to attach (e.g. a TLP marking id)")
        ] = [],
        label_ids: Annotated[
            list[str], Field(description="Label ids to attach")
        ] = [],
    ) -> Any:
        return get_client().intrusion_set.create(
            name=name,
            description=description,
            objectMarking=marking_ids or None,
            objectLabel=label_ids or None,
        )
