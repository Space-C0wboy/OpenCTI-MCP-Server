from __future__ import annotations

from fastmcp import FastMCP

from . import (
    attack_patterns,
    campaigns,
    cases,
    graphql,
    identities,
    incidents,
    indicators,
    intrusion_sets,
    labels_markings,
    malware,
    observables,
    platform,
    relationships,
    reports,
    search,
    stix_bundle,
    threat_actors,
    tools,
    vulnerabilities,
)

_DOMAIN_MODULES = [
    indicators,
    observables,
    reports,
    malware,
    threat_actors,
    intrusion_sets,
    campaigns,
    attack_patterns,
    tools,
    vulnerabilities,
    incidents,
    cases,
    relationships,
    labels_markings,
    identities,
]


def register_all(mcp: FastMCP, *, read_only: bool) -> None:
    for module in _DOMAIN_MODULES:
        module.register(mcp, read_only=read_only)
    graphql.register(mcp, read_only=read_only)
    search.register(mcp, read_only=read_only)
    platform.register(mcp, read_only=read_only)
    stix_bundle.register(mcp, read_only=read_only)
