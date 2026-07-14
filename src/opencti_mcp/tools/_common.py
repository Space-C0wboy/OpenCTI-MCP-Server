from __future__ import annotations

import json
from typing import Annotated, Any, Callable

from fastmcp import FastMCP
from pydantic import Field

from ..client import get_client

HelperGetter = Callable[[Any], Any]

_DROP_KEYS = {"objects", "config", "connector_user", "parent_types", "spec_version", "content"}
_SIZE_LIMIT = 100_000


def _slim_entity(entity):
    """Reduce a pycti entity dict to a compact, LLM-friendly summary."""
    if not isinstance(entity, dict):
        return entity
    slim = {}
    for key, value in entity.items():
        if key in _DROP_KEYS or key.endswith("Ids"):
            continue
        if key == "createdBy" and isinstance(value, dict):
            slim[key] = {"id": value.get("id"), "name": value.get("name")}
        elif key == "objectMarking" and isinstance(value, list):
            slim[key] = [m.get("definition") for m in value if isinstance(m, dict)]
        elif key == "objectLabel" and isinstance(value, list):
            slim[key] = [m.get("value") for m in value if isinstance(m, dict)]
        elif key in ("from", "to") and isinstance(value, dict):
            slim[key] = {
                "id": value.get("id"),
                "entity_type": value.get("entity_type"),
                "name": value.get("name"),
                "standard_id": value.get("standard_id"),
            }
        elif key == "externalReferences" and isinstance(value, list):
            slim[key] = [
                {"source_name": r.get("source_name"), "url": r.get("url"), "external_id": r.get("external_id")}
                for r in value
                if isinstance(r, dict)
            ]
        else:
            slim[key] = value
    return slim


def slim_result(result):
    """Slim a list-shaped tool result (either a {entities: [...], pagination} dict or a bare list)."""
    if isinstance(result, dict) and isinstance(result.get("entities"), list):
        slimmed = {**result, "entities": [_slim_entity(e) for e in result["entities"]]}
        entities = slimmed["entities"]
        while len(entities) > 1 and len(json.dumps(slimmed, default=str)) > _SIZE_LIMIT:
            keep = max(1, len(entities) // 2)
            dropped = len(entities) - keep
            entities = entities[:keep]
            slimmed = {
                **slimmed,
                "entities": entities,
                "_note": f"Result truncated to {keep} entities ({dropped} more omitted) to fit size limits; "
                         f"narrow your query or use pagination/first for the rest.",
            }
        return slimmed
    if isinstance(result, list):
        return [_slim_entity(e) for e in result]
    return result


def guard_size(entity, limit=_SIZE_LIMIT):
    """Return a single entity as-is unless it serializes larger than `limit`, in which case slim it."""
    try:
        raw = json.dumps(entity, default=str)
    except (TypeError, ValueError):
        return entity
    if len(raw) <= limit:
        return entity
    slim = _slim_entity(entity) if isinstance(entity, dict) else entity
    if isinstance(slim, dict):
        slim = {
            **slim,
            "_note": "Entity too large to return in full; showing a slimmed view. "
                     "Use stix_export_entity or graphql_query for complete detail.",
        }
    return slim


def register_reads(mcp: FastMCP, *, name: str, label: str, helper: HelperGetter) -> None:
    @mcp.tool(name=f"{name}_list", description=f"List or search {label} entities in OpenCTI.")
    async def _list(
        search: Annotated[str | None, Field(description="Full-text search string")] = None,
        first: Annotated[int, Field(description="Max results (1-500)", ge=1, le=500)] = 25,
        after: Annotated[str | None, Field(description="Pagination cursor")] = None,
        order_by: Annotated[
            str | None,
            Field(
                description=(
                    "Field to sort by, e.g. 'created_at' or 'modified'. "
                    "Use 'created_at' for most-recent-first."
                )
            ),
        ] = None,
        descending: Annotated[
            bool,
            Field(description="Sort descending (newest/highest first). Ignored unless order_by is set."),
        ] = True,
    ) -> Any:
        order_mode = ("desc" if descending else "asc") if order_by else None
        return slim_result(
            helper(get_client()).list(
                search=search,
                first=first,
                after=after,
                orderBy=order_by,
                orderMode=order_mode,
                withPagination=True,
            )
        )

    @mcp.tool(name=f"{name}_get", description=f"Get a single {label} by id.")
    async def _get(
        id: Annotated[str, Field(description="Entity id (STIX id or internal UUID)")],
    ) -> Any:
        return guard_size(helper(get_client()).read(id=id))


_DEFAULT_EDITOR = lambda c: c.stix_domain_object  # noqa: E731


def register_update(
    mcp: FastMCP, *, name: str, label: str, read_only: bool, editor: HelperGetter = _DEFAULT_EDITOR
) -> None:
    if read_only:
        return

    @mcp.tool(name=f"{name}_update", description=f"Update one field on a {label}.")
    async def _update(
        id: Annotated[str, Field(description="Entity id to update")],
        key: Annotated[str, Field(description="Field name, e.g. 'description' or 'confidence'")],
        value: Annotated[str, Field(description="New value for the field")],
    ) -> Any:
        return editor(get_client()).update_field(id=id, input=[{"key": key, "value": value}])


def register_delete(
    mcp: FastMCP, *, name: str, label: str, read_only: bool, deleter: HelperGetter = _DEFAULT_EDITOR
) -> None:
    if read_only:
        return

    @mcp.tool(name=f"{name}_delete", description=f"Delete a {label} by id.")
    async def _delete(
        id: Annotated[str, Field(description="Entity id to delete")],
    ) -> dict:
        deleter(get_client()).delete(id=id)
        return {"deleted": id}
