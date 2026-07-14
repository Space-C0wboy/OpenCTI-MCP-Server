from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from ..client import get_client
from ._common import register_delete, register_reads, register_update, slim_result

_HELPER = lambda c: c.stix_cyber_observable  # noqa: E731
_NAME = "observables"
_LABEL = "observable"


def register(mcp: FastMCP, *, read_only: bool) -> None:
    register_reads(mcp, name=_NAME, label=_LABEL, helper=_HELPER)
    register_update(mcp, name=_NAME, label=_LABEL, read_only=read_only, editor=_HELPER)
    register_delete(mcp, name=_NAME, label=_LABEL, read_only=read_only, deleter=_HELPER)

    @mcp.tool(
        name="observables_by_value",
        description="Look up STIX cyber observables by exact value (e.g. an IP address, domain, URL, or file hash).",
    )
    async def _by_value(
        value: Annotated[
            str, Field(description="The observable value to match exactly, e.g. '1.2.3.4' or a SHA-256 hash")
        ],
        first: Annotated[int, Field(description="Max results (1-500)", ge=1, le=500)] = 25,
    ) -> Any:
        return slim_result(
            get_client().stix_cyber_observable.list(
                filters={
                    "mode": "and",
                    "filters": [{"key": "value", "values": [value], "operator": "eq"}],
                    "filterGroups": [],
                },
                first=first,
                withPagination=True,
            )
        )

    if read_only:
        return

    @mcp.tool(
        name="observables_create",
        description=(
            "Create a STIX cyber observable. 'StixFile.*' keys are accepted and "
            "normalized to 'File.*'. Values for keys ending in '.number' (e.g. "
            "'Autonomous-System.number') are coerced to integers. Use "
            "additional_hashes to attach extra file hashes (e.g. 'SHA-1:...', "
            "'MD5:...') alongside the primary hash on a file observable."
        ),
    )
    async def _create(
        observable_key: Annotated[
            str, Field(description="Observable key, e.g. 'IPv4-Addr.value' or 'Domain-Name.value'")
        ],
        observable_value: Annotated[str, Field(description="The observable value")],
        description: Annotated[str | None, Field(description="Description")] = None,
        marking_ids: Annotated[
            list[str], Field(description="Marking-definition ids to attach (e.g. a TLP marking id)")
        ] = [],
        label_ids: Annotated[
            list[str], Field(description="Label ids to attach")
        ] = [],
        additional_hashes: Annotated[
            list[str],
            Field(description="Extra file hashes as 'ALGO:VALUE', e.g. 'SHA-1:abc', 'MD5:def'"),
        ] = [],
    ) -> Any:
        key = observable_key
        if key.startswith("StixFile."):
            key = "File." + key[len("StixFile.") :]

        value: Any = observable_value
        if key.endswith(".number"):
            try:
                value = int(observable_value)
            except ValueError as exc:
                raise ValueError(
                    f"observable_value for {key} must be an integer, got {observable_value!r}"
                ) from exc

        client = get_client()
        if additional_hashes and key.startswith("File.hashes."):
            algo = key.split(".")[-1]  # e.g. "SHA-256"
            hashes = {algo: observable_value}
            for entry in additional_hashes:
                a, sep, v = entry.partition(":")
                if not sep or not a.strip() or not v.strip():
                    raise ValueError(
                        f"additional_hashes entry must be 'ALGO:VALUE', got {entry!r}"
                    )
                hashes[a.strip()] = v.strip()
            return client.stix_cyber_observable.create(
                observableData={"type": "File", "hashes": hashes},
                objectMarking=marking_ids or None,
                objectLabel=label_ids or None,
            )
        return client.stix_cyber_observable.create(
            simple_observable_key=key,
            simple_observable_value=value,
            simple_observable_description=description,
            objectMarking=marking_ids or None,
            objectLabel=label_ids or None,
        )
