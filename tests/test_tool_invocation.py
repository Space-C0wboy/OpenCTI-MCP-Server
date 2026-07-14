"""Invocation-level tests that pin the pycti kwarg mappings.

These tests go a step further than the existing registration tests: they
actually call the registered tool bodies and assert on the kwargs passed to
the underlying pycti helper. Registration-only tests can pass even if a
tool's body maps arguments incorrectly (e.g. `object_ids` never renamed to
`objects`), so this file exists to catch that class of bug.

Invocation mechanism: `await mcp.get_tools()` returns a dict of
name -> fastmcp.tools.tool.FunctionTool. Each FunctionTool exposes the
original async function as `.fn`, which can be awaited directly with
keyword arguments (bypassing MCP's JSON-RPC/schema layer entirely). This
was confirmed against the installed fastmcp==2.14.7.

Binding note: `_common.py` and the domain modules each do
`from ..client import get_client` at import time, so the name `get_client`
is bound separately in every module's namespace. Patching
`opencti_mcp.client.get_client` does not affect those already-bound names.
Reads/update/delete (registered via `_common.register_reads` etc.) must be
patched on `opencti_mcp.tools._common.get_client`; the `_create` tools
defined directly in `observables.py`, `reports.py`, and `relationships.py`
must be patched on their own module's `get_client` name.
"""

from __future__ import annotations

import pytest
from fastmcp import FastMCP

from opencti_mcp.tools import indicators, observables, relationships, reports


class FakeIndicatorHelper:
    """Mirrors the real pycti Indicator class: no update_field/delete methods."""

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
    """The generic pycti helper (client.stix_domain_object) that owns update/delete."""

    def __init__(self):
        self.calls = {}

    def update_field(self, **kw):
        self.calls["update_field"] = kw
        return {"id": kw.get("id")}

    def delete(self, **kw):
        self.calls["delete"] = kw
        return None


class FakeReportHelper:
    def __init__(self):
        self.calls = {}

    def list(self, **kw):
        return []

    def read(self, **kw):
        return {}

    def update_field(self, **kw):
        return {}

    def delete(self, **kw):
        return None

    def create(self, **kw):
        self.calls["create"] = kw
        return {"id": "new", **kw}


class FakeRelationshipHelper:
    def __init__(self):
        self.calls = {}

    def list(self, **kw):
        return []

    def read(self, **kw):
        return {}

    def update_field(self, **kw):
        self.calls["update_field"] = kw
        return {}

    def delete(self, **kw):
        self.calls["delete"] = kw
        return None

    def create(self, **kw):
        self.calls["create"] = kw
        return {"id": "new", **kw}


class FakeObservableHelper:
    def __init__(self):
        self.calls = {}

    def list(self, **kw):
        return []

    def read(self, **kw):
        return {}

    def update_field(self, **kw):
        self.calls["update_field"] = kw
        return {}

    def delete(self, **kw):
        self.calls["delete"] = kw
        return None

    def create(self, **kw):
        self.calls["create"] = kw
        return {"id": "new", **kw}


async def _fn(mcp: FastMCP, tool_name: str):
    tools = await mcp.get_tools()
    return tools[tool_name].fn


@pytest.mark.asyncio
async def test_indicators_list_maps_kwargs(monkeypatch):
    helper = FakeIndicatorHelper()
    fake_client = type("C", (), {"indicator": helper})()
    monkeypatch.setattr("opencti_mcp.tools._common.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    indicators.register(mcp, read_only=True)

    fn = await _fn(mcp, "indicators_list")
    await fn(search="x", first=5)

    assert helper.calls["list"] == {
        "search": "x",
        "first": 5,
        "after": None,
        "orderBy": None,
        "orderMode": None,
        "withPagination": True,
    }


@pytest.mark.asyncio
async def test_indicators_list_default_ordering_is_none(monkeypatch):
    helper = FakeIndicatorHelper()
    fake_client = type("C", (), {"indicator": helper})()
    monkeypatch.setattr("opencti_mcp.tools._common.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    indicators.register(mcp, read_only=True)

    fn = await _fn(mcp, "indicators_list")
    await fn(search="x", first=5)

    assert helper.calls["list"] == {
        "search": "x",
        "first": 5,
        "after": None,
        "orderBy": None,
        "orderMode": None,
        "withPagination": True,
    }


@pytest.mark.asyncio
async def test_indicators_list_order_by_descending(monkeypatch):
    helper = FakeIndicatorHelper()
    fake_client = type("C", (), {"indicator": helper})()
    monkeypatch.setattr("opencti_mcp.tools._common.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    indicators.register(mcp, read_only=True)

    fn = await _fn(mcp, "indicators_list")
    await fn(order_by="created_at")

    assert helper.calls["list"]["orderBy"] == "created_at"
    assert helper.calls["list"]["orderMode"] == "desc"


@pytest.mark.asyncio
async def test_indicators_list_order_by_ascending(monkeypatch):
    helper = FakeIndicatorHelper()
    fake_client = type("C", (), {"indicator": helper})()
    monkeypatch.setattr("opencti_mcp.tools._common.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    indicators.register(mcp, read_only=True)

    fn = await _fn(mcp, "indicators_list")
    await fn(order_by="created_at", descending=False)

    assert helper.calls["list"]["orderBy"] == "created_at"
    assert helper.calls["list"]["orderMode"] == "asc"


@pytest.mark.asyncio
async def test_indicators_get_maps_kwargs(monkeypatch):
    helper = FakeIndicatorHelper()
    fake_client = type("C", (), {"indicator": helper})()
    monkeypatch.setattr("opencti_mcp.tools._common.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    indicators.register(mcp, read_only=True)

    fn = await _fn(mcp, "indicators_get")
    await fn(id="abc")

    assert helper.calls["read"] == {"id": "abc"}


@pytest.mark.asyncio
async def test_indicators_delete_maps_kwargs_and_return_shape(monkeypatch):
    helper = FakeIndicatorHelper()
    sdo = FakeStixDomainObjectHelper()
    fake_client = type("C", (), {"indicator": helper, "stix_domain_object": sdo})()
    monkeypatch.setattr("opencti_mcp.tools._common.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    indicators.register(mcp, read_only=False)

    fn = await _fn(mcp, "indicators_delete")
    result = await fn(id="abc")

    # Delete must route to the generic stix_domain_object helper, not the
    # per-entity indicator helper (which lacks a delete method in real pycti).
    assert sdo.calls["delete"] == {"id": "abc"}
    assert result == {"deleted": "abc"}
    assert not hasattr(helper, "delete")


@pytest.mark.asyncio
async def test_indicators_update_routes_to_stix_domain_object(monkeypatch):
    helper = FakeIndicatorHelper()
    sdo = FakeStixDomainObjectHelper()
    fake_client = type("C", (), {"indicator": helper, "stix_domain_object": sdo})()
    monkeypatch.setattr("opencti_mcp.tools._common.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    indicators.register(mcp, read_only=False)

    fn = await _fn(mcp, "indicators_update")
    await fn(id="abc", key="confidence", value="80")

    assert sdo.calls["update_field"] == {"id": "abc", "input": [{"key": "confidence", "value": "80"}]}
    assert not hasattr(helper, "update_field")


@pytest.mark.asyncio
async def test_reports_create_maps_object_ids_to_objects(monkeypatch):
    helper = FakeReportHelper()
    fake_client = type("C", (), {"report": helper})()
    monkeypatch.setattr("opencti_mcp.tools.reports.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    reports.register(mcp, read_only=False)

    fn = await _fn(mcp, "reports_create")
    await fn(name="R", published="2024-01-01T00:00:00Z", object_ids=["a", "b"])

    call = helper.calls["create"]
    assert call["objects"] == ["a", "b"]
    assert "object_ids" not in call
    # Omitted list params (report_types, marking_ids, label_ids) must forward as
    # None to pycti, matching pre-change behavior when these were omitted.
    assert call["report_types"] is None
    assert call["objectMarking"] is None
    assert call["objectLabel"] is None


@pytest.mark.asyncio
async def test_indicators_create_maps_marking_and_label_ids(monkeypatch):
    helper = FakeIndicatorHelper()
    fake_client = type("C", (), {"indicator": helper})()
    monkeypatch.setattr("opencti_mcp.tools.indicators.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    indicators.register(mcp, read_only=False)

    fn = await _fn(mcp, "indicators_create")
    await fn(
        name="I",
        pattern="[ipv4-addr:value = '1.2.3.4']",
        pattern_type="stix",
        x_opencti_main_observable_type="IPv4-Addr",
        marking_ids=["m1"],
        label_ids=["l1"],
    )

    call = helper.calls["create"]
    assert call["objectMarking"] == ["m1"]
    assert call["objectLabel"] == ["l1"]


@pytest.mark.asyncio
async def test_indicators_create_omitted_lists_forward_none(monkeypatch):
    helper = FakeIndicatorHelper()
    fake_client = type("C", (), {"indicator": helper})()
    monkeypatch.setattr("opencti_mcp.tools.indicators.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    indicators.register(mcp, read_only=False)

    fn = await _fn(mcp, "indicators_create")
    await fn(
        name="I",
        pattern="[ipv4-addr:value = '1.2.3.4']",
        pattern_type="stix",
        x_opencti_main_observable_type="IPv4-Addr",
    )

    call = helper.calls["create"]
    assert call["objectMarking"] is None
    assert call["objectLabel"] is None


@pytest.mark.asyncio
async def test_relationships_create_maps_kwargs(monkeypatch):
    helper = FakeRelationshipHelper()
    fake_client = type("C", (), {"stix_core_relationship": helper})()
    monkeypatch.setattr("opencti_mcp.tools.relationships.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    relationships.register(mcp, read_only=False)

    fn = await _fn(mcp, "relationships_create")
    await fn(from_id="a", to_id="b", relationship_type="uses")

    call = helper.calls["create"]
    assert call["fromId"] == "a"
    assert call["toId"] == "b"
    assert call["relationship_type"] == "uses"


@pytest.mark.asyncio
async def test_relationships_update_and_delete_route_to_stix_core_relationship(monkeypatch):
    helper = FakeRelationshipHelper()
    fake_client = type("C", (), {"stix_core_relationship": helper})()
    monkeypatch.setattr("opencti_mcp.tools._common.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    relationships.register(mcp, read_only=False)

    update_fn = await _fn(mcp, "relationships_update")
    await update_fn(id="rel-1", key="confidence", value="50")
    assert helper.calls["update_field"] == {"id": "rel-1", "input": [{"key": "confidence", "value": "50"}]}

    delete_fn = await _fn(mcp, "relationships_delete")
    result = await delete_fn(id="rel-1")
    assert helper.calls["delete"] == {"id": "rel-1"}
    assert result == {"deleted": "rel-1"}


@pytest.mark.asyncio
async def test_observables_update_and_delete_route_to_stix_cyber_observable(monkeypatch):
    helper = FakeObservableHelper()
    fake_client = type("C", (), {"stix_cyber_observable": helper})()
    monkeypatch.setattr("opencti_mcp.tools._common.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    observables.register(mcp, read_only=False)

    update_fn = await _fn(mcp, "observables_update")
    await update_fn(id="obs-1", key="x_opencti_score", value="90")
    assert helper.calls["update_field"] == {
        "id": "obs-1",
        "input": [{"key": "x_opencti_score", "value": "90"}],
    }

    delete_fn = await _fn(mcp, "observables_delete")
    result = await delete_fn(id="obs-1")
    assert helper.calls["delete"] == {"id": "obs-1"}
    assert result == {"deleted": "obs-1"}


@pytest.mark.asyncio
async def test_observables_create_maps_kwargs(monkeypatch):
    helper = FakeObservableHelper()
    fake_client = type("C", (), {"stix_cyber_observable": helper})()
    monkeypatch.setattr("opencti_mcp.tools.observables.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    observables.register(mcp, read_only=False)

    fn = await _fn(mcp, "observables_create")
    await fn(observable_key="IPv4-Addr.value", observable_value="1.2.3.4")

    call = helper.calls["create"]
    assert call["simple_observable_key"] == "IPv4-Addr.value"
    assert call["simple_observable_value"] == "1.2.3.4"
    assert call["simple_observable_description"] is None
    # Omitted list params must forward as None to pycti, matching
    # pre-change behavior when these were omitted.
    assert call["objectMarking"] is None
    assert call["objectLabel"] is None


@pytest.mark.asyncio
async def test_observables_create_normalizes_stixfile_key(monkeypatch):
    helper = FakeObservableHelper()
    fake_client = type("C", (), {"stix_cyber_observable": helper})()
    monkeypatch.setattr("opencti_mcp.tools.observables.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    observables.register(mcp, read_only=False)

    fn = await _fn(mcp, "observables_create")
    await fn(observable_key="StixFile.hashes.SHA-256", observable_value="abc")

    call = helper.calls["create"]
    assert call["simple_observable_key"] == "File.hashes.SHA-256"
    assert call["simple_observable_value"] == "abc"


@pytest.mark.asyncio
async def test_observables_create_coerces_autonomous_system_number(monkeypatch):
    helper = FakeObservableHelper()
    fake_client = type("C", (), {"stix_cyber_observable": helper})()
    monkeypatch.setattr("opencti_mcp.tools.observables.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    observables.register(mcp, read_only=False)

    fn = await _fn(mcp, "observables_create")
    await fn(observable_key="Autonomous-System.number", observable_value="215439")

    call = helper.calls["create"]
    assert call["simple_observable_value"] == 215439
    assert isinstance(call["simple_observable_value"], int)


@pytest.mark.asyncio
async def test_observables_create_rejects_non_integer_autonomous_system_number(monkeypatch):
    helper = FakeObservableHelper()
    fake_client = type("C", (), {"stix_cyber_observable": helper})()
    monkeypatch.setattr("opencti_mcp.tools.observables.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    observables.register(mcp, read_only=False)

    fn = await _fn(mcp, "observables_create")
    with pytest.raises(ValueError):
        await fn(observable_key="Autonomous-System.number", observable_value="not-a-number")


@pytest.mark.asyncio
async def test_observables_create_multi_hash_file_uses_observable_data(monkeypatch):
    helper = FakeObservableHelper()
    fake_client = type("C", (), {"stix_cyber_observable": helper})()
    monkeypatch.setattr("opencti_mcp.tools.observables.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    observables.register(mcp, read_only=False)

    fn = await _fn(mcp, "observables_create")
    await fn(
        observable_key="File.hashes.SHA-256",
        observable_value="<sha256>",
        additional_hashes=["SHA-1:aaa", "MD5:bbb"],
    )

    call = helper.calls["create"]
    assert "simple_observable_key" not in call
    assert call["observableData"]["type"] == "File"
    assert call["observableData"]["hashes"] == {
        "SHA-256": "<sha256>",
        "SHA-1": "aaa",
        "MD5": "bbb",
    }


@pytest.mark.asyncio
async def test_observables_create_rejects_malformed_additional_hash_entry(monkeypatch):
    helper = FakeObservableHelper()
    fake_client = type("C", (), {"stix_cyber_observable": helper})()
    monkeypatch.setattr("opencti_mcp.tools.observables.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    observables.register(mcp, read_only=False)

    fn = await _fn(mcp, "observables_create")
    with pytest.raises(ValueError):
        await fn(
            observable_key="File.hashes.SHA-256",
            observable_value="<sha256>",
            additional_hashes=["not-a-valid-entry"],
        )
