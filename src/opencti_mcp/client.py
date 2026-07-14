from __future__ import annotations

import re
from typing import Any

from pycti import OpenCTIApiClient

from .config import get_config

_client: OpenCTIApiClient | None = None
# Read-only guard for the raw graphql escape-hatch: matches a document whose first
# operation keyword is `mutation`. This is intentionally a first-token check, not a
# full parser — a multi-operation document is invalid GraphQL without an operationName
# (which the graphql_query tool does not expose), and a least-privilege API token is the
# primary write boundary. Do not rely on this as a complete mutation scanner.
_MUTATION_RE = re.compile(r"^\s*mutation\b", re.IGNORECASE)


def get_client() -> OpenCTIApiClient:
    global _client
    if _client is None:
        cfg = get_config()
        _client = OpenCTIApiClient(
            cfg.url,
            cfg.token,
            ssl_verify=cfg.ssl_verify,
            log_level=cfg.log_level.lower(),
            requests_timeout=cfg.timeout,
        )
    return _client


def reset_client_cache() -> None:
    global _client
    _client = None


def is_mutation_document(query: str) -> bool:
    return bool(_MUTATION_RE.match(query or ""))


def run_raw_query(query: str, variables: dict[str, Any] | None = None) -> Any:
    return get_client().query(query, variables or {})
