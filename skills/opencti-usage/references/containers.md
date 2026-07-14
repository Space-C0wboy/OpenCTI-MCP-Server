# OpenCTI Containers

A **container** is a STIX Domain Object that bundles other objects together. Per the STIX 2.1 standard, containers use the `object_refs` attribute — an array of references to the entities, observables, and relationships that belong to it. In the OpenCTI UI this array is exposed as the container's **objects** (its "Knowledge"): the set of things you can list, add to, remove from, or graph. A container doesn't just point at loose objects — it asserts that those objects share a context (an incident, an intelligence product, an investigation).

Containers are the main mechanism for turning scattered entities/relationships into a coherent, shareable "story" — a report you publish, a case you work, a note you leave on an investigation.

## Container types

**Report** — the primary way to bundle documented intelligence. Per STIX 2.1, a Report is "a collection of threat intelligence focused on one or more topics, such as a description of a threat actor, malware, or attack technique, including context and related details." Reports anchor provenance: they typically represent an external source (a vendor threat-intel writeup, blog post, press article, conference talk, MISP event) plus everything extracted from it — indicators, entities, relationships. Because everything in a report traces back to where it came from, Reports are the standard way to bundle an incident's IOCs, entities, and relationships into one citable, exportable unit. Reports additionally expose Graph, Timeline, Correlation, and Matrix (ATT&CK) views over their objects.

**Grouping** — a container like a Report, but it does *not* represent a finished intelligence product. It only asserts that the referenced objects share an explicit context (unlike a bare STIX bundle, which makes no such claim). Use a Grouping for ongoing analysis or collaborative investigation that hasn't matured into a citable report yet — the STIX spec frames it as something that, "given sufficient analysis, would mature to convey an incident or threat report as a STIX Report object." Groupings have the same Overview/Knowledge/Content/Entities/Observables/Data tabs as Reports, but no Timeline view.

**Note** — unstructured analyst commentary attached to any object or relationship in the platform. STIX 2.1 describes a Note as text meant "to provide further context and/or ... additional analysis not contained in the STIX Objects ... which the Note relates to." Notes are how an analyst records reasoning, caveats, or context that doesn't fit a formal field.

**Opinion** — an assessment by one party of whether the information in another object (or container) is correct. Used to capture disagreement, corroboration, or confidence judgments from a different analyst/source than the one who produced the original content — e.g. building "lessons learned" on a closed case.

**External References** — not a container of *objects*, but the mechanism containers (and any entity) use to cite sources outside the platform: "pointers to information represented outside of STIX." A Report's external references are typically the source document(s) it was built from; a Malware object's external reference might be its ID in an external database.

**Cases** — containers for organizing response/analytical work, distinct from Reports (which document a finished product) and from Incidents (which represent the event itself). A Case can hold the same kind of Knowledge as a Report — SDOs and SCOs — and the UI marks whether each object was added directly or inferred by the reasoning engine. Three case subtypes:
- **Incident Response** — the context and actions taken *responding to* a specific incident, not the incident itself.
- **Request for Information (RFI)** — used when a stakeholder asks a CTI team for analysis on a subject, whether tied to an active incident or a trending threat.
- **Request for Takedown (RFT)** — used to track infrastructure-removal requests (e.g. a malicious domain or phishing mailbox), which usually involve coordinating with an external provider under time pressure.

A separate, non-investigative kind of case is **Feedback** — a way for platform users to flag a concern about knowledge or platform behavior; each submission becomes its own case for the team to act on.

### Tasks within Cases

A **Task** is "an action to be performed in the context of a Case." Tasks are usually assigned to one user, though important ones can involve several. They can be added directly to a case or pulled in from a **case template** — a predefined checklist configured under Settings → Taxonomies → Case templates and then attached to a case from its overview. Each task has its own Overview/Content/Data/History tabs, and a case's Tasks tab lets you filter by assignee, due date, and status. A user can also see everything assigned to them across cases from a personal dashboard.

## How membership works

Membership in a container is just the `object_refs` array being populated with the STIX IDs of entities, observables, or relationships. Concretely:

- **At creation time**, a container can be created with an initial set of objects to reference.
- **After creation**, the UI lets you add or remove entities/observables from the container's object list directly (there's no separate "join" object — you're editing the container's `object_refs`).
- Relationships between the referenced objects can themselves be included in `object_refs`, which is what lets a container be rendered as a connected graph rather than just an unordered list.
- Creating a *new* entity from inside a container pre-populates that entity's markings from the container's own markings, so knowledge added to a classified report inherits its classification by default.

## In this MCP

- `reports_create(..., object_ids=[...])` is the primary way to group entities into a report: pass the STIX/internal IDs of the entities you want as the report's initial Knowledge. It also accepts `marking_ids` and `label_ids`. There is no separate "add to report" tool in this MCP — set membership at creation via `object_ids`, or use `graphql_query` to update `objects` on an existing report.
- `cases_create` creates an **Incident Response** case (name, description, severity, priority). Unlike `reports_create`, it does **not** currently accept `object_ids` in this MCP — a newly created case starts with no attached Knowledge. If you need objects on the case immediately, add them via `graphql_query`, or attach them after the fact through the OpenCTI UI. RFI, RFT, and Feedback case subtypes are not exposed as separate tools; only the Incident Response subtype is.
- There is no dedicated `groupings_*`, `notes_*`, or `opinions_*` tool family in this MCP — use `graphql_query` if you need to create or read these container types directly.
- `relationships_create` / `relationships_for_entity` operate on the SROs that can themselves be referenced inside a container's `object_refs`; see `relationships.md` for that model.

## Source

> OpenCTI docs (latest), distilled 2026-07-10.

- https://docs.opencti.io/latest/usage/exploring-analysis/
- https://docs.opencti.io/latest/usage/exploring-cases/
- https://docs.opencti.io/latest/usage/containers/
- https://docs.opencti.io/latest/usage/case-management/
