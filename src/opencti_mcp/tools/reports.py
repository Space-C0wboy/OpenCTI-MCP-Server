from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from ..client import get_client
from ._common import register_delete, register_reads, register_update

_HELPER = lambda c: c.report  # noqa: E731
_NAME = "reports"
_LABEL = "report"


def register(mcp: FastMCP, *, read_only: bool) -> None:
    register_reads(mcp, name=_NAME, label=_LABEL, helper=_HELPER)
    register_update(mcp, name=_NAME, label=_LABEL, read_only=read_only)
    register_delete(mcp, name=_NAME, label=_LABEL, read_only=read_only)
    if read_only:
        return

    @mcp.tool(name="reports_create", description="Create a report in OpenCTI.")
    async def _create(
        name: Annotated[str, Field(description="Report name")],
        published: Annotated[str, Field(description="ISO-8601 published date")],
        description: Annotated[str | None, Field(description="Description")] = None,
        report_types: Annotated[
            list[str], Field(description="Report types, e.g. ['threat-report']")
        ] = [],
        object_ids: Annotated[
            list[str], Field(description="Ids of entities to attach to the report")
        ] = [],
        marking_ids: Annotated[
            list[str], Field(description="Marking-definition ids to attach (e.g. a TLP marking id)")
        ] = [],
        label_ids: Annotated[
            list[str], Field(description="Label ids to attach")
        ] = [],
    ) -> Any:
        return get_client().report.create(
            name=name,
            published=published,
            description=description,
            report_types=report_types or None,
            objects=object_ids or None,
            objectMarking=marking_ids or None,
            objectLabel=label_ids or None,
        )
