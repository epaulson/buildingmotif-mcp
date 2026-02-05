"""Entry point for the BuildingMOTIF MCP server."""

import asyncio
import logging
import os
import sys
from pathlib import Path

from buildingmotif_mcp.server import BuildingMOTIFServer


def setup_logging() -> None:
    """Configure logging."""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )


def main() -> None:
    """Main entry point."""
    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("Starting BuildingMOTIF MCP server")

    # Parse custom ontology paths from environment variable
    ontology_paths = None
    env_paths = os.getenv("BUILDINGMOTIF_ONTOLOGY_PATHS", "")
    if env_paths:
        ontology_paths = [p.strip() for p in env_paths.split(":") if p.strip()]
        logger.info(f"Custom ontology paths from environment: {ontology_paths}")

    try:
        server = BuildingMOTIFServer(ontology_paths=ontology_paths)
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.exception(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
