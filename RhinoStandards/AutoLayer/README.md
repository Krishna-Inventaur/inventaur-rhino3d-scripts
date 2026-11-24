# Rhino AutoLayer startup entrypoint

This file is the Rhino startup bootstrap for the Inventaur standards runtime and RhinoAI MCP.

## Version-specific startup

- Rhino 9: load the standards installer, then invoke _MCPStart _Enter. RhinoAI chooses an available listener and registers it against the active Rhino document.
- Rhino 8: skip the Rhino 9-targeted standards installer and retain the separate MCP-only _MCPStart 10508 path.

## Startup safety

AutoLayer does not scan ports, open sockets or send JSON-RPC tools/list probes during Rhino startup. RhinoAI owns port allocation, collision handling and document-scoped listener registration. This avoids a second allocator and prevents a non-responsive listener from blocking Rhino's UI thread.

The actual port is determined by RhinoAI. Run MCPStatus in Rhino and use the reported endpoint when configuring or verifying an AI client. Do not assume that the Rhino 9 instance always uses 10500.

## Runtime paths

The entrypoint resolves the user's Documents directory and loads the Inventaur standards installer from:

    Documents/Inventaur/Rhino Standards/Inventaur_RhinoStandards_Install.py

The bootstrap log is written below:

    LOCALAPPDATA/Inventaur/RhinoStandards/logs/

## Client connection

RhinoAI is client-neutral. Run MCPConnect in Rhino to open the built-in client configuration dialog. Use its Install tab for detected MCP clients or its Prompt/mcp.json tabs for manual setup. The same RhinoAI server is used by all clients.

The RhinoAI source patch, RHP/router build and guarded installer are maintained as editable files in the sibling tools/RhinoAI_MCP/ tree.
