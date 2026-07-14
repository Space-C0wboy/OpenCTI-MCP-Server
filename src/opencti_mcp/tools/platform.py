from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from ..client import get_client
from ._common import guard_size, register_reads, slim_result


def register(mcp: FastMCP, *, read_only: bool) -> None:
    register_reads(mcp, name="users", label="user", helper=lambda c: c.user)
    register_reads(mcp, name="groups", label="group", helper=lambda c: c.group)

    @mcp.tool(name="connectors_list", description="List connectors registered in OpenCTI.")
    async def _connectors_list() -> Any:
        return slim_result(get_client().connector.list())

    @mcp.tool(
        name="connectors_get",
        description=(
            "Get a single connector by id, including its status/state fields "
            "(active, connector_state, queue details) for ingestion health checks."
        ),
    )
    async def _connectors_get(
        connector_id: Annotated[str, Field(description="Connector id")],
    ) -> Any:
        return guard_size(get_client().connector.read(connector_id=connector_id))

    @mcp.tool(name="files_for_entity", description="List files/attachments on an entity.")
    async def _files_for_entity(
        entity_id: Annotated[str, Field(description="Entity id")],
    ) -> Any:
        return slim_result(get_client().stix_core_object.list_files(id=entity_id))

    if read_only:
        return

    @mcp.tool(
        name="entity_ask_enrichment",
        description=(
            "Trigger a connector to enrich an entity. This has side-effects: it queues "
            "a connector job against the entity."
        ),
    )
    async def _entity_ask_enrichment(
        entity_id: Annotated[str, Field(description="Entity id to enrich")],
        connector_id: Annotated[str, Field(description="Connector id to run the enrichment")],
    ) -> Any:
        get_client().stix_core_object.ask_enrichment(
            element_id=entity_id, connector_id=connector_id
        )
        return {"enrichment_requested": entity_id, "connector_id": connector_id}
