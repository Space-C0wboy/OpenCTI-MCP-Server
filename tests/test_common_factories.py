import pytest
from fastmcp import FastMCP
from opencti_mcp.tools import _common
from opencti_mcp import client


class FakeHelper:
    def __init__(self):
        self.calls = {}

    def list(self, **kw):
        self.calls["list"] = kw
        return [{"id": "1"}]

    def read(self, **kw):
        self.calls["read"] = kw
        return {"id": kw.get("id")}

    def update_field(self, **kw):
        self.calls["update_field"] = kw
        return {"id": kw.get("id")}

    def delete(self, **kw):
        self.calls["delete"] = kw
        return None


async def _tool_names(mcp):
    return set((await mcp.get_tools()).keys())


@pytest.mark.asyncio
async def test_reads_register_list_and_get(monkeypatch):
    helper = FakeHelper()
    monkeypatch.setattr(client, "get_client", lambda: object())
    mcp = FastMCP(name="t")
    _common.register_reads(mcp, name="widgets", label="widget", helper=lambda c: helper)
    names = await _tool_names(mcp)
    assert {"widgets_list", "widgets_get"} <= names


@pytest.mark.asyncio
async def test_write_factories_skip_when_read_only():
    mcp = FastMCP(name="t")
    _common.register_update(mcp, name="w", label="w", read_only=True)
    _common.register_delete(mcp, name="w", label="w", read_only=True)
    names = await _tool_names(mcp)
    assert "w_update" not in names
    assert "w_delete" not in names


@pytest.mark.asyncio
async def test_write_factories_register_when_writable():
    mcp = FastMCP(name="t")
    _common.register_update(mcp, name="w", label="w", read_only=False)
    _common.register_delete(mcp, name="w", label="w", read_only=False)
    names = await _tool_names(mcp)
    assert {"w_update", "w_delete"} <= names


class FakePerEntityHelper:
    """A per-entity pycti helper (e.g. client.indicator) with NO update_field/delete.

    Mirrors real pycti classes like Indicator, Malware, etc., which lack these
    methods. If update/delete code ever wrongly routes to this helper, calling
    update_field/delete on it raises AttributeError.
    """

    def __init__(self):
        self.calls = {}

    def list(self, **kw):
        self.calls["list"] = kw
        return [{"id": "1"}]

    def read(self, **kw):
        self.calls["read"] = kw
        return {"id": kw.get("id")}


class FakeGenericHelper:
    """A generic pycti helper (stix_domain_object/observable/relationship/label)."""

    def __init__(self):
        self.calls = {}

    def update_field(self, **kw):
        self.calls["update_field"] = kw
        return {"id": kw.get("id")}

    def delete(self, **kw):
        self.calls["delete"] = kw
        return None


@pytest.mark.asyncio
async def test_register_update_defaults_to_stix_domain_object(monkeypatch):
    per_entity = FakePerEntityHelper()
    generic = FakeGenericHelper()
    fake_client = type("C", (), {"indicator": per_entity, "stix_domain_object": generic})()
    monkeypatch.setattr(_common, "get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    _common.register_update(mcp, name="w", label="w", read_only=False)
    fn = (await mcp.get_tools())["w_update"].fn

    await fn(id="abc", key="description", value="new")

    assert generic.calls["update_field"] == {"id": "abc", "input": [{"key": "description", "value": "new"}]}
    assert not hasattr(per_entity, "update_field")


@pytest.mark.asyncio
async def test_register_delete_defaults_to_stix_domain_object(monkeypatch):
    per_entity = FakePerEntityHelper()
    generic = FakeGenericHelper()
    fake_client = type("C", (), {"indicator": per_entity, "stix_domain_object": generic})()
    monkeypatch.setattr(_common, "get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    _common.register_delete(mcp, name="w", label="w", read_only=False)
    fn = (await mcp.get_tools())["w_delete"].fn

    result = await fn(id="abc")

    assert generic.calls["delete"] == {"id": "abc"}
    assert result == {"deleted": "abc"}
    assert not hasattr(per_entity, "delete")


@pytest.mark.asyncio
async def test_register_update_uses_custom_editor(monkeypatch):
    generic = FakeGenericHelper()
    fake_client = type("C", (), {"stix_cyber_observable": generic})()
    monkeypatch.setattr(_common, "get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    _common.register_update(
        mcp, name="w", label="w", read_only=False, editor=lambda c: c.stix_cyber_observable
    )
    fn = (await mcp.get_tools())["w_update"].fn

    await fn(id="abc", key="k", value="v")

    assert generic.calls["update_field"] == {"id": "abc", "input": [{"key": "k", "value": "v"}]}


@pytest.mark.asyncio
async def test_register_delete_uses_custom_deleter(monkeypatch):
    generic = FakeGenericHelper()
    fake_client = type("C", (), {"stix_core_relationship": generic})()
    monkeypatch.setattr(_common, "get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    _common.register_delete(
        mcp, name="w", label="w", read_only=False, deleter=lambda c: c.stix_core_relationship
    )
    fn = (await mcp.get_tools())["w_delete"].fn

    await fn(id="abc")

    assert generic.calls["delete"] == {"id": "abc"}
