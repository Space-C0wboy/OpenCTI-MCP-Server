# OpenCTI API and GraphQL

OpenCTI exposes a single **GraphQL** API — there is no separate REST surface for platform data. Everything the web UI can do (browse, search, create, edit, delete, manage connectors, manage users/roles) is achievable through this same API, because the UI itself is just another GraphQL client.

## Endpoint and authentication

- The API (and its interactive GraphQL Playground) is served from the platform at `/graphql`, e.g. `https://<your-instance>/graphql`.
- Authentication is a **Bearer token** (an OpenCTI user's API key) sent as a standard HTTP header:

```
Content-Type: application/json
Authorization: Bearer <API key>
```

- Access is scoped by the calling user: whatever that user's roles/groups/marking access allow in the UI is exactly what the API key can read or write. There is no separate API-level permission model.

## The FilterGroup shape

List and search queries (and equivalent typed tools) take a `filters` argument shaped as a **FilterGroup** — a recursive structure of filters combined with a boolean mode, which can itself nest child `filterGroups` for AND/OR trees. Verified example from this repo's usage:

```json
{"mode": "and", "filters": [{"key": "value", "values": ["1.2.3.4"], "operator": "eq"}], "filterGroups": []}
```

- `mode` — `"and"` or `"or"`; how the entries in `filters` (and any nested `filterGroups`) combine.
- `filters` — a list of individual filter clauses, each with:
  - `key` — the field to filter on, e.g. `value` (an observable's raw value), `x_mitre_id` (an attack-pattern's MITRE ATT&CK ID), `created_at`.
  - `values` — an array of values to match against `key`.
  - `operator` — the comparison, e.g. `eq` (equals). Other operators exist (e.g. negation, ranges) but `eq` is the common case.
- `filterGroups` — nested FilterGroups for building more complex AND/OR trees; empty when not needed.

## Mutations

Edits and deletes on STIX objects go through generic, type-family mutations rather than one bespoke mutation per entity type — for example `stixDomainObjectEdit(id: "...") { delete }` deletes (and the same generic edit mutation handles field updates) for any STIX Domain Object, regardless of its specific type (Malware, Threat-Actor, Report, etc.). Equivalent generic mutations exist for observables and relationships.

The platform caps some batched calls: only **one** `stixDomainObjectEdit`-style mutation is accepted per mutation document. If you need to edit or delete several objects, submit them as separate GraphQL mutation documents/requests rather than aliasing multiple calls into one document.

## In this MCP

`graphql_query(query, variables)` is the escape-hatch for anything the typed tools don't cover — for example, working with status templates, controlling connectors, filtering attack-patterns by `x_mitre_id`, or creating an identity via `identityAdd` with `type: Organization`. It builds on the same client the typed tools use, and it **rejects mutations** when the server is running in read-only mode (`OPENCTI_READ_ONLY=true`), just like every mutating typed tool.

## Source

> OpenCTI docs (latest), distilled 2026-07-10.

- https://docs.opencti.io/latest/development/api-usage/
- https://docs.opencti.io/latest/reference/api/
