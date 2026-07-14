"""Invocation tests pinning the `or None` behavior for the remaining optional
list[str] params converted to plain-array schema (see test_array_param_schema.py
for the schema-shape assertions, and test_tool_invocation.py for indicators_create/
reports_create/observables_create coverage).

For each converted param this confirms:
- passing a non-empty list still forwards that list to pycti unchanged.
- omitting the param entirely (schema default is `[]`) forwards `None` to
  pycti, matching pre-change behavior when the param was omitted entirely.
"""

from __future__ import annotations

import pytest
from fastmcp import FastMCP

from opencti_mcp.tools import intrusion_sets, malware, search, threat_actors, tools as tools_mod


class FakeMalwareHelper:
    def __init__(self):
        self.calls = {}

    def create(self, **kw):
        self.calls["create"] = kw
        return {"id": "new", **kw}


class FakeIntrusionSetHelper:
    def __init__(self):
        self.calls = {}

    def create(self, **kw):
        self.calls["create"] = kw
        return {"id": "new", **kw}


class FakeToolHelper:
    def __init__(self):
        self.calls = {}

    def create(self, **kw):
        self.calls["create"] = kw
        return {"id": "new", **kw}


class FakeThreatActorHelper:
    def __init__(self):
        self.calls = {}

    def create(self, **kw):
        self.calls["create"] = kw
        return {"id": "new", **kw}


class FakeCoreObjectHelper:
    def __init__(self):
        self.calls = {}

    def list(self, **kw):
        self.calls["list"] = kw
        return []


async def _fn(mcp: FastMCP, tool_name: str):
    tools = await mcp.get_tools()
    return tools[tool_name].fn


@pytest.mark.asyncio
async def test_malware_create_forwards_lists_and_empty_as_none(monkeypatch):
    helper = FakeMalwareHelper()
    fake_client = type("C", (), {"malware": helper})()
    monkeypatch.setattr("opencti_mcp.tools.malware.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    malware.register(mcp, read_only=False)
    fn = await _fn(mcp, "malware_create")

    await fn(name="M", malware_types=["ransomware"], marking_ids=["m1"], label_ids=["l1"])
    call = helper.calls["create"]
    assert call["malware_types"] == ["ransomware"]
    assert call["objectMarking"] == ["m1"]
    assert call["objectLabel"] == ["l1"]

    await fn(name="M2")
    call = helper.calls["create"]
    assert call["malware_types"] is None
    assert call["objectMarking"] is None
    assert call["objectLabel"] is None


@pytest.mark.asyncio
async def test_intrusion_sets_create_forwards_lists_and_empty_as_none(monkeypatch):
    helper = FakeIntrusionSetHelper()
    fake_client = type("C", (), {"intrusion_set": helper})()
    monkeypatch.setattr("opencti_mcp.tools.intrusion_sets.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    intrusion_sets.register(mcp, read_only=False)
    fn = await _fn(mcp, "intrusion_sets_create")

    await fn(name="IS", marking_ids=["m1"], label_ids=["l1"])
    call = helper.calls["create"]
    assert call["objectMarking"] == ["m1"]
    assert call["objectLabel"] == ["l1"]

    await fn(name="IS2")
    call = helper.calls["create"]
    assert call["objectMarking"] is None
    assert call["objectLabel"] is None


@pytest.mark.asyncio
async def test_tools_create_forwards_lists_and_empty_as_none(monkeypatch):
    helper = FakeToolHelper()
    fake_client = type("C", (), {"tool": helper})()
    monkeypatch.setattr("opencti_mcp.tools.tools.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    tools_mod.register(mcp, read_only=False)
    fn = await _fn(mcp, "tools_create")

    await fn(name="T", tool_types=["remote-access"], marking_ids=["m1"], label_ids=["l1"])
    call = helper.calls["create"]
    assert call["tool_types"] == ["remote-access"]
    assert call["objectMarking"] == ["m1"]
    assert call["objectLabel"] == ["l1"]

    await fn(name="T2")
    call = helper.calls["create"]
    assert call["tool_types"] is None
    assert call["objectMarking"] is None
    assert call["objectLabel"] is None


@pytest.mark.asyncio
async def test_threat_actors_create_forwards_list_and_empty_as_none(monkeypatch):
    helper = FakeThreatActorHelper()
    fake_client = type("C", (), {"threat_actor_group": helper})()
    monkeypatch.setattr("opencti_mcp.tools.threat_actors.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    threat_actors.register(mcp, read_only=False)
    fn = await _fn(mcp, "threat_actors_create")

    await fn(name="TA", threat_actor_types=["crime-syndicate"])
    call = helper.calls["create"]
    assert call["threat_actor_types"] == ["crime-syndicate"]

    await fn(name="TA2")
    call = helper.calls["create"]
    assert call["threat_actor_types"] is None


@pytest.mark.asyncio
async def test_search_all_forwards_list_and_empty_as_none(monkeypatch):
    helper = FakeCoreObjectHelper()
    fake_client = type("C", (), {"stix_core_object": helper})()
    monkeypatch.setattr("opencti_mcp.tools.search.get_client", lambda: fake_client)
    mcp = FastMCP(name="t")
    search.register(mcp, read_only=True)
    fn = await _fn(mcp, "search_all")

    await fn(query="emotet", types=["Malware"])
    assert helper.calls["list"]["types"] == ["Malware"]

    await fn(query="emotet")
    assert helper.calls["list"]["types"] is None
