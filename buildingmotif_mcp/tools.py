"""MCP tools for BuildingMOTIF operations."""

import logging
from typing import List
from buildingmotif_mcp.ontology import OntologyManager

logger = logging.getLogger(__name__)


class BuildingMOTIFTools:
    """MCP tools for BuildingMOTIF operations."""

    def __init__(self, ontology_manager: OntologyManager):
        """Initialize tools with an ontology manager.

        Args:
            ontology_manager: OntologyManager instance
        """
        self.om = ontology_manager

    def list_libraries(self) -> dict:
        """List all available libraries with metadata.

        Returns:
            dict with detailed library information including metadata
        """
        libraries_info = self.om.get_all_libraries_info()

        return {
            "success": True,
            "count": len(libraries_info),
            "libraries": libraries_info,
        }

    def list_templates(self, library_name: str = None) -> dict:
        """List all available templates in a library, or all templates if no library specified.

        Args:
            library_name: Name of the library to query (optional - if not provided, returns all templates)

        Returns:
            dict with templates list and metadata
        """
        # If no library specified, return all templates from all libraries
        if library_name is None:
            all_templates = {}
            for lib_name in self.om.list_libraries():
                templates = self.om.list_templates(lib_name)
                all_templates[lib_name] = templates

            total_count = sum(len(templates) for templates in all_templates.values())

            return {
                "success": True,
                "library": "all",
                "count": total_count,
                "templates_by_library": all_templates,
            }

        # Return templates from specific library
        available_libraries = self.om.list_libraries()

        if library_name not in available_libraries:
            return {
                "success": False,
                "error": f"Library '{library_name}' not found. Available libraries: {available_libraries}",
                "templates": [],
            }

        templates = self.om.list_templates(library_name)

        return {
            "success": True,
            "library": library_name,
            "count": len(templates),
            "templates": templates,
        }

    def get_template_details(self, library_name: str, template_name: str) -> dict:
        """Get detailed information about a specific template.

        Args:
            library_name: Name of the library
            template_name: Name/URI of the template

        Returns:
            dict with template details including parameters and structure
        """
        available_libraries = self.om.list_libraries()

        if library_name not in available_libraries:
            return {
                "success": False,
                "error": f"Library '{library_name}' not found. Available libraries: {available_libraries}",
            }

        template = self.om.get_template_by_name(library_name, template_name)

        if not template:
            available_templates = self.om.list_templates(library_name)
            return {
                "success": False,
                "error": f"Template '{template_name}' not found in library '{library_name}'.",
                "hint": f"Available templates: {available_templates[:5]}..." if len(available_templates) > 5 else f"Available templates: {available_templates}",
            }

        try:
            parameters = list(template.parameters) if hasattr(template, "parameters") else []
            body_ttl = template.body.serialize(format="turtle") if hasattr(template, "body") else ""

            return {
                "success": True,
                "library": library_name,
                "template": str(template.name),
                "parameters": parameters,
                "description": template.description if hasattr(template, "description") else "",
                "body": body_ttl,
            }
        except Exception as e:
            logger.error(f"Error getting template details: {e}")
            return {
                "success": False,
                "error": f"Error retrieving template details: {str(e)}",
            }
