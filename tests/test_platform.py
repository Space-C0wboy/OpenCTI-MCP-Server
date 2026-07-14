"""Tests for the platform/ops tools module (src/opencti_mcp/tools/platform.py):

- users_list / users_get / groups_list / groups_get (via register_reads factory)
- connectors_list / connectors_get
- files_for_entity
- entity_ask_enrichment (write, gated on read_only)

Follows the invocation-test style established in tests/test_tool_invocation.py and
tests/test_enhancements.py: build a fresh FastMCP, call `module.register(...)`, pull
the tool body via `(await mcp.get_tools())[name].fn`, and invoke it against a fake
client that records the kwargs it was called with.
"""

from __future__ import annotations

import pytest
from fastmcp import FastMCP

from opencti_mcp import tools as tools_pkg
from opencti_mcp.tools import _common, platform


class FakeEntityHelper:
    def __init__(self):
        self.calls = {}

    def list(self, **kw):
        self.calls["list"] = kw
        return []

    def read(self, **kw):
        self.calls["read"] = kw
        return {"id": kw.get("id")}


class FakeConnectorHelper:
    def __init__(self):
        self.calls = {}

    def list(self, **kw):
        self.calls["list"] = kw
        return []

    def read(self, **kw):
        self.calls["read"] = kw
        return {"id": kw.get("connector_id"), "active": True}


class FakeStixCoreObjectHelper:
    def __init__(self):
        self.calls = {}

    def list_files(self, **kw):
        self.calls["list_files"] = kw
        return []

    def ask_enrichment(self, **kw):
        self.calls["ask_enrichment"] = kw
        return None


def _fake_client():
    fake = type("C", (), {})()
    fake.user = FakeEntityHelper()
    fake.group = FakeEntityHelper()
    fake.connector = FakeConnectorHelper()
    fake.stix_core_object = FakeStixCoreObjectHelper()
    return fake


async def _fn(mcp: FastMCP, tool_name: str):
    tools = await mcp.get_tools()
    return tools[tool_name].fn


@pytest.mark.asyncio
async def test_read_only_registers_all_read_tools_but_not_enrichment(monkeypatch):
    fake_client = _fake_client()
    monkeypatch.setattr(platform, "get_client", lambda: fake_client)
    monkeypatch.setattr(_common, "get_client", lambda: fake_client)

    mcp = FastMCP(name="t")
    platform.register(mcp, read_only=True)
    names = set((await mcp.get_tools()).keys())

    assert {
        "users_list",
        "users_get",
        "groups_list",
        "groups_get",
        "connectors_list",
        "connectors_get",
        "files_for_entity",
    } <= names
    assert "entity_ask_enrichment" not in names


@pytest.mark.asyncio
async def test_writable_registers_entity_ask_enrichment(monkeypatch):
    fake_client = _fake_client()
    monkeypatch.setattr(platform, "get_client", lambda: fake_client)
    monkeypatch.setattr(_common, "get_client", lambda: fake_client)

    mcp = FastMCP(name="t")
    platform.register(mcp, read_only=False)
    names = set((await mcp.get_tools()).keys())

    assert "entity_ask_enrichment" in names


@pytest.mark.asyncio
async def test_connectors_get_invokes_connector_read(monkeypatch):
    fake_client = _fake_client()
    monkeypatch.setattr(platform, "get_client", lambda: fake_client)
    monkeypatch.setattr(_common, "get_client", lambda: fake_client)

    mcp = FastMCP(name="t")
    platform.register(mcp, read_only=True)

    fn = await _fn(mcp, "connectors_get")
    await fn(connector_id="c1")

    assert fake_client.connector.calls["read"] == {"connector_id": "c1"}


@pytest.mark.asyncio
async def test_files_for_entity_invokes_list_files(monkeypatch):
    fake_client = _fake_client()
    monkeypatch.setattr(platform, "get_client", lambda: fake_client)
    monkeypatch.setattr(_common, "get_client", lambda: fake_client)

    mcp = FastMCP(name="t")
    platform.register(mcp, read_only=True)

    fn = await _fn(mcp, "files_for_entity")
    await fn(entity_id="e1")

    assert fake_client.stix_core_object.calls["list_files"] == {"id": "e1"}


@pytest.mark.asyncio
async def test_entity_ask_enrichment_invokes_ask_enrichment_and_returns_summary(monkeypatch):
    fake_client = _fake_client()
    monkeypatch.setattr(platform, "get_client", lambda: fake_client)
    monkeypatch.setattr(_common, "get_client", lambda: fake_client)

    mcp = FastMCP(name="t")
    platform.register(mcp, read_only=False)

    fn = await _fn(mcp, "entity_ask_enrichment")
    result = await fn(entity_id="e1", connector_id="c1")

    assert fake_client.stix_core_object.calls["ask_enrichment"] == {
        "element_id": "e1",
        "connector_id": "c1",
    }
    assert result == {"enrichment_requested": "e1", "connector_id": "c1"}


def _fake_full_client_with_platform_helpers():
    class F:
        def list(self, **kw):
            return []

        def read(self, **kw):
            return {}

        def create(self, **kw):
            return {}

    class Connector:
        def list(self, **kw):
            return []

        def read(self, **kw):
            return {}

    class StixCoreObject:
        def list(self, **kw):
            return []

        def list_files(self, **kw):
            return []

        def ask_enrichment(self, **kw):
            return None

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
        "user",
        "group",
    ]:
        setattr(fake, attr, F())
    fake.connector = Connector()
    fake.stix_core_object = StixCoreObject()
    return fake


@pytest.mark.asyncio
async def test_register_all_read_only_includes_platform_read_tools(monkeypatch):
    from opencti_mcp import client

    monkeypatch.setattr(client, "get_client", lambda: _fake_full_client_with_platform_helpers())
    mcp = FastMCP(name="t")
    tools_pkg.register_all(mcp, read_only=True)
    names = set((await mcp.get_tools()).keys())

    assert "connectors_get" in names
    assert "users_list" in names
    assert "entity_ask_enrichment" not in names
