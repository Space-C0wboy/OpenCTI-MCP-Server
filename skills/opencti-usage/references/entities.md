# OpenCTI Entity Types

A compact reference to the entity types this MCP exposes: what each represents and when to reach for it. For the underlying STIX object families (SDO/SCO/SRO/meta) and identifier scheme, see `data-model.md`. For how entities relate to each other, see the relationships reference.

## Observations

**Observables** (STIX Cyber Observables, SCOs) are immutable raw data points — IPv4/IPv6 addresses, domain names, email addresses, file hashes, URLs, and similar artifacts. They carry no detection intent by themselves and can represent perfectly legitimate resources; use them to catalog and track individual cyber artifacts you've seen (in your environment, in a report, etc.).
**In this MCP:** `observables_create`, `observables_get`, `observables_list`, `observables_update`, `observables_delete`, plus `observables_by_value` for lookup by raw value.

**Indicators** are detection objects: a search pattern (STIX, Sigma, YARA, etc.) with a validity window (`valid_from`/`valid_until`), a `revoked` flag, a `detection` flag, and optional kill-chain-phase references. Indicators are typically built on top of one or more observables — they wrap raw data in detection/operational logic so it can drive hunting or blocking. Use an Indicator when you want something actionable (a rule to search or alert on); use an Observable when you're just recording a raw artifact.
**In this MCP:** `indicators_create`, `indicators_get`, `indicators_list`, `indicators_update`, `indicators_delete`.

## Threats

**Threat actors** are the humans behind operations — individuals or groups (nation-state, state-sponsored, corporate, hacktivist, etc.). Individual threat actors carry demographic fields (residence, citizenship, etc.); group threat actors represent organized teams. Use them to track *who* is responsible.
**In this MCP:** `threat_actors_create`, `threat_actors_get`, `threat_actors_list`, `threat_actors_update`, `threat_actors_delete`.

**Intrusion sets** capture the consistent technical/operational signature behind attacks — a recurring set of TTPs, tools, malware, and infrastructure. Use them to track *how* attacks are carried out; a single threat actor may be linked to multiple intrusion sets over time.
**In this MCP:** `intrusion_sets_create`, `intrusion_sets_get`, `intrusion_sets_list`, `intrusion_sets_update`, `intrusion_sets_delete`.

**Campaigns** are discrete, time-bounded waves of malicious activity against a defined set of victims. Use them to scope a specific attack effort (a start/end window and victim set), typically attributed to an intrusion set.
**In this MCP:** `campaigns_create`, `campaigns_get`, `campaigns_list`, `campaigns_update`, `campaigns_delete`.

Rule of thumb: Threat actors = *who*, Intrusion sets = *how/what*, Campaigns = *when/where*.

## Arsenal

**Malware** is code designed to damage, disrupt, or gain unauthorized access — viruses, worms, trojans, ransomware, spyware. Use it to model and track malicious code employed by intrusion sets.
**In this MCP:** `malware_create`, `malware_get`, `malware_list`, `malware_update`, `malware_delete`.

**Tools** are legitimate, pre-installed software or hardware (command-line utilities, scripts, admin tools — e.g. LOLBAS) that attackers repurpose for malicious ends. Use them to track misuse of legitimate software rather than purpose-built malicious code.
**In this MCP:** `tools_create`, `tools_get`, `tools_list`, `tools_update`, `tools_delete`.

**Vulnerabilities** are weaknesses that can be exploited to compromise the confidentiality, integrity, or availability of a system. Use them to track and manage security flaws that need remediation, and to associate them with the intrusion sets, malware, or campaigns that exploit them.
**In this MCP:** `vulnerabilities_create`, `vulnerabilities_get`, `vulnerabilities_list`, `vulnerabilities_update`, `vulnerabilities_delete`.

## Techniques

**Attack patterns** describe the methods adversaries use to compromise targets (a type of TTP) — e.g. spear phishing. They generalize specific attacks into reusable patterns and help explain how an attack is performed, referencing frameworks like MITRE ATT&CK (cyber), CAPEC (cyber attacks), and DISARM (influence operations). Use them to map adversary tactics/techniques and link detections or mitigations to a known technique.
**In this MCP:** `attack_patterns_create`, `attack_patterns_get`, `attack_patterns_list`, `attack_patterns_update`, `attack_patterns_delete`.

## Entities (Identities)

Identities cover the people, organizations, and systems relevant to an investigation, in four subtypes:

- **Organizations** — companies, government bodies, associations, non-profits, and other groups with specific aims. Use for tracking targets, attackers' fronts, or partners in the threat landscape.
- **Individuals** — specific persons relevant to the analysis (targeted people, influential figures). Use for cyber-stalking, impersonation, or other person-targeted investigations.
- **Systems** — software applications, platforms, or frameworks (e.g. WordPress, VirtualBox, Firefox, Python). Use for vulnerability assessment, patch management, and tracking affected applications.
- **Sectors** — areas of economic activity (energy, government, health, finance, etc.). Use to categorize targeted industries for context, not as a target in itself.

**In this MCP:** all four subtypes go through `identities_create`, `identities_get`, `identities_list`, `identities_delete` (subtype is set via a type/class field on create).

## Events / Cases

**Incidents** represent a negative event on an information system — a cyberattack (intrusion, phishing, etc.), a qualified SIEM/EDR alert, or a larger compromise. Incidents are **containers**: they hold related entities, observables, analyses, and content documenting the event. Use them to record that something bad happened and to gather everything known about it.
**In this MCP:** `incidents_create`, `incidents_get`, `incidents_list`, `incidents_update`, `incidents_delete`.

**Cases** are containers for organizing a response or analytical effort, distinct from the incident itself. Three kinds:
- **Incident Response** — the context and actions taken in responding to a specific incident (not the incident itself).
- **Request for Information (RFI)** — analytical requests, e.g. "what do we know about threat X."
- **Request for Takedown (RFT)** — requests to remove attacker-controlled infrastructure (e.g. during a targeted campaign).

Like Reports, a Case is a container you can add any knowledge to (entities, observables, tasks). Use Cases to organize investigation/response work; use Incidents to record the event being responded to.
**In this MCP:** `cases_create`, `cases_get`, `cases_list`, `cases_update`, `cases_delete`.

## Analyses

**Reports** are intelligence containers: a set of attributes/metadata describing an external document — a vendor threat-intel report, blog post, press article, video, conference extract, MISP event, or similar — plus the knowledge (entities, observables, relationships) extracted from it. Reports are **containers**, and they anchor provenance: everything traced from a report can be traced back to its source. Use Reports when publishing or ingesting a finished, citable piece of intelligence (as opposed to Cases/Groupings, which track ongoing investigative work).
**In this MCP:** `reports_create`, `reports_get`, `reports_list`, `reports_update`, `reports_delete`.

## Source

> OpenCTI docs (latest), distilled 2026-07-10.

- https://docs.opencti.io/latest/usage/exploring-observations/
- https://docs.opencti.io/latest/usage/exploring-threats/
- https://docs.opencti.io/latest/usage/exploring-arsenal/
- https://docs.opencti.io/latest/usage/exploring-techniques/
- https://docs.opencti.io/latest/usage/exploring-entities/
- https://docs.opencti.io/latest/usage/exploring-events/
- https://docs.opencti.io/latest/usage/exploring-analysis/
- https://docs.opencti.io/latest/usage/exploring-cases/
