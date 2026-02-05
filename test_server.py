#!/usr/bin/env python3
"""Simple test script for the BuildingMOTIF MCP server."""

import sys
import logging

logging.basicConfig(level=logging.INFO)

from buildingmotif_mcp.server import BuildingMOTIFServer

def test_server():
    """Test server initialization and basic functionality."""
    print("Testing BuildingMOTIF MCP Server...")
    
    try:
        # Create server
        server = BuildingMOTIFServer()
        print("✓ Server created successfully")
        
        # Test list_libraries tool
        print("\n✓ Testing list_libraries tool:")
        lib_result = server.tools.list_libraries()
        if lib_result["success"]:
            print(f"  - Found {lib_result['count']} libraries")
            for lib_info in lib_result['libraries']:
                lib_type = lib_info['metadata'].get('type', 'unknown')
                lib_desc = lib_info['metadata'].get('description', 'No description')
                print(f"    • {lib_info['name']} ({lib_type}): {lib_desc[:80]}...")
                print(f"      Templates: {lib_info['template_count']}")
            libraries = [lib['name'] for lib in lib_result['libraries']]
        else:
            print(f"  - Error: {lib_result.get('error')}")
            libraries = []
        
        # Test list_templates tool without library (all templates)
        print("\n✓ Testing list_templates tool (all libraries):")
        all_result = server.tools.list_templates()
        if all_result["success"]:
            print(f"  - Total templates across all libraries: {all_result['count']}")
            for lib_name, templates in all_result.get('templates_by_library', {}).items():
                print(f"    • {lib_name}: {len(templates)} templates")
        else:
            print(f"  - Error: {all_result.get('error')}")
        
        # Test list_templates tool with specific library
        print("\n✓ Testing list_templates tool:")
        for lib_name in libraries:
            result = server.tools.list_templates(lib_name)
            if result["success"]:
                print(f"  - Library '{lib_name}' has {result['count']} templates")
                if result.get('templates', [])[:3]:
                    print(f"    Sample: {result['templates'][:3]}")
            else:
                print(f"  - Error: {result.get('error')}")
        
        # Test get_template_details
        if libraries:
            lib_name = libraries[0]
            templates = server.ontology_manager.list_templates(lib_name)
            if templates:
                template_name = templates[0]
                print(f"\n✓ Testing get_template_details for '{template_name[:60]}...':")
                result = server.tools.get_template_details(lib_name, template_name)
                if result["success"]:
                    print(f"  - Parameters: {result['parameters']}")
                    body_preview = result['body'][:150].replace('\n', ' ')
                    print(f"  - Body preview: {body_preview}...")
                else:
                    print(f"  - Error: {result.get('error')}")

        # Test parsing example shapes.ttl
        print("\n✓ Testing example shapes.ttl parsing:")
        from pathlib import Path
        import rdflib
        from buildingmotif.dataclasses import Library

        shapes_path = Path("examples/sample-org/shapes.ttl")
        if shapes_path.exists():
            try:
                graph = rdflib.Graph()
                graph.parse(str(shapes_path), format="turtle")
                print(f"  - Parsed shapes.ttl successfully ({len(graph)} triples)")

                # Also try loading as a BuildingMOTIF library
                lib = Library.load(ontology_graph=str(shapes_path))
                print(f"  - Loaded as library with {len(lib.get_templates())} templates")
            except Exception as e:
                print(f"  - Error parsing/loading shapes.ttl: {e}")
                return 1
        else:
            print("  - Error: examples/sample-org/shapes.ttl not found")
            return 1
        
        print("\n✓ All tests passed!")
        return 0
        
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(test_server())
