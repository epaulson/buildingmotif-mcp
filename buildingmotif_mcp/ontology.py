"""Ontology and library management for BuildingMOTIF MCP."""

import os
from pathlib import Path
from typing import Dict, List, Optional
import logging
import json

from buildingmotif import BuildingMOTIF
from buildingmotif.dataclasses import Library

logger = logging.getLogger(__name__)


class OntologyManager:
    """Manages loading and accessing BuildingMOTIF libraries and ontologies."""

    def __init__(self, db_url: str = "sqlite://", ontology_paths: Optional[List[str]] = None):
        """Initialize the ontology manager.

        Args:
            db_url: BuildingMOTIF database URL (default: in-memory SQLite)
            ontology_paths: List of paths to ontology directories/files to load
        """
        self.bm = BuildingMOTIF(db_url)
        self.libraries: Dict[str, Library] = {}
        self.library_metadata: Dict[str, dict] = {}
        self.ontology_paths = ontology_paths or []

        # Always add bundled ontologies - handle both dev and installed scenarios
        bundled_ontologies = Path(__file__).parent.parent / "ontologies"
        if bundled_ontologies.exists():
            logger.info(f"Found bundled ontologies at: {bundled_ontologies}")
            self.ontology_paths.insert(0, str(bundled_ontologies))
        else:
            # Try to find ontologies from installed package location
            try:
                import importlib.resources as pkg_resources
                # For Python 3.9+
                ontologies_path = Path(str(pkg_resources.files('buildingmotif_mcp'))) / "ontologies"
                if ontologies_path.exists():
                    logger.info(f"Found installed ontologies at: {ontologies_path}")
                    self.ontology_paths.insert(0, str(ontologies_path))
            except (ImportError, AttributeError, TypeError):
                logger.warning("Could not find bundled ontologies in installed package")

        logger.info(f"Ontology search paths: {self.ontology_paths}")
        self._load_ontologies()

    def _load_ontologies(self) -> None:
        """Load all ontologies from configured paths."""
        for path_str in self.ontology_paths:
            path = Path(path_str)
            if not path.exists():
                logger.warning(f"Ontology path does not exist: {path}")
                continue

            if path.is_dir():
                # Check if this directory contains TTL files directly
                ttl_files = list(path.glob("*.ttl")) + list(path.glob("*.rdf")) + list(path.glob("*.owl"))
                if ttl_files:
                    # Directory contains ontology files
                    self._load_from_directory(path)
                else:
                    # Check subdirectories
                    for subdir in path.iterdir():
                        if subdir.is_dir():
                            sub_ttl_files = list(subdir.glob("*.ttl")) + list(subdir.glob("*.rdf")) + list(subdir.glob("*.owl"))
                            if sub_ttl_files:
                                self._load_from_directory(subdir)
            elif path.suffix.lower() in {".ttl", ".rdf", ".owl"}:
                self._load_file(path)

    def _load_from_directory(self, directory: Path) -> None:
        """Load all ontology files from a directory.

        Args:
            directory: Directory path containing ontology files
        """
        library_name = directory.name
        logger.info(f"Loading ontologies from directory: {directory} (name: {library_name})")

        # Find ontology files
        ontology_files = list(directory.glob("*.ttl")) + list(directory.glob("*.rdf")) + list(directory.glob("*.owl"))
        
        if not ontology_files:
            logger.warning(f"No ontology files found in {directory}")
            return

        try:
            # If there's only one file, load it directly; otherwise load the whole directory
            if len(ontology_files) == 1:
                lib = Library.load(ontology_graph=str(ontology_files[0]))
                file_for_metadata = ontology_files[0]
            else:
                lib = Library.load(ontology_graph=str(directory))
                file_for_metadata = ontology_files[0]
            
            self.libraries[library_name] = lib
            
            # Load metadata if available
            metadata = self._load_metadata(file_for_metadata)
            self.library_metadata[library_name] = metadata
            
            logger.info(f"Loaded library '{library_name}' with {len(lib.get_templates())} templates")
        except Exception as e:
            logger.error(f"Error loading library from {directory}: {e}")

    def _load_file(self, file_path: Path) -> None:
        """Load a single ontology file.

        Args:
            file_path: Path to ontology file
        """
        library_name = file_path.stem
        logger.info(f"Loading ontology file: {file_path}")

        try:
            lib = Library.load(ontology_graph=str(file_path))
            
            # Load metadata if available
            metadata = self._load_metadata(file_path)
            self.library_metadata[library_name] = metadata
            
            self.libraries[library_name] = lib
            logger.info(f"Loaded library '{library_name}' with {len(lib.get_templates())} templates")
        except Exception as e:
            logger.error(f"Error loading ontology from {file_path}: {e}")

    def _load_metadata(self, ontology_file: Path) -> dict:
        """Load metadata for an ontology file.

        Args:
            ontology_file: Path to the ontology file

        Returns:
            Dictionary with metadata, or default metadata if file not found
        """
        metadata_file = Path(str(ontology_file) + ".metadata")
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    logger.info(f"Loaded metadata from {metadata_file}")
                    return metadata
            except Exception as e:
                logger.warning(f"Error loading metadata from {metadata_file}: {e}")
        
        # Return default metadata
        return {
            "name": ontology_file.stem,
            "description": "No description available",
            "type": "unknown"
        }

    def get_library(self, library_name: str) -> Optional[Library]:
        """Get a loaded library by name.

        Args:
            library_name: Name of the library

        Returns:
            The Library object or None if not found
        """
        return self.libraries.get(library_name)

    def list_libraries(self) -> List[str]:
        """List all loaded library names.
        
        Returns:
            List of library names
        """
        return list(self.libraries.keys())

    def get_library_info(self, library_name: str) -> Optional[dict]:
        """Get detailed information about a library including metadata.

        Args:
            library_name: Name of the library

        Returns:
            Dictionary with library info or None if not found
        """
        lib = self.get_library(library_name)
        if not lib:
            return None
        
        metadata = self.library_metadata.get(library_name, {})
        
        return {
            "name": library_name,
            "template_count": len(lib.get_templates()),
            "metadata": metadata
        }

    def get_all_libraries_info(self) -> List[dict]:
        """Get information about all loaded libraries.

        Returns:
            List of dictionaries with library info and metadata
        """
        result = []
        for lib_name in self.list_libraries():
            info = self.get_library_info(lib_name)
            if info:
                result.append(info)
        return result
    def list_templates(self, library_name: str) -> List[str]:
        """List all template names in a library.

        Args:
            library_name: Name of the library

        Returns:
            List of template names (URIs as strings)
        """
        lib = self.get_library(library_name)
        if not lib:
            return []

        templates = lib.get_templates()
        return [str(template.name) for template in templates]

    def get_template_by_name(self, library_name: str, template_name: str):
        """Get a specific template from a library.

        Args:
            library_name: Name of the library
            template_name: Name of the template

        Returns:
            The Template object or None if not found
        """
        lib = self.get_library(library_name)
        if not lib:
            return None

        try:
            return lib.get_template_by_name(template_name)
        except Exception as e:
            logger.error(f"Error getting template '{template_name}' from library '{library_name}': {e}")
            return None
