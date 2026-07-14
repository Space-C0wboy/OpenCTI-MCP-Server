import pytest
from fastmcp import FastMCP
from opencti_mcp.tools import observables
from opencti_mcp import client


class FakeObs:
    def list(self, **kw): return [{"id": "obs-1"}]
    def read(self, **kw): return {"id": kw["id"]}
    def create(self, **kw): return {"id": "obs-new", **kw}


@pytest.fixture
def fake_client(monkeypatch):
    fake = type("C", (), {})()
    fake.stix_cyber_observable = FakeObs()
    monkeypatch.setattr(client, "get_client", lambda: fake)
    return fake


@pytest.mark.asyncio
async def test_registers_reads_and_create(fake_client):
    mcp = FastMCP(name="t")
    observables.register(mcp, read_only=False)
    names = set((await mcp.get_tools()).keys())
    assert {"observables_list", "observables_get", "observables_create"} <= names
