"""Core MCP server implementation for BuildingMOTIF."""

import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from buildingmotif_mcp.ontology import OntologyManager
from buildingmotif_mcp.tools import BuildingMOTIFTools

logger = logging.getLogger(__name__)


class BuildingMOTIFServer:
    """MCP server for BuildingMOTIF operations."""

    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("buildingmotif-mcp")
        self.ontology_manager = OntologyManager()
        self.tools = BuildingMOTIFTools(self.ontology_manager)

        # Register MCP handlers
        self._register_tools()

    def _register_tools(self) -> None:
        """Register all available MCP tools."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="list_libraries",
                    description="List all available BuildingMOTIF libraries that have been loaded",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="list_templates",
                    description="List all available templates. Optionally specify a library to filter results, or omit to get all templates from all libraries.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "library_name": {
                                "type": "string",
                                "description": "(Optional) Name of the library to query (e.g., 'brick', 'ashrae-223'). If not provided, returns all templates from all libraries.",
                            }
                        },
                    },
                ),
                Tool(
                    name="get_template_details",
                    description="Get detailed information about a specific template including its parameters and structure",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "library_name": {
                                "type": "string",
                                "description": "Name of the library",
                            },
                            "template_name": {
                                "type": "string",
                                "description": "Name or URI of the template",
                            },
                        },
                        "required": ["library_name", "template_name"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls."""
            logger.info(f"Tool called: {name} with arguments: {arguments}")

            try:
                if name == "list_libraries":
                    result = self.tools.list_libraries()
                elif name == "list_templates":
                    result = self.tools.list_templates(arguments.get("library_name"))
                elif name == "get_template_details":
                    result = self.tools.get_template_details(
                        arguments["library_name"],
                        arguments["template_name"],
                    )
                else:
                    result = {"error": f"Unknown tool: {name}"}

                return [TextContent(type="text", text=self._format_result(result))]

            except Exception as e:
                logger.exception(f"Error calling tool {name}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    def _format_result(self, result: dict) -> str:
        """Format result for MCP response."""
        import json

        return json.dumps(result, indent=2)

    async def run(self) -> None:
        """Run the MCP server."""
        async with stdio_server(self.server, sys.stdin.buffer, sys.stdout.buffer) as (read_stream, write_stream):
            logger.info("BuildingMOTIF MCP server started")
            await self.server.run(read_stream, write_stream, None)
