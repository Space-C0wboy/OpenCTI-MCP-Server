# Confidence, Scoring, and Reliability

How much OpenCTI (and you) should trust a given piece of data — the confidence level on entities and relationships, the maliciousness score on indicators/observables, and the reliability rating of a source. These are three distinct axes: confidence is about the *information*, reliability is about the *source*, and score is about how *dangerous* an indicator/observable currently is.

## Confidence (0-100)

Confidence represents the credibility of a piece of information itself, independent of how reliable its source is — even a trusted source can pass along something wrong. OpenCTI fuses source reliability and information credibility into this single confidence metric so it's practical to use day to day. Confidence is a numerical value from 0 to 100 and applies broadly across the platform: analyses (reports, groupings, malware analyses, notes), cases (incident response, RFI, takedown, feedback), events (incidents, sightings, observed data), observations (indicators, infrastructure), threats (threat actors, intrusion sets, campaigns), and arsenal (malware, channels, tools, vulnerabilities) — as well as on relationships between objects.

Low confidence flags data that's uncertain — a lead worth tracking but not yet verified, a suspected (not confirmed) attribution, a pivot made on a hunch. High confidence signals well-corroborated, analyst-verified knowledge.

OpenCTI ships a few standard confidence-scale templates, customizable per entity type, that you can select or relabel with meaningful "ticks":
- **Admiralty Scale** — aligned with the NATO Admiralty code credibility ratings.
- **Objective Scale** — five levels: Cannot be judged, Told (reported without verification), Induced (analytical conclusion from assumed-true data), Deduced (logical conclusion from other assumed-true information), Witnessed (source directly observed it).
- **Standard** — the historic OpenCTI scale: simple Low / Medium / High buckets.

Confidence is also tied to access control: a user or group can be capped with a **max confidence level**, and when multiple levels apply the platform takes the conservative (lowest) one. A user cannot create, update, or delete an object whose confidence exceeds their own max confidence — administrators with the bypass capability effectively have max confidence 100.

## x_opencti_score

`x_opencti_score` is a maliciousness score (0-100) carried on indicators and observables (STIX Cyber Observables use `x_opencti_score` rather than `confidence` for this purpose). It reflects how dangerous the object currently looks, not how much you trust the record of it.

An indicator's score is set at creation — either provided by the data source or defaulting to 50 — and then decays over time according to a configured decay rule attached at creation. Score updates happen at each decay reaction point; the indicator's `valid_until` is computed from the decay rule's "revoke" threshold, and once the score reaches that threshold the indicator is automatically marked `revoked` with `detection` set to false.

## Reliability

Reliability measures trust in an information *source* based on its technical capabilities and track record, separate from confidence in any single piece of information it provides. It's assigned to Organizations, Individuals, Systems, and Reports (where it reflects the reliability of the report's original author). The default scale is the NATO Admiralty code, A-F:
- **A** — Completely reliable
- **B** — Usually reliable
- **C** — Fairly reliable
- **D** — Not usually reliable
- **E** — Unreliable
- **F** — Reliability cannot be judged

Reliability is an open vocabulary (`reliability_ov`), so it can be customized under Settings -> Taxonomies -> Vocabularies.

## Confidence and deduplication/merging

When OpenCTI deduplicates incoming data against an existing entity, the ability to update or enrich that entity is gated by confidence and quality level — the platform's stated intent is to converge the knowledge base toward the highest confidence and quality data over time. The docs don't spell out exact attribute-level precedence rules for conflicting values, only the general principle that a submission's confidence (and the acting user/group's max confidence) governs whether it's allowed to overwrite what's already there.

**In this MCP:** `confidence` (0-100) is an optional parameter on `indicators_create` and on `relationships_create`. Set it deliberately: use a low value (e.g. 20) when creating an unconfirmed `related-to` relationship from a pivot you haven't verified, and a higher value once corroborated. `x_opencti_score` is not currently exposed as a parameter on the observable/indicator create tools in this MCP.

## Source

> OpenCTI docs (latest), distilled 2026-07-10.

- https://docs.opencti.io/latest/usage/reliability-confidence/
- https://docs.opencti.io/latest/usage/indicators-lifecycle/
- https://docs.opencti.io/latest/usage/deduplication/
- https://docs.opencti.io/latest/reference/data-processing/
