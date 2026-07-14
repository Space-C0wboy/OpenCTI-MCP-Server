from __future__ import annotations

import pytest
from fastmcp import FastMCP

from opencti_mcp import client
from opencti_mcp.tools import identities, register_all


class FakeIdentityHelper:
    """Mirrors the real pycti Identity class: no update_field/delete methods."""

    def __init__(self):
        self.calls = {}

    def list(self, **kw):
        self.calls["list"] = kw
        return [{"id": "1"}]

    def read(self, **kw):
        self.calls["read"] = kw
        return {"id": kw.get("id")}

    def create(self, **kw):
        self.calls["create"] = kw
        return {"id": "new", **kw}


class FakeStixDomainObjectHelper:
    def __init__(self):
        self.calls = {}

    def update_field(self, **kw):
        self.calls["update_field"] = kw
        return {"id": kw.get("id")}

    def delete(self, **kw):
        self.calls["delete"] = kw
        return None


async def _fn(mcp: FastMCP, tool_name: str):
    tools = await mcp.get_tools()
    return tools[tool_name].fn


@pytest.mark.asyncio
async def test_read_only_registers_reads_but_not_create_or_delete(monkeypatch):
    helper = FakeIdentityHelper()
    fake_client = type("C", (), {"identity": helper})()
    monkeypatch.setattr("opencti_mcp.tools._common.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    identities.register(mcp, read_only=True)

    names = set((await mcp.get_tools()).keys())
    assert "identities_list" in names
    assert "identities_get" in names
    assert "identities_create" not in names
    assert "identities_delete" not in names


@pytest.mark.asyncio
async def test_writable_registers_create_and_delete(monkeypatch):
    helper = FakeIdentityHelper()
    fake_client = type("C", (), {"identity": helper})()
    monkeypatch.setattr("opencti_mcp.tools._common.get_client", lambda: fake_client)
    monkeypatch.setattr("opencti_mcp.tools.identities.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    identities.register(mcp, read_only=False)

    names = set((await mcp.get_tools()).keys())
    assert "identities_create" in names
    assert "identities_delete" in names


@pytest.mark.asyncio
async def test_identities_delete_routes_to_stix_domain_object(monkeypatch):
    helper = FakeIdentityHelper()
    sdo = FakeStixDomainObjectHelper()
    fake_client = type("C", (), {"identity": helper, "stix_domain_object": sdo})()
    monkeypatch.setattr("opencti_mcp.tools._common.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    identities.register(mcp, read_only=False)

    fn = await _fn(mcp, "identities_delete")
    result = await fn(id="idn-1")

    assert sdo.calls["delete"] == {"id": "idn-1"}
    assert result == {"deleted": "idn-1"}
    assert not hasattr(helper, "delete")


@pytest.mark.asyncio
async def test_create_organization_maps_kwargs(monkeypatch):
    helper = FakeIdentityHelper()
    fake_client = type("C", (), {"identity": helper})()
    monkeypatch.setattr("opencti_mcp.tools.identities.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    identities.register(mcp, read_only=False)

    fn = await _fn(mcp, "identities_create")
    await fn(
        name="Acme",
        identity_class="organization",
        marking_ids=["m1"],
        label_ids=["l1"],
    )

    call = helper.calls["create"]
    assert call["type"] == "Organization"
    assert call["name"] == "Acme"
    assert call["objectMarking"] == ["m1"]
    assert call["objectLabel"] == ["l1"]


@pytest.mark.asyncio
async def test_create_individual_maps_type(monkeypatch):
    helper = FakeIdentityHelper()
    fake_client = type("C", (), {"identity": helper})()
    monkeypatch.setattr("opencti_mcp.tools.identities.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    identities.register(mcp, read_only=False)

    fn = await _fn(mcp, "identities_create")
    await fn(name="Jane Doe", identity_class="individual")

    call = helper.calls["create"]
    assert call["type"] == "Individual"


@pytest.mark.asyncio
async def test_register_all_read_only_has_identities_list_but_not_create(monkeypatch):
    class F:
        def list(self, **kw): return []
        def read(self, **kw): return {}
        def create(self, **kw): return {}
    fake = type("C", (), {})()
    for attr in [
        "indicator", "stix_cyber_observable", "report", "malware",
        "threat_actor_group", "intrusion_set", "campaign", "attack_pattern",
        "tool", "vulnerability", "incident", "case_incident",
        "stix_core_relationship", "label", "marking_definition", "identity",
    ]:
        setattr(fake, attr, F())
    monkeypatch.setattr(client, "get_client", lambda: fake)
    mcp = FastMCP(name="t")
    register_all(mcp, read_only=True)
    names = set((await mcp.get_tools()).keys())
    assert "identities_list" in names
    assert "identities_create" not in names
