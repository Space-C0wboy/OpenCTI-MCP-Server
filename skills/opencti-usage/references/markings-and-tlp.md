# Markings and TLP

> OpenCTI docs (latest), distilled 2026-07-10.

Marking definitions are OpenCTI's data-classification labels. They establish a
standardized framework for classifying data and drive **data segregation**: only users
authorized for a given marking can see the objects it's attached to. This file covers
markings and TLP specifically — for users/groups/roles/capabilities (the RBAC side of
segregation), see `rbac-and-orgs.md`.

## What a marking definition is

Every marking definition has four attributes:

- **Type** — the marking group/category (e.g. `TLP`, `PAP`, or a custom statement type).
- **Definition** — the assigned name (e.g. `TLP:AMBER`).
- **Color** — a visual indicator used in the UI.
- **Order** — a hierarchical rank within its type, used to compare markings of the same
  type (higher order = more restrictive/sensitive).

## TLP (Traffic Light Protocol)

TLP is implemented by default in OpenCTI. The supported levels, from least to most
restrictive, are:

- **TLP:CLEAR**
- **TLP:GREEN**
- **TLP:AMBER**
- **TLP:AMBER+STRICT**
- **TLP:RED**

TLP marks how widely intelligence may be shared/disseminated.

## PAP (Permissible Actions Protocol)

PAP markings (e.g. `PAP:AMBER`, `PAP:RED`) indicate what actions a recipient is
permitted to take on the data (e.g. whether it can be used for active defensive measures
against the source), distinct from TLP's sharing scope.

## Statement / custom markings

Beyond TLP and PAP, OpenCTI supports custom "statement" marking definitions — e.g. a
license/attribution statement like `CC-BY-SA-4.0 DISARM Foundation`. These work the same
way as TLP/PAP for access control: type + definition + order.

## How markings drive segregation (the access rule)

A user can see an object only if, for **every** marking attached to that object, the
user belongs to a group that either:

1. Has been granted access to that exact marking, **or**
2. Has access to a marking of the **same type** with an **equal or higher** hierarchical
   order.

Access to *all* markings on an object is required — not just one. If an object carries
both `TLP:AMBER` and a custom statement marking, a user needs sufficient access to both
types to view it.

When multiple markings of the same type but different orders are added to an object,
the platform keeps only the marking with the **highest order** for that type (it doesn't
retain a redundant lower-order marking of the same type).

## Best practice

Mark incident-derived intelligence appropriately for how sensitive/shareable it is —
for example, use `TLP:AMBER` (or stricter) for data tied to a specific customer or
victim organization, since that limits redistribution to only groups explicitly
authorized. The allowed markings on the calling user/token bound what data is visible
through the API/MCP just as they would in the UI: an object outside those markings
simply won't appear in results.

**In this MCP:** pass `marking_ids=[<marking id>]` on create tools (e.g.
`indicators_create`, `observables_create`, `reports_create`) to attach markings to a new
object. Find marking definition ids with `markings_list` (filter/scan for the one you
want, e.g. `TLP:AMBER`) or look one up by id with `markings_get`. There is no
`markings_create` tool in this MCP — marking definitions are platform-level objects
managed in OpenCTI itself, not created through this server. Labels are a separate,
unrelated tagging concept (`labels_list`, `labels_create`, and `label_ids` on create
tools) — don't conflate labels with markings.

## Source

- https://docs.opencti.io/latest/administration/ontologies/
- https://docs.opencti.io/latest/administration/segregation/
