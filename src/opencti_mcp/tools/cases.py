from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from ..client import get_client
from ._common import register_delete, register_reads, register_update

_HELPER = lambda c: c.case_incident  # noqa: E731
_NAME = "cases"
_LABEL = "case"


def register(mcp: FastMCP, *, read_only: bool) -> None:
    register_reads(mcp, name=_NAME, label=_LABEL, helper=_HELPER)
    register_update(mcp, name=_NAME, label=_LABEL, read_only=read_only)
    register_delete(mcp, name=_NAME, label=_LABEL, read_only=read_only)
    if read_only:
        return

    @mcp.tool(name="cases_create", description="Create an incident-response case.")
    async def _create(
        name: Annotated[str, Field(description="Case name")],
        description: Annotated[str | None, Field(description="Description")] = None,
        severity: Annotated[str | None, Field(description="Severity, e.g. 'high'")] = None,
        priority: Annotated[str | None, Field(description="Priority, e.g. 'P2'")] = None,
    ) -> Any:
        return get_client().case_incident.create(
            name=name, description=description, severity=severity, priority=priority
        )
