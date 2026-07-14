from __future__ import annotations

from typing import Annotated, Any, Callable

from fastmcp import FastMCP
from pydantic import Field

from ..client import is_mutation_document, run_raw_query


def _make_query_callable(*, read_only: bool) -> Callable:
    async def _graphql_query(
        query: str,
        variables: dict[str, Any] | None = None,
    ) -> Any:
        if read_only and is_mutation_document(query):
            raise ValueError(
                "Server is in read-only mode; GraphQL mutations are rejected. "
                "Set OPENCTI_READ_ONLY=false to enable writes."
            )
        return run_raw_query(query, variables)

    return _graphql_query


def register(mcp: FastMCP, *, read_only: bool) -> None:
    impl = _make_query_callable(read_only=read_only)

    @mcp.tool(
        name="graphql_query",
        description=(
            "Run a raw GraphQL query against the OpenCTI API. Use for operations not "
            "covered by the typed domain tools. Mutations are rejected in read-only mode."
        ),
    )
    async def graphql_query(
        query: Annotated[str, Field(description="A GraphQL query document")],
        variables: Annotated[
            dict[str, Any] | None, Field(description="Optional variables object")
        ] = None,
    ) -> Any:
        return await impl(query, variables)
