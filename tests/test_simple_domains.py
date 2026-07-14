import pytest
from fastmcp import FastMCP
from opencti_mcp import client
from opencti_mcp.tools import (
    malware, threat_actors, intrusion_sets, campaigns,
    attack_patterns, tools as tools_mod, vulnerabilities, incidents,
)

CASES = [
    (malware, "malware", "malware"),
    (threat_actors, "threat_actor_group", "threat_actors"),
    (intrusion_sets, "intrusion_set", "intrusion_sets"),
    (campaigns, "campaign", "campaigns"),
    (attack_patterns, "attack_pattern", "attack_patterns"),
    (tools_mod, "tool", "tools"),
    (vulnerabilities, "vulnerability", "vulnerabilities"),
    (incidents, "incident", "incidents"),
]


def _fake(attr):
    class F:
        def list(self, **kw): return [{"id": "1"}]
        def read(self, **kw): return {"id": kw["id"]}
        def create(self, **kw): return {"id": "new", **kw}
    fake = type("C", (), {})()
    setattr(fake, attr, F())
    return fake


@pytest.mark.parametrize("module,attr,name", CASES)
@pytest.mark.asyncio
async def test_domain_registers(monkeypatch, module, attr, name):
    monkeypatch.setattr(client, "get_client", lambda: _fake(attr))
    mcp = FastMCP(name="t")
    module.register(mcp, read_only=False)
    names = set((await mcp.get_tools()).keys())
    assert {f"{name}_list", f"{name}_get", f"{name}_create"} <= names


class _PerEntityHelper:
    """Mirrors real pycti per-entity classes (Malware, Incident, ...): no update_field/delete."""

    def list(self, **kw): return [{"id": "1"}]
    def read(self, **kw): return {"id": kw["id"]}
    def create(self, **kw): return {"id": "new", **kw}


class _StixDomainObjectHelper:
    def __init__(self):
        self.calls = {}

    def update_field(self, **kw):
        self.calls["update_field"] = kw
        return {"id": kw.get("id")}

    def delete(self, **kw):
        self.calls["delete"] = kw
        return None


@pytest.mark.parametrize("module,attr,name", CASES)
@pytest.mark.asyncio
async def test_domain_update_and_delete_route_to_stix_domain_object(monkeypatch, module, attr, name):
    per_entity = _PerEntityHelper()
    sdo = _StixDomainObjectHelper()
    fake = type("C", (), {attr: per_entity, "stix_domain_object": sdo})()
    monkeypatch.setattr("opencti_mcp.tools._common.get_client", lambda: fake)
    mcp = FastMCP(name="t")
    module.register(mcp, read_only=False)

    tools = await mcp.get_tools()
    await tools[f"{name}_update"].fn(id="e1", key="confidence", value="70")
    assert sdo.calls["update_field"] == {"id": "e1", "input": [{"key": "confidence", "value": "70"}]}

    result = await tools[f"{name}_delete"].fn(id="e1")
    assert sdo.calls["delete"] == {"id": "e1"}
    assert result == {"deleted": "e1"}
    assert not hasattr(per_entity, "update_field")
    assert not hasattr(per_entity, "delete")
