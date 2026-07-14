from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from ..client import get_client
from ._common import register_delete, register_reads, register_update

_LABEL_HELPER = lambda c: c.label  # noqa: E731
_MARK_HELPER = lambda c: c.marking_definition  # noqa: E731


def register(mcp: FastMCP, *, read_only: bool) -> None:
    register_reads(mcp, name="labels", label="label", helper=_LABEL_HELPER)
    register_update(mcp, name="labels", label="label", read_only=read_only, editor=_LABEL_HELPER)
    register_delete(mcp, name="labels", label="label", read_only=read_only, deleter=_LABEL_HELPER)
    register_reads(mcp, name="markings", label="marking definition", helper=_MARK_HELPER)
    if read_only:
        return

    @mcp.tool(name="labels_create", description="Create a label in OpenCTI.")
    async def _create(
        value: Annotated[str, Field(description="Label text")],
        color: Annotated[str | None, Field(description="Hex color, e.g. '#ff0000'")] = None,
    ) -> Any:
        return get_client().label.create(value=value, color=color)
