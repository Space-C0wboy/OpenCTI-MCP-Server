from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values

from .errors import ConfigError

_TRUTHY = {"1", "true", "yes", "on"}
_DEFAULT_ENV_PATH = Path(".env")

_cache: "Config | None" = None


@dataclass(frozen=True)
class Config:
    url: str
    token: str
    read_only: bool
    timeout: int
    ssl_verify: bool
    log_level: str
    http_host: str
    http_port: int


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    # Try JSON-fragment style: "KEY": "value", ...
    try:
        body = text.strip()
        if body.endswith(","):
            body = body[:-1]
        wrapped = "{" + body + "}"
        data = json.loads(wrapped)
        return {str(k): str(v) for k, v in data.items()}
    except ValueError:
        return {k: v for k, v in dotenv_values(path).items() if v is not None}


def _get(source: dict[str, str], key: str) -> str | None:
    return os.environ.get(key, source.get(key))


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in _TRUTHY


def get_config(env_path: Path | None = None) -> Config:
    global _cache
    if _cache is not None:
        return _cache
    source = _read_env_file(env_path or _DEFAULT_ENV_PATH)
    url = _get(source, "OPENCTI_URL")
    token = _get(source, "OPENCTI_TOKEN")
    if not url or not token:
        missing = [k for k, v in (("OPENCTI_URL", url), ("OPENCTI_TOKEN", token)) if not v]
        raise ConfigError(f"Missing required config: {', '.join(missing)}")
    _cache = Config(
        url=url.rstrip("/") + "/",
        token=token,
        read_only=_as_bool(_get(source, "OPENCTI_READ_ONLY"), True),
        timeout=int(_get(source, "OPENCTI_TIMEOUT") or 30),
        ssl_verify=_as_bool(_get(source, "OPENCTI_SSL_VERIFY"), True),
        log_level=(_get(source, "LOG_LEVEL") or "INFO").upper(),
        http_host=_get(source, "MCP_HTTP_HOST") or "127.0.0.1",
        http_port=int(_get(source, "MCP_HTTP_PORT") or 8765),
    )
    return _cache


def reset_config_cache() -> None:
    global _cache
    _cache = None
