# OpenCTI Data Model

OpenCTI represents everything it knows as a **knowledge graph**: nodes are
entities, edges are relationships between two entities, and the whole graph is
built on the STIX 2.1 standard. This file covers the model itself — object
families and how objects are identified — not entity-by-entity semantics (see
`entities.md` for that).

## Knowledge = entities + relationships

- A **node** describes an entity, which carries properties/attributes (e.g. a
  `Malware` object's name, description, malware type).
- An **edge** describes a relationship created between two entity nodes (e.g.
  the SDO `APT28` has a `uses` relationship to the SDO `Drovorub`).
- The platform's architecture is explicitly based on the **STIX 2.1
  standard**, so this graph can be described, exchanged, and enriched in a
  common, interoperable format.

OpenCTI also loosely distinguishes two layers of content that sit on top of
this same graph:

- **"Hot knowledge"** — analyses, cases, events, and observations added daily
  and requiring active analyst work (reports, groupings, malware analyses,
  etc.).
- **"Cold knowledge"** — the more stable contextual "encyclopedia" (threats,
  arsenal, techniques, entities, locations) that hot knowledge is linked
  against for context.

Both are just STIX objects and relationships in the same graph; the
distinction is about analyst workflow, not object type.

## The four object families

STIX 2.1 (and OpenCTI's platform extensions to it) organizes objects into
four families:

### 1. SDO — STIX Domain Objects

The core knowledge entities: things like Attack Patterns, Malware, Threat
Actors, Indicators, Reports, and Identities. OpenCTI also extends the SDO set
with platform-specific types for disinformation and cybercrime use cases
(e.g. channels, events, narratives).

**In this MCP:** most SDOs have their own tool family — `indicators_*`,
`malware_*`, `threat_actors_*`, `campaigns_*`, `intrusion_sets_*`,
`attack_patterns_*`, `reports_*`, `cases_*`, `incidents_*`,
`vulnerabilities_*`, `identities_*`, `tools_*`.

### 2. SCO — STIX Cyber Observables

Raw, immutable data points: IP addresses, domain names, hashes, and similar
low-level artifacts (e.g. `IPv4-Addr`, `Domain-Name`, `Url`, `StixFile`,
`Autonomous-System`). OpenCTI extends the standard SCO set to also cover
things like cryptocurrency wallets and user agents.

An Observable is distinct from an Indicator:

- An **Observable** is a raw fact with no built-in judgment of maliciousness
  — a legitimate IP address or domain is still a valid Observable.
- An **Indicator** is the SDO that adds detection context. It can be "based
  on" one or more Observables, and viewing an Indicator surfaces the
  Observables it's built from.

**In this MCP:** `observables_*` for CRUD, plus `observables_by_value` for
looking an observable up by its raw value instead of its id.

### 3. SRO — STIX Relationship Objects

Two core kinds:

- **Relationships** — typed edges such as `uses`, `targets`, `indicates`,
  `based-on`.
- **Sightings** — the other core SRO kind.

Platform extensions add further relationship types alongside the
disinformation/cybercrime SDOs (e.g. `amplifies`, `publishes`).

**In this MCP:** `relationships_*` for CRUD on a specific relationship, and
`relationships_for_entity` to list the relationships attached to a given
entity.

### 4. Meta objects (marking definitions, labels, external references, kill chain phases)

In raw STIX, things like the author (`created_by_ref`), TLP/markings
(`object_marking_refs`), labels, kill chain phases, and external references
are normally either simple attribute references or objects embedded directly
inside an entity.

OpenCTI instead models **all of these as relationships to full entities** in
the graph — "to be able to pivot more easily on labels, external references,
kill chain phases, marking definitions, etc." The translation between STIX's
embedded/nested format and OpenCTI's relationship-based graph model is
automated and transparent to users on import/export, so you don't need to
hand-manage the conversion — you just see markings, labels, and external
references as first-class, linkable objects in the platform.

**In this MCP:** `labels_*` for labels, `markings_get`/`markings_list` for
marking definitions. External references and kill chain phases are read as
part of an entity's detail rather than as their own dedicated tool family.

## Object identity: entity_type, standard_id, internal id

Every object in the graph carries more than one kind of identifier:

- **`entity_type`** — the object's type, e.g. `Indicator`, `StixFile`,
  `Report`, `Malware`, or the broader `Stix-Cyber-Observable`. This is the
  primary field used to filter and classify objects across the platform
  (dynamic filters, stored filters, live streams, triggers, and playbooks all
  support filtering by `entity_type`).
- **`standard_id`** — a deterministic STIX id in the standard
  `<type>--<uuid>` form (e.g. `indicator--...`), computed from the object's
  identifying properties so the same real-world object always resolves to
  the same STIX id.
- **internal id (`internal_id`)** — the platform's own UUID for the object,
  used internally by the database and GraphQL API.
- **`stix_ids`** — additional STIX ids an object may carry (e.g. from
  re-imports or upstream sources).

OpenCTI's filter system reflects this directly: there is a special `ids`
filter key that matches "any of the entity id, `internal_id`, `standard_id`
or `stix_ids`" in one shot, treating them as equivalent ways of pointing at
the same object.

**In this MCP:** `*_get` tools and the relationship tools accept either the
internal id or the `standard_id` when you need to reference a specific
entity — you don't have to know which kind of id you were handed.

## In this MCP: reading and writing across the model

Most tools in this server are namespaced per `entity_type` (e.g.
`indicators_list`, `indicators_get`, `observables_create`,
`relationships_for_entity`). Two tools cut across that per-type structure:

- **`search_all`** — a cross-type search over the knowledge graph, for when
  you don't know (or don't want to restrict to) a specific `entity_type`.
- **`graphql_query`** — a raw GraphQL escape hatch for anything not covered
  by a typed tool.

## Source

> OpenCTI docs (latest), distilled 2026-07-10.

- https://docs.opencti.io/latest/usage/data-model/
- https://docs.opencti.io/latest/usage/overview/
- https://docs.opencti.io/latest/usage/nested/
- https://docs.opencti.io/latest/usage/exploring-observations/
- https://docs.opencti.io/latest/reference/filters/
