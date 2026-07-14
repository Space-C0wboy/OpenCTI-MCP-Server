# OpenCTI MCP Server

[![PyPI](https://img.shields.io/pypi/v/opencti-mcp.svg)](https://pypi.org/project/opencti-mcp/)
[![Python versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-server-purple.svg)](https://modelcontextprotocol.io)
[![CI](https://github.com/Space-C0wboy/OpenCTI-MCP-Server/actions/workflows/ci.yml/badge.svg)](https://github.com/Space-C0wboy/OpenCTI-MCP-Server/actions/workflows/ci.yml)

A [Model Context Protocol](https://modelcontextprotocol.io) server that exposes **OpenCTI**, the open-source threat-intelligence platform, to AI assistants. Built on the official `pycti` client, it registers 45 typed tools (91 when writes are enabled) across 15 threat-intel domains — indicators, observables, reports, malware, threat actors, intrusion sets, campaigns, attack patterns, tools, vulnerabilities, incidents, cases, relationships, identities, and labels/markings — plus platform/operations tools (connectors, users, groups, files), STIX bundle import/export, a `graphql_query` escape-hatch, and cross-cutting search/relationship/observable-lookup tools for anything the typed per-domain tools don't cover.

> [!IMPORTANT]
> This is an unofficial, community-maintained project. It is not affiliated with, endorsed by, or supported by Filigran or the OpenCTI project.

> [!WARNING]
> **Ships read-only by default.** With the default configuration, only list/get/query tools are registered and `graphql_query` rejects mutations. Setting `OPENCTI_READ_ONLY=false` exposes `*_create`, `*_update`, and the destructive `*_delete` tools, and lets `graphql_query` run mutations. Only enable writes with a least-privilege OpenCTI API token, and understand that an assistant with write access can create, modify, and permanently delete intelligence data in your instance.

## Tools

| Domain | Reads | Writes | Notable tools |
| --- | :---: | :---: | --- |
| Indicators | 2 | 3 | `indicators_list`, `indicators_get`, `indicators_create` |
| Observables | 2 | 3 | `observables_list`, `observables_get`, `observables_create` |
| Reports | 2 | 3 | `reports_list`, `reports_get`, `reports_create` |
| Malware | 2 | 3 | `malware_list`, `malware_get`, `malware_create` |
| Threat actors | 2 | 3 | `threat_actors_list`, `threat_actors_get`, `threat_actors_create` |
| Intrusion sets | 2 | 3 | `intrusion_sets_list`, `intrusion_sets_get`, `intrusion_sets_create` |
| Campaigns | 2 | 3 | `campaigns_list`, `campaigns_get`, `campaigns_create` |
| Attack patterns | 2 | 3 | `attack_patterns_list`, `attack_patterns_get`, `attack_patterns_create` |
| Tools | 2 | 3 | `tools_list`, `tools_get`, `tools_create` |
| Vulnerabilities | 2 | 3 | `vulnerabilities_list`, `vulnerabilities_get`, `vulnerabilities_create` |
| Incidents | 2 | 3 | `incidents_list`, `incidents_get`, `incidents_create` |
| Cases | 2 | 3 | `cases_list`, `cases_get`, `cases_create` |
| Relationships | 2 | 3 | `relationships_list`, `relationships_get`, `relationships_create` |
| Identities | 2 | 2 | `identities_list`, `identities_get`, `identities_create` (organizations/individuals/systems/sectors), `identities_delete` |
| Labels & markings | 4 | 3 | `labels_list`, `labels_create`, `markings_list`, `markings_get` |

Every domain also has an `_update` and `_delete` tool once writes are enabled (markings are read-only; identities has `_create`/`_delete` but no `_update`). In addition, `graphql_query` runs a raw GraphQL query/mutation against the OpenCTI API for anything not covered by a typed tool above — reads always work, mutations are rejected unless `OPENCTI_READ_ONLY=false`. See [`docs/ENDPOINTS.md`](docs/ENDPOINTS.md) for the full tool-to-`pycti`-call mapping.

Every `*_list` tool also accepts `order_by` (a field name, e.g. `"created_at"`) and `descending` (default `true`), so `order_by="created_at"` gives most-recent-first without any extra filtering.

`observables_create` also accepts `StixFile.*` observable keys (normalized to `File.*`), coerces `Autonomous-System.number` values to an integer, and takes an optional `additional_hashes` param (a list of `"ALGO:VALUE"` entries, e.g. `"SHA-1:..."`) to attach extra hashes to a file observable alongside the primary one.

### Cross-cutting read tools

- `search_all(query, types?, first?)` — full-text search across all STIX object types at once, optionally restricted to specific `types`.
- `relationships_for_entity(entity_id, relationship_type?, first?)` — lists relationships touching an entity as either source or target, e.g. "what is related to X".
- `observables_by_value(value, first?)` — exact-value lookup for an observable (IP, domain, URL, hash, etc.) without knowing its id.

### Platform & operations

- `connectors_list` / `connectors_get(connector_id)` — list connectors and check one's status/health (active, state, queue details).
- `users_list` / `users_get(id)` — list/get OpenCTI users.
- `groups_list` / `groups_get(id)` — list/get OpenCTI groups.
- `files_for_entity(entity_id)` — list files/attachments on an entity.
- `stix_export_entity(entity_type, entity_id, mode?)` / `stix_export_list(entity_type, first=25, mode?)` — export a single entity, or up to `first` entities of a type (max 500), as a STIX 2 bundle; large exports are capped by `first`, and if the bundle is still too large a small note (`_note`, `entity_type`, `first`, `object_count`) is returned instead.
- `stix_import_bundle(bundle_json, update?)` — **write, requires `OPENCTI_READ_ONLY=false`** — bulk create/update entities and relationships from a STIX bundle.
- `entity_ask_enrichment(entity_id, connector_id)` — **write, requires `OPENCTI_READ_ONLY=false`** — trigger a connector to enrich an entity.

Two related capabilities are intentionally not exposed as typed tools and remain available via `graphql_query`: OpenCTI status templates, and connector start/stop/reset (`pycti` exposes no dedicated method for either).

## Bundled skill

A **Claude Skill** lives at [`skills/opencti-usage/`](skills/opencti-usage/) that teaches an AI agent OpenCTI's model — the STIX data model, entity types, indicators vs observables, relationships, containers, TLP markings, confidence, connectors, and RBAC — and maps each concept to the right MCP tool above. An agent operating the `opencti` tools loads this skill to understand the platform before creating, relating, or reasoning about OpenCTI data.

- [`skills/opencti-usage/SKILL.md`](skills/opencti-usage/SKILL.md) is the entry point; the `references/` folder holds the per-topic detail.
- The content is distilled from the official OpenCTI docs (`docs.opencti.io/latest`), distilled 2026-07-10. Each reference file has a `## Source` link back to the docs it was drawn from, so it can be refreshed later.

## Quick start

### Install

From PyPI (recommended):

```bash
uv tool install opencti-mcp        # installs the `opencti-mcp` command
```

Or with `pip`, or run it without installing:

```bash
pip install opencti-mcp
uvx --from opencti-mcp opencti-mcp --help   # run ad hoc, no install
```

From source (for development):

```bash
git clone https://github.com/Space-C0wboy/OpenCTI-MCP-Server.git
cd OpenCTI-MCP-Server
uv venv
uv pip install -e ".[dev]"
```

### Get an API token

In OpenCTI, open your profile menu → **API access**, then copy your personal access token.

### Configuration

Configuration is read from environment variables, or from a `.env` file in the working directory (either a standard `KEY=value` dotenv file or a JSON-style fragment). OS environment variables always take precedence over the file.

| Variable | Required | Default | Description |
| --- | :---: | --- | --- |
| `OPENCTI_URL` | Yes | — | Base URL of your OpenCTI instance |
| `OPENCTI_TOKEN` | Yes | — | OpenCTI API token |
| `OPENCTI_READ_ONLY` | No | `true` | When `true`, hides all write tools and blocks mutations |
| `OPENCTI_TIMEOUT` | No | `30` | Request timeout in seconds |
| `OPENCTI_SSL_VERIFY` | No | `true` | Verify TLS certificates |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |
| `MCP_HTTP_HOST` | No | `127.0.0.1` | Bind host when using `--transport http` |
| `MCP_HTTP_PORT` | No | `8765` | Bind port when using `--transport http` |

### Run

Stdio (default, for editor/IDE integrations):

```bash
opencti-mcp                 # if installed via `uv tool install` / `pip`
# from source: uv run opencti-mcp
```

HTTP transport:

```bash
opencti-mcp --transport http --host 127.0.0.1 --port 8765
```

## Read-only mode

`OPENCTI_READ_ONLY` defaults to `true`. In read-only mode, only list/get tools and `markings_list`/`markings_get` are registered — no `*_create`, `*_update`, or `*_delete` tool is available for any domain, and `graphql_query` raises an error if the query document contains a `mutation`. Set `OPENCTI_READ_ONLY=false` to register the write tools and allow `graphql_query` to run mutations.

## Editor integration

### Claude Desktop

Add to `claude_desktop_config.json` (uses `uvx`, no install or local path needed):

```json
{
  "mcpServers": {
    "opencti": {
      "command": "uvx",
      "args": ["--from", "opencti-mcp", "opencti-mcp"],
      "env": {
        "OPENCTI_URL": "https://your-opencti-instance.example.com/",
        "OPENCTI_TOKEN": "your-api-token"
      }
    }
  }
}
```

If you installed it (`uv tool install opencti-mcp` / `pip install opencti-mcp`), use `"command": "opencti-mcp"` with `"args": []` instead. To run from a source checkout, use `"command": "uv"`, `"args": ["--directory", "/absolute/path/to/OpenCTI-MCP-Server", "run", "opencti-mcp"]`.

### Claude Code

```bash
claude mcp add opencti -- uvx --from opencti-mcp opencti-mcp
```

## Example prompts

- "List the 10 most recent indicators."
- "Search reports mentioning 'Emotet'."
- "Show me the MITRE ATT&CK technique T1059."
- "Create an IPv4 observable for 1.2.3.4." (requires `OPENCTI_READ_ONLY=false`)
- "Which threat actors are linked to intrusion set APT29?"
- "Get the full detail on case CASE-ID, including its labels and markings."
- "What are the 10 most recent reports?"
- "Is 1.2.3.4 in OpenCTI?"
- "What is this threat actor related to?"
- "Search across everything for 'Emotet'."
- "Are our OpenCTI connectors healthy?"
- "Export this report as a STIX bundle."
- "List the groups in OpenCTI."
- "Add the victim organization 'Acme Corp' to OpenCTI." (requires `OPENCTI_READ_ONLY=false`)
- "Create an individual identity for John Doe with a description."

## Development

```bash
uv run pytest
uv run ruff check .
```

## License

MIT — see [LICENSE](LICENSE).

## Support

This is a community-maintained project provided as-is, with no guaranteed support SLA. Issues and pull requests are welcome.
