# Endpoint Catalog

Every tool registered by `opencti_mcp.tools.register_all`, mapped to the underlying `pycti` client call it wraps. "Mode" is `read` for tools always available, `write` for tools only registered when `OPENCTI_READ_ONLY=false`, and `read/write` for `graphql_query`, which is always registered but gates mutations on the read-only flag.

Read-only mode registers 45 tools. Enabling writes (`OPENCTI_READ_ONLY=false`) registers 91 tools total (the 45 reads plus 46 write tools).

Every `*_list` tool also accepts `order_by`/`descending`, which map to the `orderBy`/`orderMode` (`"asc"`/`"desc"`) arguments on the underlying `pycti` `.list()` call.

## Indicators

| Tool | pycti call | Mode |
| --- | --- | --- |
| `indicators_list` | `indicator.list` | read |
| `indicators_get` | `indicator.read` | read |
| `indicators_create` | `indicator.create` | write |
| `indicators_update` | `indicator.update_field` | write |
| `indicators_delete` | `indicator.delete` | write |

## Observables

| Tool | pycti call | Mode |
| --- | --- | --- |
| `observables_list` | `stix_cyber_observable.list` | read |
| `observables_get` | `stix_cyber_observable.read` | read |
| `observables_by_value` | `stix_cyber_observable.list` (filtered by `value`) | read |
| `observables_create` | `stix_cyber_observable.create` | write |
| `observables_update` | `stix_cyber_observable.update_field` | write |
| `observables_delete` | `stix_cyber_observable.delete` | write |

Note: `observables_create` accepts `StixFile.*` observable keys and normalizes them to `File.*`; values for keys ending in `.number` (e.g. `Autonomous-System.number`) are coerced to integers; and the optional `additional_hashes` param (a list of `"ALGO:VALUE"` strings, e.g. `"SHA-1:..."`, `"MD5:..."`) attaches extra hashes to a `File` observable alongside the primary hash.

## Reports

| Tool | pycti call | Mode |
| --- | --- | --- |
| `reports_list` | `report.list` | read |
| `reports_get` | `report.read` | read |
| `reports_create` | `report.create` | write |
| `reports_update` | `report.update_field` | write |
| `reports_delete` | `report.delete` | write |

## Malware

| Tool | pycti call | Mode |
| --- | --- | --- |
| `malware_list` | `malware.list` | read |
| `malware_get` | `malware.read` | read |
| `malware_create` | `malware.create` | write |
| `malware_update` | `malware.update_field` | write |
| `malware_delete` | `malware.delete` | write |

## Threat Actors

| Tool | pycti call | Mode |
| --- | --- | --- |
| `threat_actors_list` | `threat_actor_group.list` | read |
| `threat_actors_get` | `threat_actor_group.read` | read |
| `threat_actors_create` | `threat_actor_group.create` | write |
| `threat_actors_update` | `threat_actor_group.update_field` | write |
| `threat_actors_delete` | `threat_actor_group.delete` | write |

## Intrusion Sets

| Tool | pycti call | Mode |
| --- | --- | --- |
| `intrusion_sets_list` | `intrusion_set.list` | read |
| `intrusion_sets_get` | `intrusion_set.read` | read |
| `intrusion_sets_create` | `intrusion_set.create` | write |
| `intrusion_sets_update` | `intrusion_set.update_field` | write |
| `intrusion_sets_delete` | `intrusion_set.delete` | write |

## Campaigns

| Tool | pycti call | Mode |
| --- | --- | --- |
| `campaigns_list` | `campaign.list` | read |
| `campaigns_get` | `campaign.read` | read |
| `campaigns_create` | `campaign.create` | write |
| `campaigns_update` | `campaign.update_field` | write |
| `campaigns_delete` | `campaign.delete` | write |

## Attack Patterns

| Tool | pycti call | Mode |
| --- | --- | --- |
| `attack_patterns_list` | `attack_pattern.list` | read |
| `attack_patterns_get` | `attack_pattern.read` | read |
| `attack_patterns_create` | `attack_pattern.create` | write |
| `attack_patterns_update` | `attack_pattern.update_field` | write |
| `attack_patterns_delete` | `attack_pattern.delete` | write |

## Tools (software)

| Tool | pycti call | Mode |
| --- | --- | --- |
| `tools_list` | `tool.list` | read |
| `tools_get` | `tool.read` | read |
| `tools_create` | `tool.create` | write |
| `tools_update` | `tool.update_field` | write |
| `tools_delete` | `tool.delete` | write |

## Vulnerabilities

| Tool | pycti call | Mode |
| --- | --- | --- |
| `vulnerabilities_list` | `vulnerability.list` | read |
| `vulnerabilities_get` | `vulnerability.read` | read |
| `vulnerabilities_create` | `vulnerability.create` | write |
| `vulnerabilities_update` | `vulnerability.update_field` | write |
| `vulnerabilities_delete` | `vulnerability.delete` | write |

## Incidents

| Tool | pycti call | Mode |
| --- | --- | --- |
| `incidents_list` | `incident.list` | read |
| `incidents_get` | `incident.read` | read |
| `incidents_create` | `incident.create` | write |
| `incidents_update` | `incident.update_field` | write |
| `incidents_delete` | `incident.delete` | write |

## Cases

| Tool | pycti call | Mode |
| --- | --- | --- |
| `cases_list` | `case_incident.list` | read |
| `cases_get` | `case_incident.read` | read |
| `cases_create` | `case_incident.create` | write |
| `cases_update` | `case_incident.update_field` | write |
| `cases_delete` | `case_incident.delete` | write |

## Relationships

| Tool | pycti call | Mode |
| --- | --- | --- |
| `relationships_list` | `stix_core_relationship.list` | read |
| `relationships_get` | `stix_core_relationship.read` | read |
| `relationships_for_entity` | `stix_core_relationship.list` (filtered by `fromOrToId`) | read |
| `relationships_create` | `stix_core_relationship.create` | write |
| `relationships_update` | `stix_core_relationship.update_field` | write |
| `relationships_delete` | `stix_core_relationship.delete` | write |

## Identities

| Tool | pycti call | Mode |
| --- | --- | --- |
| `identities_list` | `identity.list` | read |
| `identities_get` | `identity.read` | read |
| `identities_create` | `identity.create` | write |
| `identities_delete` | `identity.delete` | write |

Note: identities has no `_update` tool.

## Labels & Markings

| Tool | pycti call | Mode |
| --- | --- | --- |
| `labels_list` | `label.list` | read |
| `labels_get` | `label.read` | read |
| `labels_create` | `label.create` | write |
| `labels_update` | `label.update_field` | write |
| `labels_delete` | `label.delete` | write |
| `markings_list` | `marking_definition.list` | read |
| `markings_get` | `marking_definition.read` | read |

## Cross-Type Search

| Tool | pycti call | Mode |
| --- | --- | --- |
| `search_all` | `stix_core_object.list` (full-text search across all STIX types, optionally filtered by `types`) | read |

## Platform & Operations

| Tool | pycti call | Mode |
| --- | --- | --- |
| `connectors_list` | `connector.list` | read |
| `connectors_get` | `connector.read` | read |
| `users_list` | `user.list` | read |
| `users_get` | `user.read` | read |
| `groups_list` | `group.list` | read |
| `groups_get` | `group.read` | read |
| `files_for_entity` | `stix_core_object.list_files` | read |
| `entity_ask_enrichment` | `stix_core_object.ask_enrichment` | write |

Note: OpenCTI status templates and connector start/stop/reset are not exposed as typed tools — `pycti` has no dedicated method for either, so use `graphql_query` if you need them.

## STIX Bundles

| Tool | pycti call | Mode |
| --- | --- | --- |
| `stix_export_entity` | `stix2.get_stix_bundle_or_object_from_entity_id` | read |
| `stix_export_list` | `stix_core_object.list` + `stix2.export_selected` | read |
| `stix_import_bundle` | `stix2.import_bundle_from_json` | write |

Note: `stix_export_list(entity_type, first=25, mode?)` bundles up to `first` entities (max 500). If the resulting bundle still exceeds the response size limit, it returns a small note (`_note`, `entity_type`, `first`, `object_count`) instead of the oversized bundle.

## Raw GraphQL

| Tool | pycti call | Mode |
| --- | --- | --- |
| `graphql_query` | `client.query` | read/write, mutation-gated by `OPENCTI_READ_ONLY` |
