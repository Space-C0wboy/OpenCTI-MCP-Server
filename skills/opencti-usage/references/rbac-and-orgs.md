# RBAC & Organizations

> OpenCTI docs (latest), distilled 2026-07-10.

How OpenCTI decides what a given user can see and do: **Users** belong to **Groups**,
groups grant **Roles**, roles carry **Capabilities**. **Organizations** add a second,
orthogonal layer of segregation on top of markings. This file does not cover marking
mechanics themselves — see `markings-and-tlp.md` for TLP/PAP and how marking access
gates visibility.

## Users, Groups, Roles, Capabilities

- **User** — a platform account (human or service account) that authenticates and acts
  through the API/UI.
- **Group** — "the main way to manage permissions and data segregation" and platform
  customization. A group bundles:
  - one or more assigned **Roles** (which supply capabilities),
  - a default dashboard,
  - **allowed marking definitions** (which markings its members can see/apply) and a
    **default marking** applied to new entities members create,
  - a **max confidence level** — the ceiling on the `confidence` a member's created/edited
    data can carry.
  A user can belong to multiple groups; where values differ (e.g. confidence, markings),
  the **highest** value across the user's groups applies.
- **Role** — a named collection of **Capabilities** assigned to a group (indirectly to its
  users).
- **Capability** — an individual permission, e.g. access/create-update/delete/merge
  knowledge, access dashboards, access investigations, access data sharing, access/manage
  ingestion, access administration parameters, manage credentials/authentication, access
  connectors, manage connector state, use the connectors API, API usage with
  authorization headers, allow token/basic-auth usage, use Playbooks, access PIR, and the
  catch-all **"Bypass all capabilities."**

A user without a **max confidence level** cannot create, delete, or update any data —
confidence is a hard gate on write access, not just a data-quality field.

Two illustrative capabilities worth knowing by name:

- **"Bypass all capabilities"** — a superuser-style capability that skips the rest of the
  RBAC check entirely; typically reserved for platform administrators.
- **"Allow modification of sensitive configuration"** — gates changes to
  security-sensitive platform settings, separate from ordinary knowledge capabilities.

Where a user belongs to multiple groups with different marking access or confidence
ceilings, the platform applies the **highest** value found across those groups (see
"Groups" above) — membership in an additional group does not restrict access already
granted by another.

**In this MCP:** inspect this structure read-only with `users_list` / `users_get` and
`groups_list` / `groups_get`. If a create/update/delete tool call fails or an entity is
missing for a given API token, check whether the token's user has the max confidence
level and capabilities the action requires, and whether the markings on the target data
are among the user's groups' allowed markings.

## Organizations

**Organizations** are a second segregation axis, independent of markings and groups.
Platform admins can promote a member to **Organization administrator**, letting them
create/edit/delete users within their own organization and grant a pre-approved set of
groups to new members — without needing full platform-admin rights.

Full **organization-level data segregation** (compartmentalizing knowledge so members of
one organization cannot see another's, with an access-request workflow for restricted
resources) is an **OpenCTI Enterprise Edition** feature layered on top of the base
organization model.

**Service accounts** (technical/API users with no password, used by connectors and
integrations) are always additionally treated as members of the **platform organization**
— the platform's primary organization — regardless of any other organization they belong
to, so they retain the access they need even if organization assignments change.

**In this MCP:** organizations are represented as STIX **Identity** objects with
`identity_class` `organization` (see `entities.md`), not as a distinct RBAC tool family.
Create one with `identities_create` (`identity_class="organization"`); there is no
dedicated `organizations_*` tool set. Membership of a *user* in an organization (the RBAC
concept above) is a platform-administration setting, not something this MCP's tools
manage — `users_get` surfaces it for reading, but there is no user/org-membership write
tool here.

### User-to-user visibility

Separately from knowledge (entities/relationships) visibility, OpenCTI also restricts
which **other users** a given user can see in `users_list`/`users_get`-style reads. A user
can see another user when any of the following holds: organization sharing is disabled
platform-wide; the acting user has a capability such as bypass-all, user management,
Playbooks, or customization; or the policy "allow users to view users of other
organizations" is enabled. Otherwise visibility is limited to: users who belong to no
organization, co-members of an organization the acting user shares, service accounts, and
internal system users. If `users_list` returns fewer users than expected, this — not a
bug — is usually why.

## Connectors as users

Every connector authenticates as its own **user** with its own token and capability set
(typically connector-relevant capabilities like access/manage connectors and knowledge
create/update, scoped to what that connector needs to do). This is why connector-created
data has its own author/creator identity in the knowledge graph, distinct from the human
analysts using the platform.

**In this MCP:** `connectors_list` / `connectors_get` show connector health and identity,
but the connector's own user/role/capability configuration is managed in the platform UI,
not exposed as an MCP tool.

## Putting it together for reasoning about visibility

If a read comes back empty or a write is rejected, the two things to check are:

1. **Markings** — does the acting user's group grant access to every marking on the
   object? (All markings must be satisfied, not just one — see `markings-and-tlp.md`.)
2. **Organization** — if Enterprise Edition organization segregation is enabled, is the
   object restricted to an organization the acting user isn't a member of?

Confidence (max confidence level on the user's groups) governs whether a **write** is
possible at all, separate from either of the above.

## Source

- https://docs.opencti.io/latest/administration/users/
- https://docs.opencti.io/latest/administration/organization-segregation/
- https://docs.opencti.io/latest/administration/segregation/
