# BuildingMOTIF MCP Server

An [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server for [BuildingMOTIF](https://github.com/NREL/BuildingMOTIF) that enables AI coding assistants and agents to intelligently import and refine Brick models from unstructured building data.

## Overview

This MCP server integrates BuildingMOTIF capabilities into your AI coding environment, allowing you to:

- **Discover available templates** from Brick, custom ontologies, and SHACL-based libraries
- **Understand point requirements** for each template to guide data collection
- **Iteratively build Brick models** by evaluating templates with your building data
- **Apply custom validation rules** using SHACL shapes to enforce organizational standards
- **Integrate with document analysis** to extract equipment and point information from PDFs, CSVs, spreadsheets, and other sources

Whether you're working with legacy building data, creating new Brick models, or refining existing ones, this server helps you systematically transform unstructured data into semantic building models.

## Installation

This package is not yet published to PyPI. Install directly from GitHub using `uv`:

```bash
uv pip install git+https://github.com/epaulson/buildingmotif-mcp.git
```

Or clone and install locally:

```bash
git clone https://github.com/epaulson/buildingmotif-mcp.git
cd buildingmotif-mcp
uv pip install -e .
```

## Quick Start

### 1. Basic Usage in VS Code or Claude

Configure your MCP server in your tool's settings to include the BuildingMOTIF server. The server provides tools for:

- **List available templates** - See what templates are available for model building
- **Explore template details** - Understand parameters and requirements for a specific template
- **Evaluate templates** - Generate RDF graphs from templates by providing parameter bindings
- **Validate models** - Check models against Brick and custom SHACL shapes
- **Query ontologies** - Search for classes, properties, and patterns in loaded ontologies

### 2. Configuration

The server loads ontologies and templates from the bundled `ontologies/` directory by default, which includes:

- **Brick** - The Brick ontology with standard building templates
- **ASHRAE 223** - The emerging ASHRAE 223 standard for semantic building modeling. Brick and 223 work together. 
- Additional domain-specific ontologies

#### Using Custom Ontologies

To add custom ontologies or SHACL rules to your configuration, create or modify the MCP configuration:

```json
{
  "mcpServers": {
    "buildingmotif": {
      "command": "uv",
      "args": ["run", "buildingmotif-mcp"],
      "env": {
        "BUILDINGMOTIF_ONTOLOGY_PATHS": "/path/to/custom/ontologies:/path/to/local/org/ontologies"
      }
    }
  }
}
```

## Example: Using Local Organization Standards

Many organizations have specific requirements for their Brick models. This example shows how to define and use organizational standards.

### Create a Local Organization Ontology

Create a file `my-org/shapes.ttl` that defines your organizational requirements:

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix myorg: <urn:myorg/> .

# Shape: Every floor must have at least one temperature sensor
myorg:FloorTemperatureSensorShape
  a sh:NodeShape ;
  sh:targetClass brick:Floor ;
  sh:property [
    sh:path brick:hasPoint ;
    sh:qualifiedValueShape [
      sh:class brick:Temperature_Sensor ;
    ] ;
    sh:qualifiedMinCount 1 ;
    sh:message "Every floor must have at least one temperature sensor" ;
  ] .

# Shape: Equipment labels must follow naming convention
myorg:EquipmentNameShape
  a sh:NodeShape ;
  sh:targetClass brick:Equipment ;
  sh:property [
    sh:path rdfs:label ;
    sh:pattern "^[A-Z]{2,4}[0-9]{1,3}(-[A-Z0-9]+)?$" ;
    sh:message "Equipment labels must follow pattern: XX-000 or XXXX-000" ;
  ] .
```

### Configure the Server to Use Your Shapes

Update your MCP configuration to include your local organization ontologies:

```json
{
  "mcpServers": {
    "buildingmotif": {
      "command": "uv",
      "args": ["run", "buildingmotif-mcp"],
      "env": {
        "BUILDINGMOTIF_ONTOLOGY_PATHS": "./my-org"
      }
    }
  }
}
```

### Use in Your Workflow

With the server configured, you can:

1. **Ask Claude/AI to analyze your building data:**
   ```
   I have a CSV with equipment names and a PDF with floor layouts. 
   Using the MCP server, help me understand what templates are available 
   and what building structure I need to create.
   ```

2. **Explore templates and requirements:**
   The server lists templates from Brick (e.g., `Air_Handler_Unit`, `Zone_Air_Temperature_Sensor`) 
   and your custom shapes (e.g., the floor temperature requirement).

3. **Guide model building:**
   ```
   For each floor in my building, I need to create a Brick model. 
   What does the AHU template need? What other points should I define?
   Use the MCP server to help me structure this correctly and validate 
   against our org standards.
   ```

4. **Validate incrementally:**
   As you build your model, the server validates against both Brick standards 
   and your organizational SHACL shapes, catching issues early.

## Project Structure

```
buildingmotif-mcp/
├── README.md
├── pyproject.toml
├── buildingmotif_mcp/
│   ├── __init__.py
│   ├── main.py              # MCP server entry point
│   ├── server.py            # Core server implementation
│   ├── tools.py             # MCP tools/handlers
│   └── ontology.py          # Ontology management
├── ontologies/
│   ├── brick/               # Brick ontology
│   ├── ashrae-223/             # ashrae 223 ontology
│   └── ...
└── examples/
    └── sample-org/
        └── shapes.ttl       # Example organizational shapes
```

## MCP Tools

The server currently exposes the following tools to your AI assistant:

### Library and Template Discovery
- `list_libraries()` - List available libraries with metadata (description, type, tags)
- `list_templates(library_name?)` - List templates in a library, or omit `library_name` to return all templates across libraries
- `get_template_details(library_name, template_name)` - Get parameters and structure for a template

### Planned (Coming Soon)
- `search_templates(keyword)` - Find templates matching a query
- `evaluate_template(template_name, parameters)` - Generate RDF graph from template bindings
- `get_template_parameters(template_name)` - Get required and optional parameters
- `list_ontologies()` - See loaded ontologies and their sources
- `get_shape_requirements(shape_name)` - Understand what a SHACL shape requires
- `find_class_by_keyword(keyword)` - Search for ontology classes

### Model Validation
- `validate_model(rdf_content)` - Check model against loaded ontologies and SHACL shapes
- `get_validation_report(model_uri)` - Get detailed validation results

### Workflow Helpers
- `suggest_equipment_templates(equipment_type)` - Get recommended templates for equipment
- `get_point_requirements(template_name)` - List all points typically needed for a template

## Typical Workflow

Here's how you might use this server in an AI-assisted building modeling workflow:

```python
# 1. AI reads your building data (PDF, CSV, spreadsheet)
# 2. AI asks the MCP server: "What templates are available for an AHU?"
#    → Server returns AHU template with parameters: {name}

# 3. AI extracts AHU information from your data
# 4. AI asks the MCP server: "What points does an AHU template need?"
#    → Server lists: Supply Fan, Cooling Coil, Dampers, Points, etc.

# 5. AI maps your data to template requirements
# 6. AI uses the server to evaluate templates:
#    → evaluate_template("AHU", {"name": "bldg:Core_ZN_AHU_1"})
#    → Returns RDF graph with AHU structure

# 7. AI builds up model incrementally
# 8. AI validates: "Does my model match our org standards?"
#    → Server checks against custom SHACL shapes
#    → Returns any validation errors or warnings

# 9. Iterate: Refine data extraction, add more equipment/points
# 10. Export: Get final Brick RDF model for downstream use
```

## Development

This is an active development project. Future enhancements may include:

- **Ingress connectors** for common data sources (BACnet, Haystack, etc.)
- **Incremental model building** - Support partial template evaluation
- **Shape generation** - Auto-generate SHACL shapes from patterns
- **Model comparison** - Identify differences between model versions
- **Export utilities** - Output to Haystack, JSON-LD, etc.

## Contributing

Contributions welcome! The project is organized to make it easy to add new tools and capabilities.

## License

See LICENSE file for details.

## Resources

- [BuildingMOTIF Documentation](https://buildingmotif.readthedocs.io/)
- [Brick Ontology](https://brickschema.org/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [SHACL Specification](https://www.w3.org/TR/shacl/)

## Library Metadata Files

You can add metadata for any ontology file by creating a JSON file with the same name plus `.metadata`.

**Example:**
```
ontologies/brick/Brick-subset.ttl
ontologies/brick/Brick-subset.ttl.metadata
```

**Format:**
```json
{
  "name": "Brick Schema",
  "description": "Brick is a uniform metadata schema for buildings...",
  "type": "builtin",
  "version": "1.3",
  "url": "https://brickschema.org/",
  "tags": ["hvac", "buildings", "iot", "metadata"]
}
```

**Notes:**
- `type` should be `builtin` for bundled libraries and `custom` for site-specific libraries.
- Any additional fields are preserved and returned in `list_libraries`.
