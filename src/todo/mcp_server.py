"""MCP server for Todo application.

Usage:
    # stdio mode (for Claude Desktop, etc.)
    uv run python -m todo.mcp_server

    # HTTP mode
    uv run python -m todo.mcp_server --http
"""

from todo.database import init_db
from todo.models import BaseEntity


def main() -> None:
    import asyncio
    import sys

    from sqlmodel_graphql.mcp import create_mcp_server

    # Initialize database before starting MCP server
    asyncio.run(init_db())

    mcp = create_mcp_server(
        apps=[{"name": "todo", "base": BaseEntity}],
        name="Todo GraphQL MCP Server",
    )

    if "--http" in sys.argv:
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
