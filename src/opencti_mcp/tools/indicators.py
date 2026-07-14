from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from ..client import get_client
from ._common import register_delete, register_reads, register_update

_HELPER = lambda c: c.indicator  # noqa: E731
_NAME = "indicators"
_LABEL = "indicator"


def register(mcp: FastMCP, *, read_only: bool) -> None:
    register_reads(mcp, name=_NAME, label=_LABEL, helper=_HELPER)
    register_update(mcp, name=_NAME, label=_LABEL, read_only=read_only)
    register_delete(mcp, name=_NAME, label=_LABEL, read_only=read_only)
    if read_only:
        return

    @mcp.tool(name="indicators_create", description="Create an indicator in OpenCTI.")
    async def _create(
        name: Annotated[str, Field(description="Indicator name")],
        pattern: Annotated[str, Field(description="Detection pattern, e.g. a STIX pattern")],
        pattern_type: Annotated[str, Field(description="Pattern type, e.g. 'stix'")],
        x_opencti_main_observable_type: Annotated[
            str, Field(description="Main observable type, e.g. 'IPv4-Addr'")
        ],
        description: Annotated[str | None, Field(description="Description")] = None,
        valid_from: Annotated[str | None, Field(description="ISO-8601 valid-from date")] = None,
        confidence: Annotated[int | None, Field(description="Confidence 0-100")] = None,
        marking_ids: Annotated[
            list[str], Field(description="Marking-definition ids to attach (e.g. a TLP marking id)")
        ] = [],
        label_ids: Annotated[
            list[str], Field(description="Label ids to attach")
        ] = [],
    ) -> Any:
        return get_client().indicator.create(
            name=name,
            pattern=pattern,
            pattern_type=pattern_type,
            x_opencti_main_observable_type=x_opencti_main_observable_type,
            description=description,
            valid_from=valid_from,
            confidence=confidence,
            objectMarking=marking_ids or None,
            objectLabel=label_ids or None,
        )
