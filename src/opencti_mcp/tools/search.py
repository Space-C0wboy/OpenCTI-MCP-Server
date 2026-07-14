from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from ..client import get_client
from ._common import slim_result


def register(mcp: FastMCP, *, read_only: bool) -> None:
    @mcp.tool(
        name="search_all",
        description=(
            "Search across all STIX object types in OpenCTI at once. Use when the entity "
            "type is unknown; optionally restrict with `types`."
        ),
    )
    async def _search_all(
        query: Annotated[str, Field(description="Full-text search string")],
        types: Annotated[
            list[str],
            Field(description="Optional STIX types to restrict to, e.g. ['Malware', 'Indicator']"),
        ] = [],
        first: Annotated[int, Field(description="Max results (1-500)", ge=1, le=500)] = 25,
    ) -> Any:
        return slim_result(
            get_client().stix_core_object.list(
                search=query, types=types or None, first=first, withPagination=True
            )
        )
