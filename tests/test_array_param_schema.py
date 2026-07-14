"""Locks in that optional list[str] tool params render as plain-array JSON schema.

Some MCP clients mis-serialize params whose schema is `anyOf: [array, null]`
(they send the list JSON-encoded as a string, which pydantic then rejects with
a list_type error). Using `Annotated[list[str], Field(default_factory=list)]`
instead of `Annotated[list[str] | None, ...] = None` renders as a plain
`{"type": "array", "items": {"type": "string"}}` schema with no `anyOf`, which
these clients handle correctly. This test builds the full registered server
and asserts a representative set of params has that shape.
"""

from __future__ import annotations

import pytest
from fastmcp import FastMCP

from opencti_mcp import client, tools as tools_pkg


def _fake_full_client():
    class F:
        def list(self, **kw):
            return []

        def read(self, **kw):
            return {}

        def create(self, **kw):
            return {}

    fake = type("C", (), {})()
    for attr in [
        "indicator", "stix_cyber_observable", "report", "malware",
        "threat_actor_group", "intrusion_set", "campaign", "attack_pattern",
        "tool", "vulnerability", "incident", "case_incident",
        "stix_core_relationship", "label", "marking_definition",
        "stix_core_object",
    ]:
        setattr(fake, attr, F())
    return fake


# (tool_name, param_name)
ARRAY_PARAMS = [
    ("indicators_create", "marking_ids"),
    ("indicators_create", "label_ids"),
    ("reports_create", "object_ids"),
    ("malware_create", "malware_types"),
    ("search_all", "types"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("tool_name,param_name", ARRAY_PARAMS)
async def test_optional_list_param_has_plain_array_schema(monkeypatch, tool_name, param_name):
    monkeypatch.setattr(client, "get_client", lambda: _fake_full_client())
    mcp = FastMCP(name="t")
    tools_pkg.register_all(mcp, read_only=False)

    tools = await mcp.get_tools()
    schema = tools[tool_name].parameters["properties"][param_name]

    assert schema.get("type") == "array"
    assert "anyOf" not in schema


# (tool_name, expected required params) -- regression guard: adding a keyword-only
# marker or a `default_factory` list param must not make sibling scalar optional
# params (e.g. description, valid_from, confidence) show up as required.
REQUIRED_PARAMS = [
    ("indicators_create", {"name", "pattern", "pattern_type", "x_opencti_main_observable_type"}),
    ("reports_create", {"name", "published"}),
    ("observables_create", {"observable_key", "observable_value"}),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("tool_name,expected_required", REQUIRED_PARAMS)
async def test_required_params_exclude_optional_scalars_and_lists(monkeypatch, tool_name, expected_required):
    monkeypatch.setattr(client, "get_client", lambda: _fake_full_client())
    mcp = FastMCP(name="t")
    tools_pkg.register_all(mcp, read_only=False)

    tools = await mcp.get_tools()
    required = set(tools[tool_name].parameters.get("required") or [])

    assert required == expected_required
