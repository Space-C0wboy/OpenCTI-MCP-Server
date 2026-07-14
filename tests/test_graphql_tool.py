import pytest
from fastmcp import FastMCP
from opencti_mcp.tools import graphql as gql_tool
from opencti_mcp import client


@pytest.mark.asyncio
async def test_graphql_query_registered_and_runs(monkeypatch):
    monkeypatch.setattr(client, "run_raw_query", lambda q, v=None: {"data": {"ok": True}})
    mcp = FastMCP(name="t")
    gql_tool.register(mcp, read_only=False)
    names = set((await mcp.get_tools()).keys())
    assert "graphql_query" in names


@pytest.mark.asyncio
async def test_read_only_rejects_mutation(monkeypatch):
    monkeypatch.setattr(client, "run_raw_query", lambda q, v=None: {"data": {}})
    tool = gql_tool._make_query_callable(read_only=True)
    with pytest.raises(ValueError):
        await tool("mutation { deleteThing(id: \"1\") }", None)


@pytest.mark.asyncio
async def test_read_only_allows_query(monkeypatch):
    monkeypatch.setattr(gql_tool, "run_raw_query", lambda q, v=None: {"data": {"ok": 1}})
    tool = gql_tool._make_query_callable(read_only=True)
    assert await tool("query { things { id } }", None) == {"data": {"ok": 1}}
