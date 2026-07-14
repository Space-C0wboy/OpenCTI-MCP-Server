"""Invocation and registration tests for the new read-only enhancement tools:

- relationships_for_entity (src/opencti_mcp/tools/relationships.py)
- observables_by_value (src/opencti_mcp/tools/observables.py)
- search_all (src/opencti_mcp/tools/search.py)

Follows the invocation-test style established in tests/test_tool_invocation.py:
build a fresh FastMCP, call `module.register(mcp, read_only=...)`, pull the tool
body via `(await mcp.get_tools())[name].fn`, and invoke it against a fake helper
that records the kwargs it was called with.
"""

from __future__ import annotations

import pytest
from fastmcp import FastMCP

from opencti_mcp import tools as tools_pkg
from opencti_mcp.tools import observables, relationships, search


class FakeRelationshipHelper:
    def __init__(self):
        self.calls = {}

    def list(self, **kw):
        self.calls["list"] = kw
        return []


class FakeObservableHelper:
    def __init__(self):
        self.calls = {}

    def list(self, **kw):
        self.calls["list"] = kw
        return []


class FakeCoreObjectHelper:
    def __init__(self):
        self.calls = {}

    def list(self, **kw):
        self.calls["list"] = kw
        return []


async def _fn(mcp: FastMCP, tool_name: str):
    tools = await mcp.get_tools()
    return tools[tool_name].fn


@pytest.mark.asyncio
async def test_relationships_for_entity_registered_read_only(monkeypatch):
    helper = FakeRelationshipHelper()
    fake_client = type("C", (), {"stix_core_relationship": helper})()
    monkeypatch.setattr("opencti_mcp.tools.relationships.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    relationships.register(mcp, read_only=True)

    names = set((await mcp.get_tools()).keys())
    assert "relationships_for_entity" in names

    fn = await _fn(mcp, "relationships_for_entity")
    await fn(entity_id="e1", relationship_type="uses")

    assert helper.calls["list"] == {
        "fromOrToId": "e1",
        "relationship_type": "uses",
        "first": 25,
        "withPagination": True,
    }


@pytest.mark.asyncio
async def test_observables_by_value_registered_read_only(monkeypatch):
    helper = FakeObservableHelper()
    fake_client = type("C", (), {"stix_cyber_observable": helper})()
    monkeypatch.setattr("opencti_mcp.tools.observables.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    observables.register(mcp, read_only=True)

    names = set((await mcp.get_tools()).keys())
    assert "observables_by_value" in names

    fn = await _fn(mcp, "observables_by_value")
    await fn(value="1.2.3.4")

    assert helper.calls["list"] == {
        "filters": {
            "mode": "and",
            "filters": [{"key": "value", "values": ["1.2.3.4"], "operator": "eq"}],
            "filterGroups": [],
        },
        "first": 25,
        "withPagination": True,
    }


@pytest.mark.asyncio
async def test_search_all_registered_read_only(monkeypatch):
    helper = FakeCoreObjectHelper()
    fake_client = type("C", (), {"stix_core_object": helper})()
    monkeypatch.setattr("opencti_mcp.tools.search.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    search.register(mcp, read_only=True)

    names = set((await mcp.get_tools()).keys())
    assert "search_all" in names

    fn = await _fn(mcp, "search_all")
    await fn(query="emotet", types=["Malware"])

    assert helper.calls["list"] == {
        "search": "emotet",
        "types": ["Malware"],
        "first": 25,
        "withPagination": True,
    }


def _fake_full_client_with_new_helpers():
    class F:
        def list(self, **kw):
            return []

        def read(self, **kw):
            return {}

        def create(self, **kw):
            return {}

    fake = type("C", (), {})()
    for attr in [
        "indicator",
        "stix_cyber_observable",
        "report",
        "malware",
        "threat_actor_group",
        "intrusion_set",
        "campaign",
        "attack_pattern",
        "tool",
        "vulnerability",
        "incident",
        "case_incident",
        "stix_core_relationship",
        "label",
        "marking_definition",
        "stix_core_object",
    ]:
        setattr(fake, attr, F())
    return fake


@pytest.mark.asyncio
async def test_register_all_read_only_includes_new_read_tools(monkeypatch):
    from opencti_mcp import client

    monkeypatch.setattr(client, "get_client", lambda: _fake_full_client_with_new_helpers())
    mcp = FastMCP(name="t")
    tools_pkg.register_all(mcp, read_only=True)
    names = set((await mcp.get_tools()).keys())

    assert "search_all" in names
    assert "relationships_for_entity" in names
    assert "observables_by_value" in names
