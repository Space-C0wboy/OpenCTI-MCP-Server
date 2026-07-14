# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-07-14

### Changed

- Documentation only — no code or behavior changes: PyPI-first install instructions
  (`uv tool install` / `pip install` / `uvx`), a PyPI version badge, and editor-integration
  configs pointing at the published package. (Refreshes the README shown on PyPI.)

## [0.1.0] - 2026-07-14

Initial release.

### Added

- FastMCP + Python MCP server exposing **OpenCTI** to AI assistants via the official
  `pycti` client, plus a raw `graphql_query` escape-hatch for anything the typed tools
  don't cover.
- **15 entity domains** — indicators, observables, reports, malware, threat actors,
  intrusion sets, campaigns, attack patterns, tools, vulnerabilities, incidents, cases,
  relationships, identities, and labels/markings — with list/get/search reads and
  create/update/delete writes. **45 tools in read-only mode, 91 when writes are enabled.**
- **Read-only by default** (`OPENCTI_READ_ONLY`, default `true`): write tools are not
  registered and `graphql_query` rejects mutations until explicitly enabled.
- **Cross-cutting tools:** `search_all` (search across all STIX types),
  `relationships_for_entity` ("what is related to X"), `observables_by_value` (exact IOC
  lookup), and `order_by`/`descending` on every `*_list` for most-recent-first results.
- **Platform & operations:** `connectors_list`/`connectors_get` (ingestion health),
  `users_*`, `groups_*`, `files_for_entity`, and `entity_ask_enrichment`.
- **STIX bundles:** `stix_import_bundle` (bulk write) and `stix_export_entity` /
  `stix_export_list` (capped, with an oversize-note fallback).
- Marking/label support (`marking_ids`/`label_ids`) on create tools; `observables_create`
  accepts `StixFile.*` keys, coerces `Autonomous-System.number` to an integer, and supports
  multi-hash files via `additional_hashes`.
- Slimmed list outputs for readable results (full detail via `*_get` / `stix_export_entity`).
- **stdio and HTTP** transports; configuration via environment variables or a JSON-style /
  standard `.env` file.
- Bundled **`opencti-usage` Claude Skill** (`skills/opencti-usage/`) teaching an agent the
  OpenCTI model and mapping each concept to the right MCP tool.

[0.1.1]: https://github.com/Space-C0wboy/OpenCTI-MCP-Server/releases/tag/v0.1.1
[0.1.0]: https://github.com/Space-C0wboy/OpenCTI-MCP-Server/releases/tag/v0.1.0
