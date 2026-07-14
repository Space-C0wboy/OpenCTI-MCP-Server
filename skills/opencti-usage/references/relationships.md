# Relationships and the Knowledge Graph

OpenCTI structures all data as a knowledge graph: STIX Domain Objects (SDOs) and STIX Cyber Observables (SCOs) are the nodes, and STIX Relationship Objects (SROs) are the edges connecting them. A relationship is not just a link — it is itself an object with its own type, direction, confidence, timestamps, and markings.

## Anatomy of a relationship

Every SRO connects exactly two entities and carries:

- **A relationship type** (e.g. `uses`, `indicates`, `targets`) that determines what the link means.
- **A direction** — a `from` entity (source) and a `to` entity (target). The entity you start the link from becomes `from`; the entity you link it to becomes `to`. Direction is not cosmetic: `A uses B` and `B uses A` are different claims, and OpenCTI's UI, filters, and inference rules all key off which side is `from` and which is `to`.
- **Confidence** (0–100) — how sure the *relationship itself* is, independent of the confidence on the two entities it connects.
- **Start time / stop time** — the window during which the relationship is asserted to hold (e.g. an actor used a tool between two dates).
- **Object markings** (e.g. TLP) controlling who can see the relationship.

Relationships are created either from an existing entity's page (the entity you start from is automatically `from`) or explicitly by ID, and the creation form mirrors an entity-creation form with these same fields.

## Common relationship types and their direction

The correct type — and its direction — depends on the pair of entity types being linked. Some of the most common:

| Type | From → To | Meaning |
|---|---|---|
| `indicates` | Indicator → Malware / Threat Actor / Intrusion Set / Tool / Campaign / Attack Pattern | This indicator is evidence of that entity's activity. |
| `uses` | Threat Actor / Intrusion Set / Campaign / Malware → Tool / Attack Pattern (technique) / Malware | The source employs the target as part of its tradecraft. |
| `targets` | Threat Actor / Intrusion Set / Campaign / Malware → Identity / Location / Sector / Vulnerability | The source victimizes or aims at the target. An Identity with `identity_class: sector` is how OpenCTI models "targets a sector." |
| `based-on` | Indicator → Observable | The indicator's detection logic (e.g. a STIX pattern) is derived from this observable. Created automatically when you "promote" an observable to an indicator. |
| `related-to` | any → any | A generic, non-committal link used when no more specific semantic applies. |
| `attributed-to` | Campaign / Intrusion Set → Threat Actor / Identity | Asserts who is believed to be behind the campaign or intrusion set. |
| `belongs-to` | Observable (e.g. IPv4-Addr) → Autonomous-System | The observable is hosted within/owned by that AS. |

These follow the STIX 2.1 relationship semantics that OpenCTI implements; when a type isn't in this table, check what pairs of entity types the UI offers for the two objects you're linking — OpenCTI only allows type/direction combinations that make sense for the selected entities.

## Confidence on relationships

Confidence is a 0–100 value (labeled with templates like Low/Medium/High, the Admiralty Code, or an "Objective" scale of Cannot-be-judged/Told/Induced/Deduced/Witnessed, depending on platform configuration) that expresses how credible a given piece of information is — separate from how reliable its source is. The same scale applies to relationships: confidence on a relationship states how sure you are that the link itself holds, not how sure you are about either endpoint.

In practice, set **LOW confidence** on a relationship when it represents an unconfirmed lead rather than a settled finding — e.g. a *suspected* attribution (`attributed-to`) before corroboration, or an infrastructure pivot (`related-to`, `uses`) based on a single weak indicator. Raise confidence as more sources corroborate the link. Platforms can also enforce a max confidence level per user/group, so only sufficiently trusted users or connectors can create or edit high-confidence relationships.

## Inference and reasoning (rule engine)

OpenCTI can automatically derive new relationships from existing ones by activating predefined inference rules (roughly twenty are available, configured under Settings > Customization > Rules engine, restricted to administrators). Once a rule is active, it runs continuously: any time a relationship is created or modified that satisfies the rule's condition, the corresponding inferred relationship is generated in real time.

Two representative rules:

- **Usage propagation of parent techniques**: if `A uses B` and `B` is a sub-technique of `C`, OpenCTI infers `A uses C`.
- **Targeting propagation via belonging / attribution**: if an entity targets an Identity/Location that belongs to (or is attributed to) a broader Identity/Location, OpenCTI infers the entity also targets the broader one.

Inferred relationships are created under the platform's Rule Manager (system) user, which defaults to confidence 100 — so inferred links generally show up as high-confidence. They are visually distinguished from manually created relationships: dotted, differently-colored lines in Graph view, and a magic-wand icon at the end of the row in list views.

**In this MCP:** `relationships_create(from_id, to_id, relationship_type, confidence)` creates an SRO — get the `from`/`to` direction right per the table above. `relationships_for_entity(entity_id)` lists every relationship touching an entity (as either source or target), which is the quickest way to see what's already connected before adding more links.

## Source

> OpenCTI docs (latest), distilled 2026-07-10.

- https://docs.opencti.io/latest/usage/data-model/
- https://docs.opencti.io/latest/usage/manual-creation/
- https://docs.opencti.io/latest/usage/reliability-confidence/
- https://docs.opencti.io/latest/usage/inferences/
- https://docs.opencti.io/latest/administration/reasoning/
