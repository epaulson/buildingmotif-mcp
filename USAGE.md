# BuildingMOTIF MCP Server - Usage Examples

## Running the Server

Once installed, you can run the server:

```bash
# Using the installed command
buildingmotif-mcp

# Or using the virtual environment directly
/path/to/.venv/bin/python -m buildingmotif_mcp.main
```

## Testing the Server

Run the test script to verify the installation:

```bash
python test_server.py
```

## Using with Claude Desktop

Add the server to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "buildingmotif": {
      "command": "/path/to/buildingmotif-mcp/.venv/bin/python",
      "args": ["-m", "buildingmotif_mcp.main"],
      "env": {}
    }
  }
}
```

### Adding Custom Ontologies

To use custom organizational ontologies:

```json
{
  "mcpServers": {
    "buildingmotif": {
      "command": "/path/to/buildingmotif-mcp/.venv/bin/python",
      "args": ["-m", "buildingmotif_mcp.main"],
      "env": {
        "BUILDINGMOTIF_ONTOLOGY_PATHS": "/path/to/custom/ontologies:/path/to/another/ontology"
      }
    }
  }
}
```

## Library Metadata

You can add metadata for any ontology file by creating a JSON file with the same name plus `.metadata`.

**Example:**
```
ontologies/brick/Brick-subset.ttl
ontologies/brick/Brick-subset.ttl.metadata
```

**Sample metadata file:**
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

Use the `type` field to distinguish built-in libraries from site-specific/custom libraries (e.g., `builtin` vs `custom`).

## Available MCP Tools

### 1. list_libraries

List all available libraries that have been loaded, including metadata (description, type, tags).

**Input:**
```json
{}
```

**Output:**
```json
{
  "success": true,
  "count": 1,
  "libraries": [
    {
      "name": "brick",
      "template_count": 838,
      "metadata": {
        "name": "Brick Schema",
        "description": "Brick is a uniform metadata schema for buildings...",
        "type": "builtin",
        "version": "1.3",
        "url": "https://brickschema.org/",
        "tags": ["hvac", "buildings", "iot", "metadata"]
      }
    }
  ]
}
```

### 2. list_templates

List all templates in a library. If `library_name` is omitted, returns all templates from all libraries.

**Input:**
```json
{
  "library_name": "brick"
}
```

**Output:**
```json
{
  "success": true,
  "library": "brick",
  "count": 838,
  "templates": ["https://brickschema.org/schema/Brick#AHU", "..."]
}
```

**All libraries (omit `library_name`):**
```json
{}
```

**Output:**
```json
{
  "success": true,
  "library": "all",
  "count": 1234,
  "templates_by_library": {
    "brick": ["https://brickschema.org/schema/Brick#AHU", "..."],
    "custom": ["urn:myorg/Custom_Template", "..."]
  }
}
```

### 3. get_template_details

Get detailed information about a specific template.

**Input:**
```json
{
  "library_name": "brick",
  "template_name": "https://brickschema.org/schema/Brick#AHU"
}
```

**Output:**
```json
{
  "success": true,
  "library": "brick",
  "template": "https://brickschema.org/schema/Brick#AHU",
  "parameters": ["name"],
  "description": "",
  "body": "@prefix brick: <https://brickschema.org/schema/Brick#> .\n\n<urn:___param___#name> a brick:AHU ."
}
```

## Example Workflow

1. **Discover available libraries:**
   ```
   Use the list_libraries tool to see what ontology libraries are loaded
   ```

2. **Discover available templates:**
   ```
   Use the list_templates tool to see what templates are available in the 'brick' library
   ```

3. **Get template details:**
   ```
   Use get_template_details to understand what parameters the AHU template needs
   ```

4. **Extract building data:**
   ```
   Analyze your PDFs, CSVs, etc. to identify equipment and points
   ```

5. **Build model incrementally:**
   ```
   Use BuildingMOTIF to evaluate templates with your extracted data
   ```

6. **Validate:**
   ```
   Analyze your PDFs, CSVs, etc. to identify equipment and points
   ```

4. **Build model incrementally:**
   ```
   Use BuildingMOTIF to evaluate templates with your extracted data
   ```

5. **Validate:**
   ```
   Check the model against Brick and your organizational SHACL shapes
   ```
