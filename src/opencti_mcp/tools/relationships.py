from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from ..client import get_client
from ._common import register_delete, register_reads, register_update, slim_result

_HELPER = lambda c: c.stix_core_relationship  # noqa: E731
_NAME = "relationships"
_LABEL = "relationship"


def register(mcp: FastMCP, *, read_only: bool) -> None:
    register_reads(mcp, name=_NAME, label=_LABEL, helper=_HELPER)
    register_update(mcp, name=_NAME, label=_LABEL, read_only=read_only, editor=_HELPER)
    register_delete(mcp, name=_NAME, label=_LABEL, read_only=read_only, deleter=_HELPER)

    @mcp.tool(
        name="relationships_for_entity",
        description="List relationships touching a given entity (as either source or target) — answers 'what is related to X'.",
    )
    async def _for_entity(
        entity_id: Annotated[
            str, Field(description="Entity id whose relationships to fetch (matches source OR target)")
        ],
        relationship_type: Annotated[
            str | None,
            Field(description="Optional relationship type filter, e.g. 'uses', 'indicates', 'targets'"),
        ] = None,
        first: Annotated[int, Field(description="Max results (1-500)", ge=1, le=500)] = 25,
    ) -> Any:
        return slim_result(
            get_client().stix_core_relationship.list(
                fromOrToId=entity_id,
                relationship_type=relationship_type,
                first=first,
                withPagination=True,
            )
        )

    if read_only:
        return

    @mcp.tool(
        name="relationships_create",
        description="Create a STIX core relationship between two entities.",
    )
    async def _create(
        from_id: Annotated[str, Field(description="Source entity id")],
        to_id: Annotated[str, Field(description="Target entity id")],
        relationship_type: Annotated[
            str, Field(description="Relationship type, e.g. 'indicates', 'uses', 'targets'")
        ],
        description: Annotated[str | None, Field(description="Description")] = None,
        confidence: Annotated[int | None, Field(description="Confidence 0-100")] = None,
    ) -> Any:
        return get_client().stix_core_relationship.create(
            fromId=from_id,
            toId=to_id,
            relationship_type=relationship_type,
            description=description,
            confidence=confidence,
        )
