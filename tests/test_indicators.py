import pytest
from fastmcp import FastMCP
from opencti_mcp.tools import indicators
from opencti_mcp import client


class FakeIndicator:
    def __init__(self):
        self.created = None

    def list(self, **kw):
        return [{"id": "ind-1", "name": "evil.com"}]

    def read(self, **kw):
        return {"id": kw["id"]}

    def create(self, **kw):
        self.created = kw
        return {"id": "ind-new", **kw}


@pytest.fixture
def fake_client(monkeypatch):
    fake = type("C", (), {})()
    fake.indicator = FakeIndicator()
    monkeypatch.setattr(client, "get_client", lambda: fake)
    return fake


async def _names(mcp):
    return set((await mcp.get_tools()).keys())


@pytest.mark.asyncio
async def test_read_only_registers_reads_only(fake_client):
    mcp = FastMCP(name="t")
    indicators.register(mcp, read_only=True)
    names = await _names(mcp)
    assert {"indicators_list", "indicators_get"} <= names
    assert "indicators_create" not in names
    assert "indicators_update" not in names
    assert "indicators_delete" not in names


@pytest.mark.asyncio
async def test_writable_registers_create(fake_client):
    mcp = FastMCP(name="t")
    indicators.register(mcp, read_only=False)
    names = await _names(mcp)
    assert {"indicators_create", "indicators_update", "indicators_delete"} <= names
