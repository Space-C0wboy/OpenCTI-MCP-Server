from __future__ import annotations

import argparse
import logging
import sys

from fastmcp import FastMCP

from .config import get_config
from .errors import ConfigError
from .tools import register_all

INSTRUCTIONS = (
    "MCP server for the OpenCTI threat-intelligence platform. Provides typed tools to "
    "query, search, and (when not read-only) create/update/delete STIX domain objects, "
    "observables, relationships, labels, and cases, plus a raw graphql_query escape-hatch."
)


def build_server() -> FastMCP:
    cfg = get_config()
    logging.basicConfig(level=getattr(logging, cfg.log_level, logging.INFO))
    mcp = FastMCP(name="opencti-mcp", instructions=INSTRUCTIONS)
    register_all(mcp, read_only=cfg.read_only)
    return mcp


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="opencti-mcp")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args(argv)

    try:
        mcp = build_server()
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        raise SystemExit(2)

    cfg = get_config()
    if args.transport == "http":
        mcp.run(
            transport="http",
            host=args.host or cfg.http_host,
            port=args.port or cfg.http_port,
        )
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
