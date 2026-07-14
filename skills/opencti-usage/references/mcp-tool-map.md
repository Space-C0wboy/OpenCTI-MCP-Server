# MCP Tool Map

This maps common OpenCTI actions to the tools exposed by the `opencti` MCP server in this repo, plus the operational gotchas found by exercising them against a live instance. Tool names below are exactly what `register_all` registers — nothing is inferred or guessed.

## Part 1 — Action → tool

| Action | Tool(s) |
|---|---|
| Find an IOC by exact value | `observables_by_value` |
| List / most-recent N of a type | `<name>_list` with `order_by="created_at"`, `descending=true` |
| Search across all STIX types | `search_all` |
| Get one entity by id | `<name>_get` |
| What's related to an entity | `relationships_for_entity` |
| Create an indicator / observable / report / malware / etc. | `<name>_create` |
| Relate two entities | `relationships_create(from_id, to_id, relationship_type, confidence)` |
| Update one field / delete | `<name>_update` / `<name>_delete` |
| Export to STIX | `stix_export_entity`, `stix_export_list` |
| Bulk-load a STIX bundle | `stix_import_bundle` |
| Trigger enrichment | `entity_ask_enrichment(entity_id, connector_id)` |
| Connector health / ingestion | `connectors_list`, `connectors_get` |
| Users / groups (read) | `users_*`, `groups_*` |
| Identities (orgs/individuals/systems/sectors) | `identities_*` |
| Markings / labels | `markings_list`, `labels_*` |
| Anything untyped (status templates, connector control, `x_mitre_id` filter, create Identity via `identityAdd`) | `graphql_query` |

`<name>` covers: `attack_patterns`, `campaigns`, `cases`, `incidents`, `indicators`, `intrusion_sets`, `malware`, `observables`, `relationships`, `reports`, `threat_actors`, `tools`, `vulnerabilities`.

## Part 2 — Gotchas / rules (from live testing)

- **File-hash observables**: use key `File.hashes.SHA-256`; the tool also accepts `StixFile.*` and normalizes it to `File.*`. Multiple hashes: `additional_hashes=["SHA-1:…","MD5:…"]` (each entry must be `ALGO:VALUE` — malformed entries are rejected, not silently dropped).
- **Autonomous-System observables**: `Autonomous-System.number` (and any key ending in `.number`) values are integers — the tool coerces the string you pass into an `int`.
- **List params are arrays**: `marking_ids`, `label_ids`, `object_ids`, `report_types`/`malware_types`/`tool_types`/`threat_actor_types`, and `search_all`'s `types` are all ARRAYS, not scalars.
- **List tool outputs are slimmed**: heavy fields (report `content`, container `objects`, `config`, `connector_user`, `parent_types`, `spec_version`) are dropped, and nested refs (markings, labels, created-by) are trimmed to id/name/value. Use `<name>_get` or `stix_export_entity` for full detail. If a single entity is still too large, `_get` returns a slimmed view with a `_note` instead of erroring.
- **`stix_export_list` is capped** by `first` (default 25). If the export would still exceed the response size limit even at the requested `first`, the tool returns a `_note` (with `object_count`) instead of an oversized bundle — lower `first`, narrow `entity_type`, or export a single entity instead.
- **Read-only by default**: writes require `OPENCTI_READ_ONLY=false`. `graphql_query` rejects mutation documents while in read-only mode.
- **Markings/labels**: set via `marking_ids`/`label_ids` on create tools; find ids via `markings_list` / `labels_list`, or make a new label with `labels_create`.
- **`cases_create` does NOT take `object_ids`** (only `reports_create` does) — to attach objects to a case, use `graphql_query` instead.
- **`identities_*` has create/list/get/delete but no update tool**; markings are read-only end to end (no `markings_create`/`_update`/`_delete`).

## Source

> Reflects the opencti MCP server at 2026-07-10; see docs/ENDPOINTS.md for the full tool→pycti mapping.
