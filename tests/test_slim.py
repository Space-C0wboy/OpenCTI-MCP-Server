"""Tests for the response-slimming helpers in src/opencti_mcp/tools/_common.py.

pycti's raw entity payloads are large (nested `objects` arrays, duplicate
`*Ids` arrays, full `createdBy`/`objectMarking`/`objectLabel` sub-objects) and
can blow past the MCP output size limit for list tools. `_slim_entity` /
`slim_result` trim that down; `guard_size` protects single-entity `_get`
reads from the same problem.
"""

from __future__ import annotations

import pytest
from fastmcp import FastMCP

from opencti_mcp.tools import indicators
from opencti_mcp.tools._common import _slim_entity, guard_size, slim_result


def test_slim_entity_drops_bulky_and_duplicate_keys():
    entity = {
        "id": "r1",
        "name": "Report",
        "created_at": "2024-01-01T00:00:00Z",
        "x_opencti_score": 50,
        "objects": [{"id": "a"}, {"id": "b"}],
        "config": {"broker": "secret"},
        "parent_types": ["Stix-Domain-Object"],
        "spec_version": "2.1",
        "objectMarkingIds": ["m1"],
        "objectLabelIds": ["l1"],
    }

    slim = _slim_entity(entity)

    assert "objects" not in slim
    assert "config" not in slim
    assert "parent_types" not in slim
    assert "spec_version" not in slim
    assert "objectMarkingIds" not in slim
    assert "objectLabelIds" not in slim
    assert slim["id"] == "r1"
    assert slim["name"] == "Report"
    assert slim["created_at"] == "2024-01-01T00:00:00Z"
    assert slim["x_opencti_score"] == 50


def test_slim_entity_trims_created_by():
    entity = {"createdBy": {"id": "o1", "name": "Org", "description": "long text..."}}
    slim = _slim_entity(entity)
    assert slim["createdBy"] == {"id": "o1", "name": "Org"}


def test_slim_entity_trims_object_marking_to_definitions():
    entity = {
        "objectMarking": [
            {"id": "m1", "definition": "TLP:CLEAR", "x_opencti_color": "#fff"},
            {"id": "m2", "definition": "TLP:AMBER"},
        ]
    }
    slim = _slim_entity(entity)
    assert slim["objectMarking"] == ["TLP:CLEAR", "TLP:AMBER"]


def test_slim_entity_trims_object_label_to_values():
    entity = {"objectLabel": [{"id": "l1", "value": "malware"}, {"id": "l2", "value": "apt"}]}
    slim = _slim_entity(entity)
    assert slim["objectLabel"] == ["malware", "apt"]


def test_slim_entity_trims_from_and_to_refs():
    entity = {
        "from": {
            "id": "e1",
            "entity_type": "Indicator",
            "name": "evil.com",
            "standard_id": "indicator--123",
            "objects": [1, 2, 3],
        },
        "to": {
            "id": "e2",
            "entity_type": "Malware",
            "name": "Emotet",
            "standard_id": "malware--456",
        },
    }
    slim = _slim_entity(entity)
    assert slim["from"] == {
        "id": "e1",
        "entity_type": "Indicator",
        "name": "evil.com",
        "standard_id": "indicator--123",
    }
    assert slim["to"] == {
        "id": "e2",
        "entity_type": "Malware",
        "name": "Emotet",
        "standard_id": "malware--456",
    }


def test_slim_entity_passthrough_for_non_dict():
    assert _slim_entity("not-a-dict") == "not-a-dict"
    assert _slim_entity(None) is None


def test_slim_entity_drops_content():
    entity = {"id": "r1", "content": "x" * 10000}
    slim = _slim_entity(entity)
    assert "content" not in slim
    assert slim["id"] == "r1"


def test_slim_entity_trims_external_references():
    entity = {
        "externalReferences": [
            {
                "source_name": "MITRE",
                "url": "https://example.com/1",
                "external_id": "T1059",
                "description": "long text...",
                "hashes": [{"algorithm": "SHA-256", "hash": "abc"}],
                "importFiles": [{"id": "f1", "name": "report.pdf"}],
            },
            {"source_name": "OtherSrc", "url": "https://example.com/2", "external_id": None},
        ]
    }
    slim = _slim_entity(entity)
    assert slim["externalReferences"] == [
        {"source_name": "MITRE", "url": "https://example.com/1", "external_id": "T1059"},
        {"source_name": "OtherSrc", "url": "https://example.com/2", "external_id": None},
    ]


def test_slim_result_on_paginated_dict_slims_entities_and_preserves_pagination():
    result = {
        "entities": [
            {"id": "1", "objects": [1, 2]},
            {"id": "2", "objects": [3, 4]},
        ],
        "pagination": {"globalCount": 2, "hasNextPage": False},
    }
    slimmed = slim_result(result)
    assert slimmed["pagination"] == {"globalCount": 2, "hasNextPage": False}
    assert slimmed["entities"] == [{"id": "1"}, {"id": "2"}]


def test_slim_result_on_bare_list_slims_each_element():
    result = [{"id": "1", "objects": []}, {"id": "2", "config": {}}]
    slimmed = slim_result(result)
    assert slimmed == [{"id": "1"}, {"id": "2"}]


def test_slim_result_passthrough_for_other_shapes():
    assert slim_result(None) is None
    assert slim_result({"foo": "bar"}) == {"foo": "bar"}
    assert slim_result("x") == "x"


def test_slim_result_size_backstop_truncates_oversized_entities(monkeypatch):
    monkeypatch.setattr("opencti_mcp.tools._common._SIZE_LIMIT", 2000)
    result = {
        "entities": [{"id": str(i), "blob": "x" * 500} for i in range(10)],
        "pagination": {"globalCount": 10},
    }
    slimmed = slim_result(result)
    assert len(slimmed["entities"]) < 10
    assert "_note" in slimmed
    assert slimmed["pagination"] == {"globalCount": 10}


def test_slim_result_small_result_unchanged_no_note():
    result = {
        "entities": [{"id": "1"}, {"id": "2"}],
        "pagination": {"globalCount": 2},
    }
    slimmed = slim_result(result)
    assert "_note" not in slimmed
    assert slimmed["entities"] == [{"id": "1"}, {"id": "2"}]


def test_guard_size_returns_small_entity_unchanged():
    entity = {"id": "1", "name": "small"}
    assert guard_size(entity) is entity


def test_guard_size_slims_and_annotates_oversized_entity():
    entity = {
        "id": "1",
        "name": "big",
        "objects": [{"id": str(i)} for i in range(50)],
    }
    guarded = guard_size(entity, limit=50)
    assert "objects" not in guarded
    assert guarded["id"] == "1"
    assert guarded["name"] == "big"
    assert "_note" in guarded


class FakeIndicatorHelper:
    def list(self, **kw):
        return {
            "entities": [
                {
                    "id": "i1",
                    "name": "x",
                    "objects": [1, 2, 3],
                    "objectMarkingIds": ["m"],
                    "createdBy": {"id": "o1", "name": "Org", "description": "long"},
                    "objectMarking": [{"definition": "TLP:CLEAR"}],
                }
            ],
            "pagination": {"globalCount": 1},
        }


@pytest.mark.asyncio
async def test_indicators_list_returns_slimmed_entities(monkeypatch):
    fake_client = type("C", (), {"indicator": FakeIndicatorHelper()})()
    monkeypatch.setattr("opencti_mcp.tools._common.get_client", lambda: fake_client)

    mcp = FastMCP(name="t")
    indicators.register(mcp, read_only=True)

    tools = await mcp.get_tools()
    fn = tools["indicators_list"].fn
    result = await fn()

    entity = result["entities"][0]
    assert "objects" not in entity
    assert "objectMarkingIds" not in entity
    assert entity["createdBy"] == {"id": "o1", "name": "Org"}
    assert entity["objectMarking"] == ["TLP:CLEAR"]
