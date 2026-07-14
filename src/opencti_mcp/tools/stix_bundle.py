from __future__ import annotations

import json
from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from ..client import get_client
from ._common import _SIZE_LIMIT


def register(mcp: FastMCP, *, read_only: bool) -> None:
    @mcp.tool(
        name="stix_export_entity",
        description="Export a single entity as a STIX 2 bundle/object.",
    )
    async def _stix_export_entity(
        entity_type: Annotated[str, Field(description="Entity type, e.g. 'Malware', 'Indicator', 'Report'")],
        entity_id: Annotated[str, Field(description="Entity id")],
        mode: Annotated[
            str, Field(description="'simple' or 'full' (full includes related files)")
        ] = "simple",
    ) -> Any:
        return get_client().stix2.get_stix_bundle_or_object_from_entity_id(
            entity_type=entity_type, entity_id=entity_id, mode=mode
        )

    @mcp.tool(
        name="stix_export_list",
        description=(
            "Export up to `first` entities of a given type as a STIX 2 bundle. "
            "If the resulting bundle would exceed the response size limit, returns a "
            "small note (with object_count) instead of the oversized bundle."
        ),
    )
    async def _stix_export_list(
        entity_type: Annotated[str, Field(description="Entity type, e.g. 'Malware', 'Indicator', 'Report'")],
        first: Annotated[
            int, Field(description="Max entities to include in the bundle (1-500)", ge=1, le=500)
        ] = 25,
        mode: Annotated[
            str, Field(description="'simple' or 'full' (full includes related files)")
        ] = "simple",
    ) -> Any:
        client = get_client()
        entities = client.stix_core_object.list(
            types=[entity_type],
            first=first,
            withPagination=True,
            withFiles=(mode == "full"),
        )["entities"]
        bundle = client.stix2.export_selected(entities_list=entities, mode=mode)
        if len(json.dumps(bundle, default=str)) > _SIZE_LIMIT:
            return {
                "_note": (
                    f"Export of '{entity_type}' exceeds the response size limit even at first={first}. "
                    "Lower `first`, narrow the entity_type, or use stix_export_entity for a single entity."
                ),
                "entity_type": entity_type,
                "first": first,
                "object_count": len(bundle.get("objects", [])),
            }
        return bundle

    if read_only:
        return

    @mcp.tool(
        name="stix_import_bundle",
        description=(
            "Import a STIX 2 bundle into OpenCTI. This CREATES/updates data in OpenCTI: "
            "a bulk write that can add or modify many entities and relationships."
        ),
    )
    async def _stix_import_bundle(
        bundle_json: Annotated[str, Field(description="A STIX bundle as a JSON string")],
        update: Annotated[
            bool, Field(description="Update existing entities if they already exist")
        ] = False,
    ) -> Any:
        imported, failed = get_client().stix2.import_bundle_from_json(
            json_data=bundle_json, update=update
        )
        return {"imported_count": len(imported), "failed_count": len(failed)}
