"""Tests for the STIX bundle import/export tools module
(src/opencti_mcp/tools/stix_bundle.py):

- stix_export_entity (read)
- stix_export_list (read)
- stix_import_bundle (write, gated on read_only)

Follows the invocation-test style established in tests/test_tool_invocation.py and
tests/test_platform.py: build a fresh FastMCP, call `module.register(...)`, pull the
tool body via `(await mcp.get_tools())[name].fn`, and invoke it against a fake client
that records the kwargs it was called with.
"""

from __future__ import annotations

import pytest
from fastmcp import FastMCP

from opencti_mcp import tools as tools_pkg
from opencti_mcp.tools import stix_bundle


class FakeStix2Helper:
    def __init__(self, export_selected_result=None):
        self.calls = {}
        self._export_selected_result = export_selected_result or {"type": "bundle"}

    def get_stix_bundle_or_object_from_entity_id(self, **kw):
        self.calls["get_stix_bundle_or_object_from_entity_id"] = kw
        return {"type": "bundle"}

    def export_selected(self, **kw):
        self.calls["export_selected"] = kw
        return self._export_selected_result

    def import_bundle_from_json(self, **kw):
        self.calls["import_bundle_from_json"] = kw
        return (["a", "b"], [])


class FakeStixCoreObjectHelper:
    def __init__(self, entities=None):
        self.calls = {}
        self._entities = entities if entities is not None else [{"id": "c1", "entity_type": "Campaign"}]

    def list(self, **kw):
        self.calls["list"] = kw
        return {"entities": self._entities, "pagination": {}}


def _fake_client(export_selected_result=None, entities=None):
    fake = type("C", (), {})()
    fake.stix2 = FakeStix2Helper(export_selected_result=export_selected_result)
    fake.stix_core_object = FakeStixCoreObjectHelper(entities=entities)
    return fake


async def _fn(mcp: FastMCP, tool_name: str):
    tools = await mcp.get_tools()
    return tools[tool_name].fn


@pytest.mark.asyncio
async def test_read_only_registers_reads_but_not_import(monkeypatch):
    fake_client = _fake_client()
    monkeypatch.setattr(stix_bundle, "get_client", lambda: fake_client)

    mcp = FastMCP(name="t")
    stix_bundle.register(mcp, read_only=True)
    names = set((await mcp.get_tools()).keys())

    assert {"stix_export_entity", "stix_export_list"} <= names
    assert "stix_import_bundle" not in names


@pytest.mark.asyncio
async def test_writable_registers_import(monkeypatch):
    fake_client = _fake_client()
    monkeypatch.setattr(stix_bundle, "get_client", lambda: fake_client)

    mcp = FastMCP(name="t")
    stix_bundle.register(mcp, read_only=False)
    names = set((await mcp.get_tools()).keys())

    assert "stix_import_bundle" in names


@pytest.mark.asyncio
async def test_stix_export_entity_invokes_helper(monkeypatch):
    fake_client = _fake_client()
    monkeypatch.setattr(stix_bundle, "get_client", lambda: fake_client)

    mcp = FastMCP(name="t")
    stix_bundle.register(mcp, read_only=True)

    fn = await _fn(mcp, "stix_export_entity")
    await fn(entity_type="Malware", entity_id="m1")

    assert fake_client.stix2.calls["get_stix_bundle_or_object_from_entity_id"] == {
        "entity_type": "Malware",
        "entity_id": "m1",
        "mode": "simple",
    }


@pytest.mark.asyncio
async def test_stix_export_list_invokes_helper(monkeypatch):
    entities = [{"id": "c1", "entity_type": "Campaign"}]
    bundle = {"type": "bundle", "objects": [{"id": "c1"}]}
    fake_client = _fake_client(export_selected_result=bundle, entities=entities)
    monkeypatch.setattr(stix_bundle, "get_client", lambda: fake_client)

    mcp = FastMCP(name="t")
    stix_bundle.register(mcp, read_only=True)

    fn = await _fn(mcp, "stix_export_list")
    result = await fn(entity_type="Report", first=10, mode="full")

    assert fake_client.stix_core_object.calls["list"] == {
        "types": ["Report"],
        "first": 10,
        "withPagination": True,
        "withFiles": True,
    }
    assert fake_client.stix2.calls["export_selected"] == {
        "entities_list": entities,
        "mode": "full",
    }
    assert result == bundle


@pytest.mark.asyncio
async def test_stix_export_list_simple_mode_passes_with_files_false(monkeypatch):
    entities = [{"id": "c1", "entity_type": "Campaign"}]
    bundle = {"type": "bundle", "objects": [{"id": "c1"}]}
    fake_client = _fake_client(export_selected_result=bundle, entities=entities)
    monkeypatch.setattr(stix_bundle, "get_client", lambda: fake_client)

    mcp = FastMCP(name="t")
    stix_bundle.register(mcp, read_only=True)

    fn = await _fn(mcp, "stix_export_list")
    await fn(entity_type="Campaign", first=5, mode="simple")

    assert fake_client.stix_core_object.calls["list"] == {
        "types": ["Campaign"],
        "first": 5,
        "withPagination": True,
        "withFiles": False,
    }


@pytest.mark.asyncio
async def test_stix_export_list_returns_note_when_bundle_too_large(monkeypatch):
    entities = [{"id": "c1", "entity_type": "Campaign"}]
    bundle = {"type": "bundle", "objects": [{"id": "c1", "name": "a" * 200}]}
    fake_client = _fake_client(export_selected_result=bundle, entities=entities)
    monkeypatch.setattr(stix_bundle, "get_client", lambda: fake_client)
    monkeypatch.setattr(stix_bundle, "_SIZE_LIMIT", 50)

    mcp = FastMCP(name="t")
    stix_bundle.register(mcp, read_only=True)

    fn = await _fn(mcp, "stix_export_list")
    result = await fn(entity_type="Campaign", first=25)

    assert "_note" in result
    assert result["object_count"] == 1
    assert result["entity_type"] == "Campaign"
    assert result["first"] == 25
    assert "objects" not in result


@pytest.mark.asyncio
async def test_stix_import_bundle_invokes_helper_and_returns_summary(monkeypatch):
    fake_client = _fake_client()
    monkeypatch.setattr(stix_bundle, "get_client", lambda: fake_client)

    mcp = FastMCP(name="t")
    stix_bundle.register(mcp, read_only=False)

    fn = await _fn(mcp, "stix_import_bundle")
    result = await fn(bundle_json='{"type":"bundle"}', update=True)

    assert fake_client.stix2.calls["import_bundle_from_json"] == {
        "json_data": '{"type":"bundle"}',
        "update": True,
    }
    assert result == {"imported_count": 2, "failed_count": 0}


def _fake_full_client_with_stix2_helper():
    class Stix2:
        def get_stix_bundle_or_object_from_entity_id(self, **kw):
            return {}

        def export_list(self, **kw):
            return {}

        def import_bundle_from_json(self, **kw):
            return ([], [])

    fake = type("C", (), {})()
    fake.stix2 = Stix2()
    return fake


@pytest.mark.asyncio
async def test_register_all_read_only_includes_stix_export_not_import(monkeypatch):
    from opencti_mcp import client

    monkeypatch.setattr(client, "get_client", lambda: _fake_full_client_with_stix2_helper())
    mcp = FastMCP(name="t")
    tools_pkg.register_all(mcp, read_only=True)
    names = set((await mcp.get_tools()).keys())

    assert "stix_export_entity" in names
    assert "stix_import_bundle" not in names
