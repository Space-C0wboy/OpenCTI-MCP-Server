from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from ..client import get_client
from ._common import register_delete, register_reads

_HELPER = lambda c: c.identity  # noqa: E731
_NAME = "identities"
_LABEL = "identity"

_IDENTITY_TYPES = {
    "organization": "Organization",
    "individual": "Individual",
    "system": "System",
    "sector": "Sector",
}


def register(mcp: FastMCP, *, read_only: bool) -> None:
    register_reads(mcp, name=_NAME, label=_LABEL, helper=_HELPER)
    register_delete(mcp, name=_NAME, label=_LABEL, read_only=read_only)
    if read_only:
        return

    @mcp.tool(name="identities_create", description="Create an identity (organization, individual, system, or sector).")
    async def _create(
        name: Annotated[str, Field(description="Identity name")],
        identity_class: Annotated[
            str, Field(description="Identity type: organization | individual | system | sector")
        ] = "organization",
        description: Annotated[str | None, Field(description="Description")] = None,
        contact_information: Annotated[str | None, Field(description="Contact information")] = None,
        marking_ids: Annotated[
            list[str], Field(description="Marking-definition ids to attach (e.g. a TLP marking id)")
        ] = [],
        label_ids: Annotated[
            list[str], Field(description="Label ids to attach")
        ] = [],
    ) -> Any:
        mapped_type = _IDENTITY_TYPES.get(identity_class.lower(), "Organization")
        return get_client().identity.create(
            type=mapped_type,
            name=name,
            description=description,
            contact_information=contact_information,
            objectMarking=marking_ids or None,
            objectLabel=label_ids or None,
        )
