---
name: opencti-usage
description: Use when working with the OpenCTI threat-intelligence platform via the `opencti` MCP tools — explains OpenCTI's STIX data model, entity types, indicators vs observables, relationships, containers, TLP markings, confidence, connectors/ingestion, and RBAC, and maps each concept to the right MCP tool. Load before creating, relating, importing, or reasoning about OpenCTI knowledge.
---

# OpenCTI Usage

## Overview

OpenCTI is a threat-intelligence platform built around a single **knowledge
graph**: everything it knows is expressed as STIX 2.1 objects (entities) and
the relationships between them. **Containers** (Reports, Groupings, Cases,
Incidents) group related entities and relationships into a citable, shareable
"story." **Markings** (TLP and friends) segregate who can see what, on top of
group/role-based access. **Connectors** are the independent processes that
ingest, enrich, and export data into and out of that graph. Almost everything
you do through the `opencti` MCP tools is either reading a slice of this
graph or adding/editing nodes and edges in it.

## Concept map

- **Observables vs Indicators** — an Observable is a raw fact with no
  built-in judgment (an IP, a hash); an Indicator is the SDO that adds
  detection intent (a pattern, a validity window) and is usually "based on"
  one or more observables.
- **Relationships** — typed, directional edges (`from` → `to`) such as
  `uses`, `indicates`, `targets`, each carrying its own confidence,
  timestamps, and markings — independent of the confidence on the entities
  they connect.
- **Containers / Reports** — Reports, Groupings, Cases, and Incidents bundle
  entities, observables, and relationships via `object_refs` into one
  citable unit with provenance back to a source.
- **Markings / TLP** — marking definitions (TLP:CLEAR…TLP:RED, PAP, etc.)
  drive data segregation: only users authorized for a marking can see the
  objects carrying it.
- **Confidence / scoring** — confidence (0-100) rates the credibility of
  information itself (on entities and on relationships); score rates how
  dangerous an indicator/observable currently is; reliability rates the
  source — three distinct axes.
- **Connectors / enrichment** — independent processes (ingestion, enrichment,
  internal-import/export) that move data into, around, and out of the
  platform; `entity_ask_enrichment` triggers one on demand for a given
  entity.

## When to use which tool

- Look up a known IOC by its raw value → `observables_by_value`.
- Don't know the type, or searching broadly → `search_all`.
- Most-recent N of a known type → `<name>_list` with
  `order_by="created_at"`, `descending=true`.
- What's already connected to an entity → `relationships_for_entity`.
- Create a new entity (indicator, observable, malware, report, etc.) →
  `<name>_create`.
- Link two existing entities → `relationships_create(from_id, to_id,
  relationship_type, confidence)`.
- Bulk-load a STIX bundle from an external source → `stix_import_bundle`.
- Trigger enrichment on an entity → `entity_ask_enrichment(entity_id,
  connector_id)`.
- Anything not covered by a typed tool (e.g. attaching objects to a case,
  status templates) → `graphql_query`.
- **Read-only by default**: this server starts with `OPENCTI_READ_ONLY=true`
  unless configured otherwise — create/update/delete tools and mutating
  `graphql_query` calls only work once it's set to `false`.

## References

- `references/data-model.md` — read this when you need the big picture: the
  SDO/SCO/SRO/meta object families and how object identity (`entity_type`,
  `standard_id`, internal id) works.
- `references/entities.md` — read this when you need a quick lookup of what
  a given entity type represents and which tools manage it.
- `references/indicators-vs-observables.md` — read this when you're unsure
  whether something should be an Observable or an Indicator, or how the two
  connect.
- `references/relationships.md` — read this when creating or reasoning about
  edges between entities: types, direction, and relationship-level
  confidence.
- `references/containers.md` — read this when bundling entities into a
  Report, Grouping, Case, or Incident, or deciding which container type
  fits.
- `references/markings-and-tlp.md` — read this when setting or reasoning
  about TLP/marking-based data segregation on an object.
- `references/confidence-and-scoring.md` — read this when you need to set or
  interpret confidence, indicator/observable score, or source reliability.
- `references/admin-connectors.md` — read this when working with ingestion,
  enrichment, or export connectors and their health/status.
- `references/rbac-and-orgs.md` — read this when reasoning about users,
  groups, roles, capabilities, or organization-based segregation.
- `references/api-and-graphql.md` — read this when you need the raw GraphQL
  API details behind `graphql_query` (endpoint, auth, schema conventions).
- `references/mcp-tool-map.md` — read this when you need the exact
  action→tool mapping for this server plus the operational gotchas found by
  exercising it live.
