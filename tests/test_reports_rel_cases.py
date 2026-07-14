import pytest
from fastmcp import FastMCP
from opencti_mcp.tools import reports, relationships, cases
from opencti_mcp import client


def _fake(attr):
    class F:
        def list(self, **kw): return [{"id": "1"}]
        def read(self, **kw): return {"id": kw["id"]}
        def create(self, **kw): return {"id": "new", **kw}
    fake = type("C", (), {})()
    setattr(fake, attr, F())
    return fake


async def _names(mcp):
    return set((await mcp.get_tools()).keys())


@pytest.mark.asyncio
async def test_reports(monkeypatch):
    monkeypatch.setattr(client, "get_client", lambda: _fake("report"))
    mcp = FastMCP(name="t")
    reports.register(mcp, read_only=False)
    assert {"reports_list", "reports_get", "reports_create"} <= await _names(mcp)


@pytest.mark.asyncio
async def test_relationships(monkeypatch):
    monkeypatch.setattr(client, "get_client", lambda: _fake("stix_core_relationship"))
    mcp = FastMCP(name="t")
    relationships.register(mcp, read_only=False)
    assert {"relationships_list", "relationships_create"} <= await _names(mcp)


@pytest.mark.asyncio
async def test_cases(monkeypatch):
    monkeypatch.setattr(client, "get_client", lambda: _fake("case_incident"))
    mcp = FastMCP(name="t")
    cases.register(mcp, read_only=False)
    assert {"cases_list", "cases_get", "cases_create"} <= await _names(mcp)
