# VS Code Setup for BuildingMOTIF MCP Server

## Prerequisites

1. VS Code installed
2. The BuildingMOTIF MCP server built and tested in this workspace

## Configuration

### Workspace Configuration (Recommended)

Create `.vscode/mcp.json` in your project root:

```json
{
  "servers": {
    "buildingmotif": {
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["-m", "buildingmotif_mcp.main"],
      "env": {}
    }
  }
}
```

This configuration uses `${workspaceFolder}` to reference your Python virtual environment, making it portable across different machines.

**With custom ontologies:**

```json
{
  "servers": {
    "buildingmotif": {
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["-m", "buildingmotif_mcp.main"],
      "env": {
        "BUILDINGMOTIF_ONTOLOGY_PATHS": "/path/to/custom/ontologies"
      }
    }
  }
}
```

### Alternative: Global Configuration

Create or edit `~/.vscode/mcp.json` (replace `/path/to/buildingmotif-mcp` with your actual clone path):

```json
{
  "servers": {
    "buildingmotif": {
      "command": "/path/to/buildingmotif-mcp/.venv/bin/python",
      "args": ["-m", "buildingmotif_mcp.main"],
      "env": {}
    }
  }
}
```

## Using the Server in VS Code

Once configured, the BuildingMOTIF MCP server will be available to:

### GitHub Copilot Chat

1. Open Copilot Chat (Cmd+Shift+I or Ctrl+Shift+I)
2. Use the server tools in your prompts:

```
@workspace Can you use the BuildingMOTIF MCP server to:
1. List available libraries and summarize their descriptions
2. List available templates in the 'brick' library
3. Get details about the AHU template
4. Show me what parameters I need to create an air handler unit
```

### Example Workflows

**Discover Libraries:**
```
Use the list_libraries tool to see what ontology libraries are available and their descriptions
```

**Discover Templates:**
```
Use the list_templates tool with library_name="brick" to see what 
building equipment templates are available. If you omit library_name, 
you'll get templates from all libraries.
```

**Get Template Details:**
```
Use get_template_details with library_name="brick" and 
template_name="https://brickschema.org/schema/Brick#AHU" to understand 
what parameters are needed for an air handling unit
```

**Build a Model:**
```
I have a CSV file with equipment names. Help me use BuildingMOTIF to:
1. Identify which templates match my equipment
2. Extract the parameters needed
3. Build a Brick model from the data
```

## Verifying the Setup

### 1. Check Server Status

Open a terminal in VS Code and run:

```bash
# From the project root directory
.venv/bin/python test_server.py
```

You should see:
```
✓ Server created successfully
✓ Libraries loaded: ['brick']
✓ Testing list_templates tool:
  - Library 'brick' has 838 templates
✓ All tests passed!
```

### 2. Test MCP Connection

In VS Code, open the Command Palette (Cmd+Shift+P / Ctrl+Shift+P) and search for:
- "MCP: Show MCP Servers" - should list `buildingmotif`
- "MCP: Restart MCP Server" - to restart if needed

## Troubleshooting

### Server Not Appearing

1. **Check the Python path is correct:**
   ```bash
   # From the project root directory
   ls -l .venv/bin/python
   ```

2. **Verify the module can be imported:**
   ```bash
   # From the project root directory
   .venv/bin/python -c "import buildingmotif_mcp; print('OK')"
   ```

3. **Check VS Code logs:**
   - Open Output panel (Cmd+Shift+U / Ctrl+Shift+U)
   - Select "MCP" from the dropdown
   - Look for buildingmotif server startup messages

### Server Crashes

Check the logs:
```bash
# Run with debug logging from the project root
LOG_LEVEL=DEBUG .venv/bin/buildingmotif-mcp
```

### Missing Libraries

If no templates appear, verify ontology files exist:
```bash
# From the project root directory
ls -l ontologies/brick/
```

Should show `Brick-subset.ttl` or similar files.

## Advanced Configuration

### Custom Logging

Add logging configuration to your settings:

```json
{
  "servers": {
    "buildingmotif": {
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["-m", "buildingmotif_mcp.main"],
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Multiple Ontology Sources

Load ontologies from multiple directories:

```json
{
  "servers": {
    "buildingmotif": {
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["-m", "buildingmotif_mcp.main"],
      "env": {
        "BUILDINGMOTIF_ONTOLOGY_PATHS": "/path/to/buildingmotif-mcp/ontologies:/path/to/my-org/custom-shapes"
      }
    }
  }
}
```

## Example: Building a Brick Model in VS Code

1. **Open your building data files** (CSV, PDF, etc.)

2. **In Copilot Chat:**
   ```
   I have equipment data in equipment.csv. Use the BuildingMOTIF MCP 
   server to help me:
   
   1. List available equipment templates
   2. Match my equipment to Brick templates
   3. Create a Brick model with proper relationships
   ```

3. **Copilot will use the MCP tools:**
   - `list_templates("brick")` to discover templates
   - `get_template_details("brick", "...")` for each relevant template
   - Guide you through creating a proper Brick model

4. **Iterate and validate:**
   - Add more equipment incrementally
   - Use organizational SHACL shapes to validate
   - Export the final model

## Next Steps

- See [README.md](README.md) for full documentation
- See [USAGE.md](USAGE.md) for tool reference
- Check [examples/sample-org/shapes.ttl](examples/sample-org/shapes.ttl) for custom SHACL examples
