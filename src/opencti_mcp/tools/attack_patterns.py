from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from ..client import get_client
from ._common import register_delete, register_reads, register_update

_HELPER = lambda c: c.attack_pattern  # noqa: E731
_NAME = "attack_patterns"
_LABEL = "attack pattern"


def register(mcp: FastMCP, *, read_only: bool) -> None:
    register_reads(mcp, name=_NAME, label=_LABEL, helper=_HELPER)
    register_update(mcp, name=_NAME, label=_LABEL, read_only=read_only)
    register_delete(mcp, name=_NAME, label=_LABEL, read_only=read_only)
    if read_only:
        return

    @mcp.tool(name="attack_patterns_create", description="Create an attack pattern (TTP).")
    async def _create(
        name: Annotated[str, Field(description="Attack pattern name")],
        description: Annotated[str | None, Field(description="Description")] = None,
        x_mitre_id: Annotated[str | None, Field(description="MITRE ATT&CK id, e.g. 'T1059'")] = None,
    ) -> Any:
        return get_client().attack_pattern.create(
            name=name, description=description, x_mitre_id=x_mitre_id
        )
