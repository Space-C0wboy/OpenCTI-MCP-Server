# Connectors: Ingestion, Enrichment, and Export

> OpenCTI docs (latest), distilled 2026-07-10.

Connectors are how data flows into and out of OpenCTI. They run as independent
processes (own API token, own user) that talk to the platform's API, typically over
RabbitMQ queues (an HTTP alternative also exists).

## Connector types

OpenCTI groups connectors into five types:

- **external-import** — automatically retrieves information from an external
  organization, application, or feed, converts it to STIX 2.1 bundles, and pushes it
  into OpenCTI. This is how threat-intel feeds (TAXII, RSS, CSV, JSON, MISP, etc.)
  become platform data.
- **internal-enrichment** — triggered on a specific object (created or requested by
  an analyst), it looks up/searches that object in an external source and generates
  a STIX bundle that enhances the existing knowledge (relationships, external
  references, or completed object fields).
- **internal-import-file** — parses an uploaded file (e.g. STIX JSON/XML via
  `ImportFileStix`, MISP JSON via `ImportFileMISP`, YARA rules via `ImportFileYARA`,
  or PDF/text/HTML/markdown via `ImportDocument`) and extracts entities into an
  analyst workbench for review before they're integrated into the platform. CSV
  files use a dedicated CSV mapper instead and import directly, skipping the
  workbench step.
- **internal-export-file** — extracts OpenCTI data into external formats (JSON,
  CSV, PDF, TXT, or STIX+JSON), either as a "simple" export (single entity) or
  "full" export (entity plus first-level associations). Exports can also be scoped
  by maximum marking level and carry their own file marking.
- **stream** — connects to a platform live stream and continuously acts on
  received events, typically pushing OpenCTI data out to SIEMs/XDRs/EDRs; some
  stream connectors are bidirectional and also import alerts/sightings back in.

Native feed formats (TAXII, TAXII push, RSS, CSV, JSON) are a special case of
**external-import**: OpenCTI ships standardized feed connectors so common
open-source/commercial feeds can be wired up without custom connector code.

Every connector runs as its own dedicated OpenCTI user with its own API token and
capabilities, so what a connector can read or write is bounded the same way a
human user's access is (see the RBAC reference).

## Enrichment in practice

An analyst can manually trigger enrichment from an entity's page (the cloud-icon
button opens a panel listing enrichment connectors compatible with that object
type — if none appear, none are configured for that type). Enrichment can also run
automatically: real-time (an `auto: true` connector setting fires as soon as
matching data arrives — best avoided for quota-limited paid connectors) or via
playbooks targeting specific objects. A user's own confidence level can limit
whether an enrichment connector is allowed to update existing platform data.

## Merging and deduplication

OpenCTI automatically merges data at creation time — whether created manually or
ingested from different sources — "if it meets certain conditions" (the platform's
deduplication logic; exact matching rules live in the administration merging docs).
In practice this means observables and indicators ingested repeatedly (e.g. the
same IP or hash seen by two feeds) converge on one object rather than duplicating.
Analysts can also manually merge same-type entities: one entity is chosen as the
anchor (keeping its name/description) and the others are folded in as aliases,
without losing any of their relationships.

## Health and state

Connector status is visible in the platform under Data > Ingestion > Connectors,
which shows each connector's RabbitMQ queue statistics — enough to tell whether a
connector is active and how large its backlog is.

**In this MCP:** check connector health/state with `connectors_list` /
`connectors_get`. Trigger enrichment on a specific entity with
`entity_ask_enrichment(entity_id, connector_id)`. Bulk-load a STIX bundle (the
same shape an external-import connector would produce) with `stix_import_bundle`.
Export data with `stix_export_entity` (single entity) or `stix_export_list`
(a filtered list, capped by `first`).

## Source

- https://docs.opencti.io/latest/deployment/connectors/
- https://docs.opencti.io/latest/usage/enrichment/
- https://docs.opencti.io/latest/usage/export/
- https://docs.opencti.io/latest/usage/import-files/
- https://docs.opencti.io/latest/usage/merging/
