import pytest
from fastmcp import FastMCP
from opencti_mcp import client, tools as tools_pkg


def _fake_full_client():
    class F:
        def list(self, **kw): return []
        def read(self, **kw): return {}
        def create(self, **kw): return {}
    fake = type("C", (), {})()
    for attr in [
        "indicator", "stix_cyber_observable", "report", "malware",
        "threat_actor_group", "intrusion_set", "campaign", "attack_pattern",
        "tool", "vulnerability", "incident", "case_incident",
        "stix_core_relationship", "label", "marking_definition",
    ]:
        setattr(fake, attr, F())
    return fake


@pytest.mark.asyncio
async def test_register_all_read_only(monkeypatch):
    monkeypatch.setattr(client, "get_client", lambda: _fake_full_client())
    mcp = FastMCP(name="t")
    tools_pkg.register_all(mcp, read_only=True)
    names = set((await mcp.get_tools()).keys())
    assert "indicators_list" in names
    assert "graphql_query" in names
    assert not any(n.endswith("_create") for n in names)


@pytest.mark.asyncio
async def test_register_all_writable(monkeypatch):
    monkeypatch.setattr(client, "get_client", lambda: _fake_full_client())
    mcp = FastMCP(name="t")
    tools_pkg.register_all(mcp, read_only=False)
    names = set((await mcp.get_tools()).keys())
    assert "indicators_create" in names
    assert "relationships_create" in names
