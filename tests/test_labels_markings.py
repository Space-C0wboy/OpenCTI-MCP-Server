import pytest
from fastmcp import FastMCP
from opencti_mcp import client
from opencti_mcp.tools import labels_markings


class F:
    def __init__(self):
        self.calls = {}

    def list(self, **kw): return [{"id": "1"}]
    def read(self, **kw): return {"id": kw["id"]}
    def create(self, **kw): return {"id": "new", **kw}

    def update_field(self, **kw):
        self.calls["update_field"] = kw
        return {"id": kw.get("id")}

    def delete(self, **kw):
        self.calls["delete"] = kw
        return None


@pytest.fixture
def fake_client(monkeypatch):
    fake = type("C", (), {})()
    fake.label = F()
    fake.marking_definition = F()
    monkeypatch.setattr(client, "get_client", lambda: fake)
    monkeypatch.setattr("opencti_mcp.tools._common.get_client", lambda: fake)
    return fake


@pytest.mark.asyncio
async def test_read_only(fake_client):
    mcp = FastMCP(name="t")
    labels_markings.register(mcp, read_only=True)
    names = set((await mcp.get_tools()).keys())
    assert {"labels_list", "markings_list", "markings_get", "labels_get"} <= names
    assert "labels_create" not in names


@pytest.mark.asyncio
async def test_writable_has_labels_create(fake_client):
    mcp = FastMCP(name="t")
    labels_markings.register(mcp, read_only=False)
    names = set((await mcp.get_tools()).keys())
    assert "labels_create" in names


@pytest.mark.asyncio
async def test_labels_update_and_delete_route_to_label_helper(fake_client):
    mcp = FastMCP(name="t")
    labels_markings.register(mcp, read_only=False)
    tools = await mcp.get_tools()

    await tools["labels_update"].fn(id="lbl-1", key="color", value="#ff0000")
    assert fake_client.label.calls["update_field"] == {
        "id": "lbl-1",
        "input": [{"key": "color", "value": "#ff0000"}],
    }
    assert "update_field" not in fake_client.marking_definition.calls

    result = await tools["labels_delete"].fn(id="lbl-1")
    assert fake_client.label.calls["delete"] == {"id": "lbl-1"}
    assert result == {"deleted": "lbl-1"}
    assert "delete" not in fake_client.marking_definition.calls
